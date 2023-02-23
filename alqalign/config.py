import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('alqalign')

root_path=Path(__file__).absolute().parent.parent

# if am is None:
#     am = read_recognizer('xlsr_transformer', '/home/xinjianl/Git/asr2k/data/model/031901/model_0.231203.pt', 'phone', 'raw')
