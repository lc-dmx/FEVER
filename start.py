#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import config
from util.doc_util import DocRetrievalTool
from doc_retrieval.build_inverted_index import DocProcess
from doc_retrieval.build_query_tfidf import TFIDF
# from doc_retrieval.select_doc import SelectDoc
from doc_retrieval.eval_doc_score import EvaluateDocScore
import lucene
from doc_retrieval.pyLuceneInit import PyLuceneDocRetrieval


if __name__ == '__main__':
    # DocProcess().start_process()

    # query = ['nikolaj', 'coster-waldau', 'work', 'fox', 'broadcast', 'company', '.']
    # TFIDF().rank_doc(query)

    # select_doc = SelectDoc()
    # select_doc.query_tfidf()

    # doc_tool = DocRetrievalTool()
    # root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
    # aa = doc_tool.load_pickle_file(root, "doc_loc")
    # print(aa)


    lucene.initVM()
    # PyLuceneDocRetrieval().index_all_wiki()
    PyLuceneDocRetrieval().select_doc()
    # query = "Nikolaj Coster-Waldau worked with the Fox Broadcasting Company."
    # PyLuceneDocRetrieval().select_doc(query)