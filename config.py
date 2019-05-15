import os
from pathlib import Path

# project directory
PRO_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
# data directory
DATA_ROOT = PRO_ROOT / "data"
# dev packages directory
DEV_PAC_ROOT = PRO_ROOT / "dev_packages"
# result directory
RESULT_PATH = PRO_ROOT / "results"
# doc retrieval directory
DOC_RETRIEVAL_ROOT = PRO_ROOT / "doc_retrieval"

WIKI_PAGE_ROOT = DATA_ROOT / "wiki-pages"
TRAIN_DATA_PATH = DATA_ROOT / "train.json"
DEV_DATA_PATH = DATA_ROOT / "devset.json"
RANDOM_DEV_DATA_PATH = DATA_ROOT / "random-devset.json"
TEST_DATA_PATH = DATA_ROOT / "test-unlabelled.json"

if __name__ == '__main__':
    print("PRO_ROOT", PRO_ROOT)
    print("DATA_ROOT", DATA_ROOT)
    print("DEV_PAC_ROOT", DEV_PAC_ROOT)
    print("RESULT_PATH", RESULT_PATH)
    print("DOC_RETRIEVAL_ROOT", DOC_RETRIEVAL_ROOT)

    print("WIKI_PAGE_PATH", WIKI_PAGE_ROOT)
    print("TRAIN_DATA_PATH", TRAIN_DATA_PATH)
    print("DEV_DATA_PATH", DEV_DATA_PATH)
    print("RANDOM_DEV_DATA_PATH", RANDOM_DEV_DATA_PATH)
    print("TEST_DATA_PATH", TEST_DATA_PATH)
