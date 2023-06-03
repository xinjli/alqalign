import unittest
from alqalign.app import align
from alqalign.config import sample_path
class TestAlignment(unittest.TestCase):

    def test_simple_alignment(self):

        audio_file = sample_path / 'eng' / 'utt.wav'
        text_file = sample_path / 'eng' / 'utt.txt'

        result = align(audio_file, text_file, 'eng', mode='sentence')

        # two sentences
        self.assertEqual(len(result), 2)

        # check timestamps
        self.assertLess(result[0]['start'], 0.5)
        self.assertGreater(result[0]['start'], 0.1)
        self.assertLess(result[0]['end'], 3.8)
        self.assertGreater(result[0]['end'], 3.4)

        self.assertLess(result[1]['start'], 4.0)
        self.assertGreater(result[1]['start'], 3.6)
        self.assertLess(result[1]['end'], 9.3)
        self.assertGreater(result[1]['end'], 8.9)

        # check scores
        self.assertGreater(result[0]['score'], -0.5)
        self.assertGreater(result[1]['score'], -0.5)

        # check texts non empty
        self.assertTrue(len(result[0]['text']) > 0)
        self.assertTrue(len(result[1]['text']) > 0)