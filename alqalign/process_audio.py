from allosaurus.audio import read_audio, write_audio, split_audio, silent_audio, concatenate_audio
import numpy as np
from pathlib import Path
from tqdm import tqdm
from unialign.config import logger
from unialign.model import read_am
import datetime

def transcribe_audio(audio_file, lang_id, data_dir, duration=15.0, batch_size=8, verbose=False):

    if (data_dir / f'logit.npz').exists():
        return

    data_dir.mkdir(parents=True, exist_ok=True)

    audio = read_audio(audio_file, 16000)
    logger.info(f"total audio duration: {audio.duration()}")

    audio_lst = split_audio(audio, duration=duration)

    am = read_am(lang_id)

    logits, tokens = am.get_logits_batch(audio_lst, lang_id, batch_size=batch_size)

    logit_lst = []

    for logit in logits:
      lpz = logit[1]
      lpz = np.concatenate([lpz, lpz[-1][np.newaxis, :]], axis=0)
      logit_lst.append(lpz)

    lpz = np.concatenate(logit_lst, axis=0)

    lpz.dump(data_dir / f'logit.npz')

    w = open(data_dir / f'decoded.txt', 'w')
    for i, token_pair in enumerate(tokens):
        utt_id = token_pair[0]
        token = token_pair[1]

        assert int(utt_id) == i

        start_time = str(datetime.timedelta(seconds=i*duration))
        end_time = str(datetime.timedelta(seconds=(i+1)*duration))

        w.write(f"{start_time} -> {end_time}: {token}\n")

    w.close()


    # if am is None:
    #     am = read_recognizer('xlsr_transformer', '/home/xinjianl/Git/asr2k/data/model/031901/model_0.231203.pt', 'phone', 'raw')
    #
    # for file in tqdm(sorted(audio_dir.glob('*.wav'))):
    #     name = file.stem
    #     print('transcribing audio ', file)
    #     res = am.get_logits(file, lang_id)
    #     lpz = res[0][0].cpu().detach().numpy()
    #     lpz = np.concatenate([lpz, lpz[-1][np.newaxis, :]], axis=0)
    #     lpz.dump(logit_dir / f'{name}.npz')