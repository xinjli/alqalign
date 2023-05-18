from alqalign.config import logger
from alqalign.model import read_am
from alqalign.utils import read_audio_rspecifier


def transcribe_audio(audio_file, lang_id, data_dir, duration=15.0, batch_size=8, force=False):

    if (data_dir / f'logit.npz').exists() and not force:
        return

    data_dir.mkdir(parents=True, exist_ok=True)

    audio = read_audio_rspecifier(audio_file)

    logger.info(f"total audio duration: {audio.duration()}")

    am = read_am(lang_id)

    # dump output results
    am.recognize(audio, lang_id, output=data_dir, batch_size=batch_size, segment_duration=duration, verbose=True, logit=True)


    # logit_lst = []
    #
    # for logit in logits:
    #   lpz = logit[1]
    #   lpz = np.concatenate([lpz, lpz[-1][np.newaxis, :]], axis=0)
    #   logit_lst.append(lpz)
    #
    # lpz = np.concatenate(logit_lst, axis=0)
    #
    # lpz.dump(data_dir / f'logit.npz')
    #
    # w = open(data_dir / f'decode.txt', 'w')
    #
    # print(decode_info_lst)
    #
    # for i, token_pair in enumerate(decode_info_lst):
    #     utt_id = token_pair[0]
    #     decoded_info = token_pair[1]
    #
    #     assert int(utt_id[-4:]) == i
    #
    #     chunk_start_time = i*duration
    #     # chunk_end_time = str(datetime.timedelta(seconds=(i+1)*duration))
    #
    #     for phone_info in decoded_info:
    #         start_time = phone_info['start'] + chunk_start_time
    #         duration = phone_info['duration']
    #         phone = phone_info['phone']
    #         prob = phone_info['prob']
    #
    #         w.write(f"{utt_id} {start_time:.3f} {duration:.3f} {phone} {prob}\n")
    #
    # w.close()