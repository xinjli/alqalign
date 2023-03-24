from transphone.tokenizer import read_tokenizer
from alqalign.model import read_lm
from alqalign.utils import split_into_sentences
from phonepiece.inventory import read_inventory
from pathlib import Path
import sys
import tqdm
import re
import string

def transcribe_text(text_file, lang_id, data_dir, mode='sentence', verbose=False):

    data_dir = Path(data_dir)
    data_dir.mkdir(exist_ok=True, parents=True)

    inventory = read_inventory(lang_id).phoneme
    r = open(text_file, 'r')

    lm = read_lm(lang_id)

    w_id = open(data_dir / 'ids.txt', 'w')
    w_phoneme = open(data_dir / 'phonemes.txt', 'w')
    w_text = open(data_dir / 'postprocess_text.txt', 'w')

    lines = r.readlines()

    # if only contain 1 line, we split sentences
    if len(lines) == 1 and mode == 'sentence':
        raw_lines = split_into_sentences(lines[0])

        lines = [line.strip() for line in raw_lines if len(line.strip()) >= 1]

    for i, line in enumerate(tqdm.tqdm(lines)):
        id_lst = []
        phoneme_lst = []
        word_lst = []

        words = lm.tokenize_words(line.strip())

        for word in words:

            phonemes = lm.tokenize(word)
            ids = inventory.get_ids(phonemes)

            if mode == 'word':
                w_id.write(' '.join(map(str, ids))+'\n')
                w_phoneme.write(word+' | ' + ' '.join(phonemes)+'\n')
                w_text.write(word+'\n')
            else:
                id_lst.extend(ids)
                phoneme_lst.extend(phonemes)
                word_lst.append(word)

        if mode == 'sentence':
            w_id.write(' '.join(map(str, id_lst))+'\n')
            w_phoneme.write(line.strip()+' | ' + ' '.join(phoneme_lst)+'\n')
            w_text.write(' '.join(words)+'\n')

    r.close()
    w_id.close()
    w_phoneme.close()