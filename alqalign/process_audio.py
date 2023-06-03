from alqalign.config import logger
from alqalign.model import read_am
from alqalign.audio import read_audio


def transcribe_audio(audio_file, lang_id, data_dir, duration=15.0, batch_size=8, force=False):

    if (data_dir / f'logit.npz').exists() and not force:
        return

    data_dir.mkdir(parents=True, exist_ok=True)

    audio = read_audio(audio_file)

    logger.info(f"total audio duration: {audio.duration()}")

    am = read_am(lang_id)

    # dump output results
    am.recognize(audio, lang_id, output=data_dir, batch_size=batch_size, segment_duration=duration, verbose=True, logit=True)