#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from math import log, sqrt
from collections import Counter
from collections import defaultdict

import config
from util.doc_util import DocRetrievalTool

doc_tool = DocRetrievalTool()
root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")


class EvaluateDocScore(object):
    def split(self):
        doc_ids = doc_tool.load_pickle_file(root, "doc_ids")
        doc_term_freqs = doc_tool.load_pickle_file(root, "doc_term_freqs")

        # split the large doc_ids and doc_term_freqs file into 10 smaller files
        split_root = os.path.join(config.DOC_RETRIEVAL_ROOT, "split_docid_term_freq")
        doc_tool.mkdir(split_root)

        doc_ids_term_freqs = defaultdict(list)
        num = 0
        for term_id in doc_ids:
            num += 1
            for i in range(len(doc_ids[term_id])):
                doc_ids_term_freqs[term_id].append((doc_ids[term_id][i], doc_term_freqs[term_id][i]))

            if num % 500000 == 0:
                print("Start writing doc_ids_term_freqs")
                doc_tool.dump_pickle_file(split_root, "doc_ids_term_freqs_%d" % (num / 500000), doc_ids_term_freqs)
                doc_ids_term_freqs.clear()
                print("Finish")
            elif num == len(self.doc_ids_term_freqs):
                print("Start writing doc_ids_term_freqs")
                doc_tool.dump_pickle_file(split_root, "doc_ids_term_freqs_%d" % (num / 500000 + 1), doc_ids_term_freqs)
                doc_ids_term_freqs.clear()
                print("Finish")

    def doc_score(self):
        print("load vocab")
        self.vocab = doc_tool.load_pickle_file(root, "vocab")
        print("load doc_ids_term_freqs")
        self.doc_ids_term_freqs = doc_tool.load_pickle_file(root, "doc_ids_term_freqs")
        print("load total_docs")
        self.total_docs = doc_tool.load_pickle_file(root, "total_docs")
        print("load doc_freqs")
        self.doc_freqs = doc_tool.load_pickle_file(root, "doc_freqs")
        print("load doc_len")
        self.doc_len = doc_tool.load_pickle_file(root, "doc_len")

