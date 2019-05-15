#!/usr/bin/env python
# -*- coding: utf-8 -*-

# train_model = DocRetrievalTool(config.TRAIN_DATA_PATH)
#
# text = "The aims for this subject is for students to develop an understanding of the main " \
#            "algorithms used in natural language processing and text retrieval, " \
#            "for use in a diverse range of applications including text classification, " \
#            "information retrieval, machine translation, and question answering."
#
# tokenized_sentence = train_model.tokenize(text)
#
# print("lemmatize word:")
# print([train_model.lemmatize(token) for token in tokenized_sentence])

# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse status_port 9000 -port 9000 -timeout 15000