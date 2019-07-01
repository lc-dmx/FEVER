#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is used to find name entity of a given string
"""

import os
from collections import defaultdict
from nltk.parse import CoreNLPParser

import config
from util.doc_util import DocRetrievalTool

parser = CoreNLPParser(url='http://localhost:9000')
ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')

doc_tool = DocRetrievalTool()
root = os.path.join(config.DOC_RETRIEVAL_ROOT, "ner_process")
doc_tool.mkdir(root)


class NER(object):
    def find_claim_ner(self):
        """
        find the name entity in the claim
        :return: ner list
        """
        # change the path dir
        # path = config.TRAIN_DATA_PATH
        path = config.DEV_DATA_PATH
        # path = config.TEST_DATA_PATH

        data_set = doc_tool.get_data_set(path)
        if type(data_set) != dict:
            return data_set

        ner_list = defaultdict(list)
        for key in data_set:
            claim = data_set[key]['claim']
            for entity in ner_tagger.tag(parser.tokenize(claim)):
                if entity[1] != 'O':
                    ner_list[key].append(entity[0])
            print(len(ner_list))

        print("Start writing...")
        # doc_tool.dump_json_file(root, "train_ner_list.json", ner_list)
        doc_tool.dump_json_file(root, "dev_ner_list.json", ner_list)
        # doc_tool.dump_json_file(root, "test_ner_list.json", ner_list)


if __name__ == '__main__':
    NER().find_claim_ner()
