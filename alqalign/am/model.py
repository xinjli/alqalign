from alqalign.config import read_config
from itertools import groupby
import editdistance
from collections import defaultdict
import torch.nn as nn
from alqalign.am.module.ssl_transformer import SSLTransformer
from sys import exit
import numpy as np
from alqalign.utils.tensor import tensor_to_cuda, move_to_tensor, move_to_ndarray

def read_am(config_or_name, overwrite_config=None):

    if isinstance(config_or_name, str):
        config = read_config('am/'+config_or_name, overwrite_config)
    else:
        config = config_or_name

    model = None

    if config.model == 'ssl_transformer':
        model =  SSLTransformer(config)
    else:
        model = None
        exit(1)

    if model is None:
        reporter.critical(f"am arch {config.model} not available from {list(arch_cls.type_ for arch_cls in arch_types)}")
        exit(1)

    am = AcousticModel(model, config)
    return am


class AcousticModel:

    def __init__(self, model, config):

        self.model = model
        self.config = config
        self.device_id = self.config.rank

    def cuda(self):
        self.model = self.model.cuda()
        return self


    def test_step(self, sample: dict):

        self.model.eval()

        # get batch and prepare it into pytorch format
        feat, feat_length = tensor_to_cuda(sample["feats"], self.device_id)

        meta = sample['meta']

        if 'format' in meta:
            format = meta['format']
        else:
            format = 'token'

        result = self.model(feat, feat_length, meta)

        output = result['output'].detach()
        output_length = result['output_length']

        emit = 1.0
        if 'emit' in sample:
            emit = sample['emit']

        timestamp = False
        if 'timestamp' in sample:
            timestamp = sample['timestamp']

        topk = 1
        if 'topk' in sample:
            topk = sample['topk']

        if format == 'logit':
            return output
        elif format == 'both':
            decoded_info = self.decode(output, output_length, topk, emit)
            return output, decoded_info

        else:
            decoded_info = self.decode(output, output_length, topk, emit)

            return decoded_info

    def reduce_report(self, reports):

        corpus_reports_dict = defaultdict(list)

        # group by corpus_id
        for report in reports:
            corpus_reports_dict[report['corpus_id']].append(report)

        corpus_report = dict()

        # do analysis per corpus
        for corpus_id, corpus_reports in corpus_reports_dict.items():
            corpus_dict = dict()
            corpus_dict['total_token_size'] = sum([report['total_token_size'] for report in corpus_reports])
            corpus_dict['total_ter'] = sum([report['total_ter'] for report in corpus_reports])
            corpus_dict['total_loss'] = sum([report['total_loss'] for report in corpus_reports])
            corpus_dict['aux_loss'] = sum([report['aux_loss'] for report in corpus_reports])
            corpus_dict['average_ter'] = corpus_dict['total_ter']*1.0 / corpus_dict['total_token_size']
            corpus_dict['average_loss'] = corpus_dict['total_loss']*1.0 / corpus_dict['total_token_size']

            corpus_report[corpus_id] = corpus_dict

        # do analysis totally
        total_report = dict()
        total_report['total_token_size'] = sum([report['total_token_size'] for report in reports])
        total_report['total_ter'] = sum([report['total_ter'] for report in reports])
        total_report['total_loss'] = sum([report['total_loss'] for report in reports])
        total_report['aux_loss'] = sum([report['aux_loss'] for report in reports])
        total_report['average_ter'] = total_report['total_ter']*1.0 / total_report['total_token_size']
        total_report['average_loss'] = total_report['total_loss']*1.0 / total_report['total_token_size']

        return total_report, corpus_report

    def eval_ter(self, output, output_length, sample):
        """
        compute SUM of ter in this batch

        :param batch_logits: (B,T,Token_size)
        :param batch_target:  (B, max_label)
        :param batch_target_len: [B]
        :return:
        """

        # print("shape is ", batch_logits.shape)

        error_cnt = 0.0
        total_cnt = 0.0

        logits = move_to_ndarray(output)
        logits_length = move_to_ndarray(output_length)

        targets, targets_length = sample["langs"]
        target_tokens = []
        decoded_tokens = []

        for i in range(len(targets_length)):
            target = targets[i, :targets_length[i]].tolist()
            logit  = logits[i][:logits_length[i]]

            raw_token = [x[0] for x in groupby(np.argmax(logit, axis=1))]
            decoded_token = list(filter(lambda a: a != 0, raw_token))

            target_tokens.append(target)
            decoded_tokens.append(decoded_token)
            #print('target ', target)
            #print('decoded_token ', decoded_token)

            error = editdistance.distance(target, decoded_token)

            error_cnt += error
            total_cnt += targets_length[i]

        return error_cnt, total_cnt, target_tokens, decoded_tokens

    def decode(self, output, output_length, topk=1, emit=1.0):

        logits = move_to_ndarray(output)
        logits_length = move_to_ndarray(output_length)

        assert len(logits) == len(logits_length)

        decoded_lst = []

        for ii in range(len(logits)):

            logit = logits[ii][:logits_length[ii]]

            emit_frame_idx = []

            cur_max_arg = -1

            # find all emitting frames
            for i in range(len(logit)):

                frame = logit[i]
                frame[0] /= emit

                arg_max = np.argmax(frame)

                # this is an emitting frame
                if arg_max != cur_max_arg and arg_max != 0:
                    emit_frame_idx.append(i)
                    cur_max_arg = arg_max

            # decode all emitting frames
            decoded_seq = []

            for i, idx in enumerate(emit_frame_idx):
                frame = logit[idx]

                if i == len(emit_frame_idx) - 1:
                    next_idx = len(logit)-1
                else:
                    next_idx = emit_frame_idx[i+1]

                exp_prob = np.exp(frame - np.max(frame))
                probs = exp_prob / exp_prob.sum()

                top_phones = frame.argsort()[-topk:][::-1]
                top_probs = sorted(probs)[-topk:][::-1]

                start_timestamp = self.config.window_shift * idx
                end_timestamp = self.config.window_shift * next_idx
                duration = min(1.0, end_timestamp - start_timestamp)

                info = {'start': self.config.window_shift * idx,
                        'duration': duration,
                        'phone_id': top_phones[0],
                        'prob': top_probs[0],
                        'alternative_ids': top_phones[:topk].tolist(),
                        'alternative_probs': top_probs[:topk]}

                decoded_seq.append(info)

            decoded_lst.append(decoded_seq)

            #raw_token = [x[0] for x in groupby(np.argmax(logit, axis=1))]
            #decoded_token = list(filter(lambda a: a != 0, raw_token))
            #decoded_tokens.append(decoded_token)

        return decoded_lst