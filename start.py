#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start this system.
First do document retrieval.
Then sentence retrieval.
Finally get original sentence.
"""

import os
import config
from util.doc_util import DocRetrievalTool

import lucene
from doc_retrieval.pyLuceneDoc import PyLuceneDocRetrieval
from sentence_retrieval.pyLuceneSent import PyLuceneSentRetrieval
from model_training.origin_setence import OriginSentence


if __name__ == '__main__':
	# document retrieval
    lucene.initVM()
    PyLuceneDocRetrieval().index_all_wiki()
    PyLuceneDocRetrieval().select_ner_doc()
    PyLuceneDocRetrieval().select_claim_doc()
    PyLuceneDocRetrieval().select_doc()

    # sentence retrieval
    # PyLuceneSentRetrieval().index()
    # PyLuceneSentRetrieval().select_sent()

    # get original sentence which will be used as trainging data
    # OriginSentence().get_origin_sent()
