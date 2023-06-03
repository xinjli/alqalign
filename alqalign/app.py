from alqalign.model import read_am, read_phoneme_inventory, read_lm
from alqalign.process_audio import transcribe_audio
from alqalign.process_text import transcribe_text
from alqalign.process_alignment import process_alignment
import numpy as np
from pathlib import Path
import tempfile

from alqalign.ctc_segmentation.ctc_segmentation import (
    CtcSegmentationParameters,
    ctc_segmentation,
    determine_utterance_segments,
    prepare_text,
    prepare_token_list,
)


def align(audio, text, lang_id='eng', mode='sentence'):

    result = []

    with tempfile.TemporaryDirectory() as output_dir:
        output_dir = Path(output_dir)
        # step 1
        transcribe_audio(audio, lang_id, output_dir)

        # step 2
        transcribe_text(text, lang_id, output_dir, mode=mode)

        # step 3
        process_alignment(audio, text, lang_id, output_dir, mode=mode)

        segments_lines = open(output_dir / 'segments', 'r').readlines()
        text_lines = open(output_dir / 'text', 'r').readlines()
        score_lines = open(output_dir / 'score', 'r').readlines()

        for i in range(len(segments_lines)):
            segments = segments_lines[i].strip().split()
            text = text_lines[i].strip()
            score = float(score_lines[i].strip().split()[1])

            utt_dict = {}

            utt_id = segments[0]
            utt_dict['utt_id'] = utt_id

            start = float(segments[2])
            end = float(segments[3])

            utt_dict['start'] = start
            utt_dict['end'] = end
            utt_dict['text'] = text.split(' ', 1)[1]
            utt_dict['score'] = score
            result.append(utt_dict)

    return result


def compute_alignment_score(audio, text, lang_id):

    # run acoustic model
    am = read_am(lang_id)
    res, lpz = am.recognize(audio, lang_id, output=None, batch_size=8, segment_duration=15.0, logit=True)

    print(res)
    print(lpz.shape)

    lm = read_lm(lang_id)

    # run pronunciation model
    inventory = read_phoneme_inventory(lang_id)
    words = lm.tokenize_words(text.strip())

    id_lst = []
    for word in words:

        phonemes = lm.tokenize(word)
        ids = inventory.get_ids(phonemes)
        id_lst.extend(ids)

    # CTC segmentation settings
    config = CtcSegmentationParameters()
    config.char_list = inventory.elems[:-1]
    config.index_duration = 0.02
    #config.blank_transition_cost_zero = True
    ground_truth_mat, utt_begin_indices = prepare_token_list(config, [np.array(id_lst)])

    print(ground_truth_mat)
    print(utt_begin_indices)

    if(len(ground_truth_mat) > lpz.shape[0]):
        print("audio is shorter than text")
        return -100.0

    timings, char_probs, state_list = ctc_segmentation(
        config, lpz, ground_truth_mat
    )

    print(timings)
    print(char_probs)
    print(state_list)

    segments = determine_utterance_segments(
        config, utt_begin_indices, char_probs, timings, [text], mode='sentence')

    return segments[0][2]