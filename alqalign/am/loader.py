import numpy as np
from alqalign.am.dataset import read_audio_dataset
from torch.utils.data import DataLoader
import torch.nn.functional as F
from alqalign.utils.tensor import pad_list
import torch

def collate_feats(utt_dict_lst):

    utt_ids = [utt_dict['utt_id'] for utt_dict in utt_dict_lst]
    batch_dict = {'utt_ids': utt_ids}

    feat_lst = []
    feat_lens = []

    for i, utt_dict in enumerate(utt_dict_lst):
        feat = utt_dict['feats']

        # cut off at 15 second
        if len(feat) > 240000:
            feat = feat[:240000]

        feat_len = feat.shape[0]
        feat_lst.append(feat)
        feat_lens.append(feat_len)

    feats = pad_list(feat_lst, 0)
    feat_lens = torch.IntTensor(feat_lens)

    batch_dict['feats'] = (feats, feat_lens)

    # meta data for this batch
    batch_dict['meta'] = {}

    return batch_dict


def read_audio_loader(corpus_path, batch_size=16, segment_duration=15):

    dataset = read_audio_dataset(corpus_path, segment_duration=segment_duration)
    return DataLoader(dataset, batch_size=batch_size, collate_fn=collate_feats)
