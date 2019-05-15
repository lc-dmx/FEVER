#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter
from collections import defaultdict
from datetime import datetime

from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()


class DocProcess(object):
    def __init__(self):
        # contains (term, term id) pairs 4698377
        self.vocab = defaultdict(int)
        # contains (term id, term) pairs
        self.invert_vocab = defaultdict(str)

        # the total number of documents 5396106
        self.total_docs = 0

        # The length of each document
        self.doc_len = defaultdict(int)

        # For each term ID, it stores a list of document ids of all documents containing that term
        self.doc_ids = defaultdict(list)

        # For each term ID, it stores a list of document term frequencies 𝑓𝑑,𝑡 (how often a document 𝑑 contains the term 𝑡)
        # of the corresponding documents stored in doc_ids
        self.doc_term_freqs = defaultdict(list)

        # For each term ID, it stores the document frequency 𝑓𝑡 indicating
        # the number of documents containing one or more occurrences of term 𝑡
        self.doc_freqs = defaultdict(int)

        # contains (doc_identifier, doc_identifier_id) pairs
        self.doc_identifier = defaultdict(int)
        # contains (doc_identifier_id, doc_identifier) pairs
        self.invert_doc_identifier = defaultdict(str)

        # contains (doc_identifier_id, file_id) pairs
        self.doc_loc = defaultdict(int)

        # parentheses_dict = [
        #     ('-LRB-', '-RRB-'),
        #     ('-LSB-', '-RSB-'),
        #     ('-LCB-', '-RCB-'),
        #     ('-lrb-', '-rrb-'),
        #     ('-lsb-', '-rsb-'),
        #     ('-lcb-', '-rcb-')
        # ]

    def norm(self, sentence_text, norm_doc):
        for term in sentence_text:
            term = doc_tool.lemmatize(term.lower())
            if term not in doc_tool.stopwords:
                norm_doc.append(term)

                if term not in self.vocab:
                    length = len(self.vocab)
                    self.vocab[term] = length
                    self.invert_vocab[length] = term

    def term_freq(self, norm_doc, identifier_id):
        dfs = Counter()
        for term in norm_doc:
            dfs[term] += 1

        self.doc_len[identifier_id] = sum(dfs.values())
        for item in dfs.items():
            term_id = self.vocab[item[0]]
            term_freq = item[1]
            self.doc_ids[term_id].append(identifier_id)
            self.doc_term_freqs[term_id].append(term_freq)
            self.doc_freqs[term_id] += 1

    def deal_wiki(self, wiki_list):
        prev_identifier = ""
        for i in range(len(wiki_list)):
            print()
            print("Processing %s..." % wiki_list[i])
            localtime = datetime.now()
            with open(os.path.join(config.WIKI_PAGE_ROOT, wiki_list[i]), 'r', encoding="utf8") as f_input:
                line_number = -1
                norm_doc = []

                for line in f_input:
                    line_number += 1
                    words = line.split(' ')
                    page_identifier = words[0]
                    sentence_number = words[1]
                    sentence_text = words[2:]

                    if not sentence_number.isdigit():
                        continue

                    if line_number == 0:
                        prev_identifier = page_identifier
                        length = len(self.doc_identifier)
                        self.doc_identifier[prev_identifier] = length
                        self.invert_doc_identifier[length] = prev_identifier
                        self.doc_loc[length] = i
                    if page_identifier == prev_identifier:
                        # This is one document
                        self.norm(sentence_text, norm_doc)

                    else:
                        # The previous document ends, we need to calculate the term frequency
                        self.term_freq(norm_doc, self.doc_identifier[prev_identifier])

                        # Start a new document
                        prev_identifier = page_identifier
                        length = len(self.doc_identifier)
                        self.doc_identifier[prev_identifier] = length
                        self.invert_doc_identifier[length] = prev_identifier
                        self.doc_loc[length] = i

                        norm_doc.clear()

                        # Prevent the document only has one sentence
                        self.norm(sentence_text, norm_doc)

                # Add the last document
                self.term_freq(norm_doc, self.doc_identifier[prev_identifier])

            localtime2 = datetime.now()
            print('Time: %.2fs' % (localtime2 - localtime).total_seconds())

        self.total_docs = len(self.doc_identifier)
        print()
        root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")

        print("Start writing doc_identifier list...")
        doc_tool.dump_pickle_file(root, "doc_identifier", self.doc_identifier)
        doc_tool.dump_pickle_file(root, "invert_doc_identifier", self.invert_doc_identifier)

        print("Start writing doc_ids list...")
        doc_tool.dump_pickle_file(root, "doc_ids", self.doc_ids)

        print("Start writing term_frequency list...")
        doc_tool.dump_pickle_file(root, "doc_term_frequency", self.doc_term_freqs)

        print("Start writing doc_freqs list...")
        doc_tool.dump_pickle_file(root, "doc_freqs", self.doc_freqs)

        print("Start writing doc_len list...")
        doc_tool.dump_pickle_file(root, "doc_len", self.doc_len)

        print("Start writing vocabulary list...")
        doc_tool.dump_pickle_file(root, "vocab", self.vocab)
        doc_tool.dump_pickle_file(root, "invert_vocab", self.invert_vocab)

        print("Start writing doc_loc list...")
        doc_tool.dump_pickle_file(root, "doc_loc", self.doc_loc)

        doc_tool.dump_pickle_file(root, "total_docs", self.total_docs)

        print("Finish")

    def start_process(self):
        wiki_list = doc_tool.load_wiki()
        # print(wiki_list)

        doc_tool.mkdir(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"))

        print("Start preprocessing the wiki pages...")
        self.deal_wiki(wiki_list)

        print()
        print("Complete all wiki pages!")
        print(self.total_docs)
        print(len(self.vocab))


if __name__ == '__main__':
    # doc_tool.mkdir(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"))
    #
    # doc_process = DocProcess()
    # file_list = ['wiki-001.txt']
    # print("Start preprocessing the wiki pages...")
    # doc_process.deal_wiki(file_list)
    #
    # print()
    # print("Complete all wiki pages!")
    # print(doc_process.total_docs)

    aa = defaultdict(list)
    aa[0] = [(1, 1), (2, 2), (3, 3)]
    aa[1] = [(1, 2), (2, 4), (3, 6)]
    print(aa)

    for key in aa:
        for i in range(len(aa[key])):
            print(aa[key][i][0], aa[key][i][1])

    # root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
    # aa = doc_tool.load_pickle_file(root, "doc_ids_term_freqs")
    # print(aa[0])