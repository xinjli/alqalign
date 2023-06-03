from genericpath import exists
from pathlib import Path
from symbol import parameters
from alqalign.model import read_phoneme_inventory
import torchaudio
from alqalign.config import logger
import logging

from alqalign.ctc_segmentation.ctc_segmentation import (
    CtcSegmentationParameters,
    ctc_segmentation,
    determine_utterance_segments,
    prepare_text,
    prepare_token_list,
)

from phonepiece.inventory import read_inventory
import numpy as np
from alqalign.audio import read_audio, slice_audio, write_audio

def process_alignment(audio_file, text_file, lang_id, data_dir, utt_id=None, mode='sentence', threshold=-100.0, slice=False, format='kaldi', verbose=False):

    logit_file = data_dir / 'logit.npz'
    lpz = np.load(logit_file, allow_pickle=True)

    if utt_id is None:
        audio_name = Path(audio_file).stem
    else:
        audio_name = utt_id

    id_lst = []

    for line in open(data_dir / 'ids.txt', 'r'):
        ids = np.array(list(map(int, line.strip().split())))
        if len(ids) == 0:
            continue
        id_lst.append(ids)

    inventory = read_phoneme_inventory(lang_id)

    # CTC segmentation settings
    config = CtcSegmentationParameters()
    config.char_list = inventory.elems[:-1]
    config.index_duration = 0.02
    #config.blank_transition_cost_zero = True
    ground_truth_mat, utt_begin_indices = prepare_token_list(config, id_lst)

    #print(ground_truth_mat)

    if(len(ground_truth_mat) > lpz.shape[0]):
        print("audio is shorter than text")
        return

    timings, char_probs, state_list = ctc_segmentation(
        config, lpz, ground_truth_mat
    )

    text = []

    for line in open(data_dir / 'postprocess_text.txt', 'r'):
        line = line.strip()
        if len(line) == 0:
            continue
        text.append(line)

    #print(text)

    if len(id_lst) != len(text):
        print(f"text file ({data_dir / 'postprocess_text.txt'}) has {len(text)} lines but id file ({data_dir / 'ids.txt'}) has {len(id_lst)} lines")

    phoneme = []
    for line in open(data_dir / 'phonemes.txt', 'r'):
        line = line.strip()

        if len(line.split('|')[1].strip()) == 0:
            continue

        phoneme.append(line)

    assert len(text) == len(phoneme), f"text file ({data_dir / 'postprocess_text.txt'}) has {len(text)} lines but phoneme file ({data_dir / 'phonemes.txt'}) has {len(phoneme)} lines"

    logger.info(timings)
    logger.info(utt_begin_indices)

    segments = determine_utterance_segments(
        config, utt_begin_indices, char_probs, timings, text, mode='sentence', verbose=verbose
    )

    audio = read_audio(audio_file)

    w_log = open(data_dir / 'log.txt', 'w')

    w_ctm = None
    w_text = None
    w_segments = None
    w_score = None

    if format == 'kaldi':
        w_text = open(data_dir / 'text', 'w')
        w_segments = open(data_dir / 'segments', 'w')
        w_score = open(data_dir / 'score', 'w')
    else:
        w_ctm = open(data_dir / 'result.ctm', 'w')

    if slice:
        output_dir = Path(data_dir / 'audios')
        output_dir.mkdir(exist_ok=True, parents=True)

    all_count = len(segments)
    success_count = 0

    for i, seg in enumerate(segments):
        start = seg[0] + 0.01
        end = seg[1] + 0.01
        score = seg[2]

        # utterance id has the format "original-id - index - start_time - end_time"
        utt_id = f'{audio_name}-{i:05d}-{"%07d" % int(start*100)}-{"%07d" % int(end*100)}'

        # write logs
        log = f'{i:04d}: time: {start:07.2f}:{end:07.2f} score: {score:04.2f}, text: {phoneme[i]}'
        if verbose:
            print(log)

        w_log.write(log +'\n')

        # write main result
        word = phoneme[i].split('|')[0].strip()

        if format == 'kaldi':
            w_text.write(f"{utt_id} {word.upper()}\n")
            w_segments.write(f"{utt_id} {audio_name} {start:.2f} {end:.2f}\n")
            w_score.write(f"{utt_id} {score:.2f}\n")

        else:
            ctm = f'{audio_name} 1 {start:.2f} {end-start:.2f} {word.upper()} {score:04.2f}'
            w_ctm.write(ctm +'\n')

        if threshold is None or score >= threshold:
            success_count += 1

        if slice:
            new_audio = slice_audio(audio, start, end)
            samples = new_audio.samples.unsqueeze(0)
            filename = output_dir / f'{utt_id}.wav'
            torchaudio.save(str(filename), samples, sample_rate=16000, bits_per_sample=16, encoding='PCM_S')

    log = f'successfully aligned {success_count} / {all_count}'
    print(log)

    w_log.write(log+'\n')
    w_log.close()

    if format == 'kaldi':
        w_text.close()
        w_segments.close()
        w_score.close()
    else:
        w_ctm.close()