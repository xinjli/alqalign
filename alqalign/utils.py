# -*- coding: utf-8 -*-
# reference: adapted from https://stackoverflow.com/questions/4576077/how-can-i-split-a-text-into-sentences
import kaldiio
import re
from allosaurus.audio import read_audio, write_audio, split_audio, silent_audio, concatenate_audio, Audio
import torch

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|edu|me)"
digits = "([0-9])"


def read_audio_rspecifier(audio_file):

    if '.ark' in str(audio_file):
        mat = kaldiio.load_mat(audio_file)
        if isinstance(mat, tuple):
            sample_rate = mat[0]
            samples = torch.from_numpy(mat[1].astype('float32'))
        else:
            sample_rate = 16000
            samples = torch.from_numpy(mat.astype('float32'))

        audio = Audio(samples, sample_rate)

    else:
        audio = read_audio(audio_file, 16000)

    return audio

def split_into_sentences(text):
    text = " " + text + "  "
    if "。" in text: text = text.replace("。",". ")
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "！" in text: text = text.replace("！", "!")
    if "!" in text: text = text.replace("!\"","\"!")
    if "？" in text: text = text.replace("？", "?")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".","<stop>")
    text = text.replace("?","<stop>")
    text = text.replace("!","<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = [s for s in [s.strip() for s in sentences] if len(s) > 0]
    return sentences
