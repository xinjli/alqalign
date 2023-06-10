from alqalign.process_audio import *
from alqalign.process_text import *
from alqalign.process_alignment import process_alignment
from alqalign.audio import find_audio
from alqalign.config import logger
from pathlib import Path
import argparse
import kaldiio
import shutil
from distutils.util import strtobool
import torch


def process(utt_ids, audio_files, text_files, output_dirs, lang_id, mode='sentence',
            device=None, batch_size=32, output_format='kaldi', slice=False, force=False, keep_logit=False, debug=False):

    for utt_id, audio_file, text_file, output_dir in zip(utt_ids, audio_files, text_files, output_dirs):

        if force and output_dir.exists():
            print(f"cleaning {output_dir}")
            shutil.rmtree(output_dir, ignore_errors=True)

        transcribe_audio(audio_file, lang_id, output_dir, device=device, batch_size=batch_size, force=force)
        transcribe_text(text_file, lang_id, output_dir, mode, device=device)
        try:
            process_alignment(audio_file, text_file, lang_id, output_dir, utt_id=utt_id, slice=slice,
                              verbose=debug, format=output_format)
        except:
            logger.info(f"failed to align: {utt_id}")

        # delete logit if necessary
        if not keep_logit:
            for path in output_dir.glob('logit.npz'):
                path.unlink()

        # delete intermediate artifacts if necessary
        if not debug:
            artifacts = ['phonemes.txt', 'ids.txt', 'decode.txt', 'detail.txt', 'postprocess_text.txt', 'log.txt']
            for artifact in artifacts:
                if (output_dir / artifact).exists():
                    (output_dir / artifact).unlink()


if __name__ == '__main__':

    parser = argparse.ArgumentParser('speech aligner')

    # main configures
    parser.add_argument('-l', '--lang', help='the target language you want to use', default='eng')
    parser.add_argument('-t', '--text', help='path to a text file or a directory containing text files', required=True)
    parser.add_argument('--text_format', help='text format of the given input text file.', default='plain', choices=['plain', 'kaldi'])
    parser.add_argument('-a', '--audio', help='path to a audio file or a directory containing audio files', required=True)
    parser.add_argument('--audio_format', help='audio format of the given input audio file', default='wav', choices=['wav', 'scp'])
    parser.add_argument('-o', '--output', help='path to the output directory', default='output')
    parser.add_argument('--output_format', help='audio format of the given input audio file', default='kaldi', choices=['ctm', 'kaldi'])
    parser.add_argument('-m', '--mode', help='alignment mode: sentence or word or phoneme', default='sentence', choices=['sentence', 'word', 'phoneme'])
    parser.add_argument('--ngpu', help='distributed alignment when multiple gpu is available', type=int)

    # other configures
    parser.add_argument('-v', '--verbose', help='showing alignment log', default=False)
    parser.add_argument('--keep_logit', help='keep logit after alignment', default=False)
    parser.add_argument('--batch_size', help='you should change this batch_size depending on your GPU memory', default=8)
    parser.add_argument('--threshold', help='threshold score', default=-3)
    parser.add_argument('--slice', help='whether to extract the aligned audio files', default=False)
    parser.add_argument('--force', help='ignoring previous cached results, re-align from scratch', default="false", type=strtobool)
    parser.add_argument('--debug', help='keep intermediate artifacts for debugging purpose', default="false", type=strtobool)

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    lang_id = args.lang
    audio_file = Path(args.audio)
    text_file = Path(args.text)
    threshold = float(args.threshold)
    batch_size = int(args.batch_size)
    slice=args.slice
    verbose=args.verbose
    text_format = args.text_format
    output_format = args.output_format
    mode=args.mode
    keep_logit=args.keep_logit
    debug = args.debug

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

    ngpu = args.ngpu

    if ngpu is not None and ngpu >= 2:
        print("distributed alignment")

        torch.multiprocessing.set_start_method('spawn')

        from multiprocessing import Process
        proc_lst = []

        for i in range(ngpu):
            proc = Process(target=process, args=(utt_ids[i::ngpu], audio_files[i::ngpu], text_files[i::ngpu], output_dirs[i::ngpu], lang_id, mode, i, batch_size, output_format, slice, args.force, keep_logit))
            proc.start()
            proc_lst.append(proc)

        for proc in proc_lst:
            proc.join()

    else:

        if ngpu is None or ngpu == 0:
            device = -1
        else:
            device = 0

        process(utt_ids, audio_files, text_files, output_dirs, lang_id, mode, device, batch_size, output_format, slice=slice, force=args.force, keep_logit=keep_logit, debug=debug)