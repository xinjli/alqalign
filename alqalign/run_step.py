from alqalign.process_audio import *
from alqalign.process_text import *
from alqalign.process_alignment import *
from allosaurus.audio import find_audio
from alqalign.config import logger
from pathlib import Path
import argparse
import kaldiio
from distutils.util import strtobool


if __name__ == '__main__':

    parser = argparse.ArgumentParser('speech aligner')
    parser.add_argument('-t', '--text', help='path to a text file', required=True)
    parser.add_argument('--text_format', help='text format', default='plain', choices=['plain', 'kaldi'])
    parser.add_argument('-a', '--audio', help='path to a audio file', required=True)
    parser.add_argument('--audio_format', help='audio format', default='wav', choices=['wav', 'scp'])
    parser.add_argument('-o', '--output', help='path to the output directory', default='output')
    parser.add_argument('-l', '--lang', help='target language', default='eng')
    parser.add_argument('-m', '--mode', help='sentence or word or phoneme', default='sentence', choices=['sentence', 'word', 'phoneme'])
    parser.add_argument('-v', '--verbose', help='showing alignment log', default=False)
    parser.add_argument('--batch_size', help='threshold score', default=8)
    parser.add_argument('--threshold', help='threshold score', default=-3)
    parser.add_argument('--slice', default=False)
    parser.add_argument('--force', default="false", type=strtobool)

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    lang_id = args.lang
    audio_file = Path(args.audio)
    text_file = Path(args.text)
    steps = list(map(int, args.step.split(',')))
    threshold = float(args.threshold)
    batch_size = int(args.batch_size)
    slice=args.slice
    verbose=args.verbose
    text_format = args.text_format
    mode=args.mode

    utt2audio = {}
    utt2text = {}
    utt_lst = []

    audio_files = []
    text_files = []
    output_dirs = []
    utt_ids = []

    # audio files
    if audio_file.is_dir():
        audio_paths = find_audio(audio_file)
        for audio_path in audio_paths:
            utt_id = audio_path.stem
            utt2audio[utt_id] = audio_path

    elif str(audio_file).endswith('scp'):
        for line in open(audio_file):
            utt_id, ark_key = line.strip().split()
            utt2audio[utt_id] = ark_key
    else:
        audio_files = [audio_file]
        output_dirs = [output_dir]
        text_files = [text_file]
        utt_ids = [audio_file.stem]

    # text files
    if text_file.is_dir():
        for text_path in sorted(text_file.glob('*')):
            utt_id = text_path.stem
            if utt_id in utt2audio:
                audio_files.append(utt2audio[utt_id])
                text_files.append(text_path)
                output_dirs.append(output_dir / utt_id)
                utt_ids.append(utt_id)
    else:
        for i, line in enumerate(open(text_file, 'r')):
            if text_format == 'kaldi':
                fields = line.strip().split()
                utt_id = fields[0]
                sent = ' '.join(fields[1:])
            else:
                utt_id = str(i)
                sent = line

            if utt_id in utt2audio:
                audio_files.append(utt2audio[utt_id])
                text_files.append(sent)
                output_dirs.append(output_dir / utt_id)
                utt_ids.append(utt_id)

    total_file_cnt = len(utt_ids)
    print(f"total {total_file_cnt} files to be processed")
    idx = 0

    if 1 in steps:
        logger.info("step 1: transcribe audios")
        idx = 0
        for utt_id, audio_file, output_dir in zip(utt_ids, audio_files, output_dirs):
            if total_file_cnt != 1:
                idx += 1
                logger.info(f"processing audio {idx}/{total_file_cnt}: {utt_id}")

            transcribe_audio(audio_file, lang_id, output_dir, batch_size=batch_size, force=args.force)

    if 2 in steps:
        logger.info("step 2: transcribing text")
        idx = 0
        for text_file, output_dir, utt_id in zip(text_files, output_dirs, utt_ids):
            if total_file_cnt != 1:
                idx += 1
                logger.info(f"processing text {idx}/{total_file_cnt}: {utt_id}")

            transcribe_text(text_file, lang_id, output_dir, mode)

    if 3 in steps:
        idx = 0
        logger.info('step 3: aligning')
        for audio_file, text_file, output_dir, utt_id in zip(audio_files, text_files, output_dirs, utt_ids):
            if total_file_cnt != 1:
                idx += 1
                logger.info(f"processing alignment {idx}/{total_file_cnt}: {utt_id}")

            try:
                align(audio_file, text_file, lang_id, output_dir, utt_id=utt_id, threshold=threshold, slice=slice, verbose=verbose)
            except:
                logger.info(f"failed to align: {utt_id}")