from alqalign.record import read_record
import torch

def read_audio_dataset(corpus_path, segment_duration=15.0):

    record = read_record(corpus_path, segment_duration=segment_duration)
    utt_ids = record.utt_ids

    return Dataset(utt_ids, record)

class Dataset:

    def __init__(self, utt_ids, record):
        self.utt_ids = utt_ids
        self.record = record

    def __repr__(self):
        return f"<Dataset utts: {len(self.utt_ids)} />"


    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.utt_ids)

    def __getitem__(self, item_or_utt_id):

        if isinstance(item_or_utt_id, int):
            utt_id = self.utt_ids[item_or_utt_id]
        else:
            utt_id = item_or_utt_id

        # audio features
        audio = self.record.read_audio(utt_id, 16000)
        feats = audio.samples

        return {
            'utt_id': utt_id,
            'feats': feats,
        }