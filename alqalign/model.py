from transphone.tokenizer import read_tokenizer
import panphon
from phonepiece.inventory import read_inventory
from allosaurus.app import read_recognizer

# models are singletons
am_ = None
lm_dict_ = {}
phoneme_dict_ = {}

def read_phoneme_inventory(lang_id):
    global phoneme_dict_

    if lang_id in phoneme_dict_:
        return phoneme_dict_[lang_id]

    phoneme_inv = read_inventory(lang_id).phoneme
    phoneme_dict_[lang_id] = phoneme_inv
    return phoneme_inv

def read_am(lang_id):

    global am_

    if am_ is not None:
        return am_

    am_ = read_recognizer()
    return am_


def read_lm(lang_id):

    global lm_dict_

    if lang_id in lm_dict_:
        return lm_dict_[lang_id]

    lm_dict_[lang_id] = read_tokenizer(lang_id)
    return lm_dict_[lang_id]