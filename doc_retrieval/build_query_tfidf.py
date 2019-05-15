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


class TFIDF(object):
    def __init__(self):
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

    def rank_doc(self, query, k=20):
        """
        for each query, get the <docid, score> of the 50 documents whose tfidf score is the highest
        :return:
        """
        # scores stores doc ids and their scores
        total_score = Counter()
        inverted_index = defaultdict(list)
        for term in query:
            if inverted_index[term]:
                continue

            term_id = self.vocab[term]
            for docid, freq in self.doc_ids_term_freqs[term_id]:
                tfidf = log(1 + freq) * log(self.total_docs / self.doc_freqs[term_id]) / sqrt(self.doc_len[docid])
                inverted_index[term].append([docid, tfidf])

        for term in query:
            for docid, score in inverted_index[term]:
                total_score[docid] += score

        return total_score.most_common(k)


if __name__ == '__main__':
    query = ['nikolaj', 'coster-waldau', 'work', 'fox', 'broadcast', 'company', '.']
    # ['roman', 'atwood', 'content', 'creator', '.']
    # query2 = ['history', 'art', 'include', 'architecture', ',', 'dance', ',', 'sculpture', ',', 'music', ',', 'paint', ',',
    # 'poetry', 'literature', ',', 'theatre', ',', 'narrative', ',', 'film', ',', 'photography', 'graphic', 'art', '.']
    # ['adrienne', 'bailon', 'accountant', '.']
    # ['system', 'briefly', 'disband', 'limbo', '.']
    # ['homeland', 'american', 'television', 'spy', 'thriller', 'base', 'israeli', 'television', 'series', 'prisoner', 'war', '.']
    # ['beautiful', 'reach', 'number', 'two', 'billboard', 'hot', '100', '2003', '.']
    # ['neal', 'schon', 'name', '1954', '.']
    # ['boston', 'celtic', 'play', 'home', 'game', 'td', 'garden', '.']
    # ['ten', 'commandment', 'epic', 'film', '.']

    print(TFIDF().rank_doc(query))
