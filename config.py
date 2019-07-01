import os
from pathlib import Path
"""
This file is used to allocate the system path
"""

# project directory
PRO_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
# data directory
DATA_ROOT = PRO_ROOT / "data"
# dev packages directory
DEV_PAC_ROOT = PRO_ROOT / "dev_packages"
# doc retrieval directory
DOC_RETRIEVAL_ROOT = PRO_ROOT / "doc_retrieval"
# sentence retrieval directory
SENT_RETRIEVAL_ROOT = PRO_ROOT / "sentence_retrieval"
# model training directory
MODEL_TRAINING_ROOT = PRO_ROOT / "model_training"

WIKI_PAGE_ROOT = DATA_ROOT / "wiki-pages"
TRAIN_DATA_PATH = DATA_ROOT / "train.json"
TRAIN_DATA_PATH1 = DATA_ROOT / "train1.json"
TRAIN_DATA_PATH3 = DATA_ROOT / "train3.json"
TRAIN_DATA_PATH6 = DATA_ROOT / "train6.json"
TRAIN_DATA_PATH9 = DATA_ROOT / "train9.json"
NEW_TRAIN_DATA_PATH1 = DATA_ROOT / "new_train1.json"
NEW_TRAIN_DATA_PATH3 = DATA_ROOT / "new_train3.json"
NEW_TRAIN_DATA_PATH6 = DATA_ROOT / "new_train6.json"
NEW_TRAIN_DATA_PATH9 = DATA_ROOT / "new_train9.json"
DEV_DATA_PATH = DATA_ROOT / "devset.json"
RANDOM_DEV_DATA_PATH = DATA_ROOT / "random-devset.json"
TEST_DATA_PATH = DATA_ROOT / "test-unlabelled.json"

if __name__ == '__main__':
    print("PRO_ROOT", PRO_ROOT)
    print("DATA_ROOT", DATA_ROOT)
    print("DEV_PAC_ROOT", DEV_PAC_ROOT)
    print("DOC_RETRIEVAL_ROOT", DOC_RETRIEVAL_ROOT)
    print("SENT_RETRIEVAL_ROOT", SENT_RETRIEVAL_ROOT)
    print("MODEL_TRAINING_ROOT", MODEL_TRAINING_ROOT)

    print("WIKI_PAGE_PATH", WIKI_PAGE_ROOT)
    print("TRAIN_DATA_PATH", TRAIN_DATA_PATH)
    print("DEV_DATA_PATH", DEV_DATA_PATH)
    print("RANDOM_DEV_DATA_PATH", RANDOM_DEV_DATA_PATH)
    print("TEST_DATA_PATH", TEST_DATA_PATH)
