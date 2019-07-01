#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is used to do document retrieval
"""

import re
import nltk
import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, ScoreDoc, TopDocs, QueryRescorer
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

import os
from datetime import datetime

from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()
index_root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_index")


class PyLuceneDocRetrieval(object):
    def process_identifier(self, page_identifier):
        new_identifier = []
        for token in page_identifier.split('_'):
            token = re.sub("(-LRB-)|(-RRB-)|(-LSB-)|(-RSB-)|(-LCB-)|(-RCB-)", ' ', token)
            if token not in doc_tool.stopwords and token != '':
                new_identifier.append(token)

        return " ".join(new_identifier)

    def process_doc(self, sentence_text, norm_doc):
        for token in sentence_text:
            token = re.sub("(-LRB-)|(-RRB-)|(-LSB-)|(-RSB-)|(-LCB-)|(-RCB-)", ' ', token)
            if token not in doc_tool.stopwords and token != '':
                norm_doc.append(token)

    def process_claim(self, claim):
        """
        tokenize the claim
        """
        new_claim = []
        for token in nltk.word_tokenize(claim):
            token = re.sub('[\/|\?|\*|\(|\)|\!|\[|\]|\{|\}]', ' ', token)
            if token not in doc_tool.stopwords and token != '':
                new_claim.append(token)

        return " ".join(new_claim)

    def process_ner(self, claim):
        new_key = []
        for token in claim:
            token = re.sub("\/", ' ', token)
            if token not in doc_tool.stopwords and token != '':
                new_key.append(token)

        return " ".join(new_key)

    def add(self, prev_identifier, sentence_text, ft1, ft2):
        doc = Document()
        doc.add(Field("page_identifier", prev_identifier, ft1))
        doc.add(Field("title", self.process_identifier(prev_identifier), ft2))
        doc.add(Field("sentence_text", " ".join(sentence_text), ft2))
        return doc

    def index(self, wiki_list):
        # if exists doc_index, delete and create a new one
        doc_tool.cleardir(index_root)
        doc_tool.mkdir(index_root)

        index_dir = FSDirectory.open(Paths.get(index_root))
        writer_config = IndexWriterConfig(StandardAnalyzer())
        writer_config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(index_dir, writer_config)

        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.NONE)

        ft2 = FieldType()
        ft2.setStored(False)
        ft2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        prev_identifier = ""
        total_docs = 0
        for i in range(len(wiki_list)):
            print()
            print("Processing %s..." % wiki_list[i])
            localtime = datetime.now()
            with open(os.path.join(config.WIKI_PAGE_ROOT, wiki_list[i]), 'r', encoding='utf-8') as f_input:
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
                    if page_identifier == prev_identifier:
                        # This is one document
                        self.process_doc(sentence_text, norm_doc)
                    else:
                        total_docs += 1
                        writer.addDocument(self.add(prev_identifier, norm_doc, ft1, ft2))

                        # Start a new document
                        prev_identifier = page_identifier
                        norm_doc.clear()

                        # Prevent the document only has one sentence
                        self.process_doc(sentence_text, norm_doc)

                total_docs += 1
                writer.addDocument(self.add(prev_identifier, norm_doc, ft1, ft2))

            localtime2 = datetime.now()
            print(localtime2)
            print('Time: %.2fs' % (localtime2 - localtime).total_seconds())

        print(total_docs)
        writer.commit()
        writer.close()
        index_dir.close()

    def index_all_wiki(self):
        wiki_list = doc_tool.load_wiki()
        # print(wiki_list)

        print("Start preprocessing the wiki pages...")
        self.index(wiki_list)

        print()
        print("Complete all wiki pages!")

    def select_ner_doc(self):
        # path = config.NEW_TRAIN_DATA_PATH1
        # path = config.DEV_DATA_PATH
        path = config.TEST_DATA_PATH

        data_set = doc_tool.get_data_set(path)
        if type(data_set) != dict:
            return data_set

        index_dir = FSDirectory.open(Paths.get(index_root))
        reader = DirectoryReader.open(index_dir)
        searcher = IndexSearcher(reader)

        # ner_list = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "ner_process"), "train_ner_list.json")
        # ner_list = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "ner_process"), "dev_ner_list.json")
        ner_list = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "ner_process"), "test_ner_list.json")

        pre_list = {}
        for key in data_set:
            claim = data_set[key]['claim']
            label = "SUPPORTS"

            evidence_list = []

            if key in ner_list and self.process_ner(ner_list[key]) != "":
                new_claim = self.process_ner(ner_list[key])
            else:
                new_claim = self.process_claim(claim)

            my_query = QueryParser("title", StandardAnalyzer()).parse(new_claim)

            total_hits = searcher.search(my_query, 1).scoreDocs

            for hit in total_hits:
                doc = searcher.doc(hit.doc)
                evidence_list.append([doc.get("page_identifier")])

            pre_list[key] = {}
            pre_list[key]['claim'] = claim
            pre_list[key]['label'] = label
            pre_list[key]['evidence'] = evidence_list
            print(len(pre_list))

        reader.close()
        index_dir.close()

        print("Start writing...")
        select_result_path = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
        doc_tool.mkdir(select_result_path)

        # doc_tool.dump_json_file(select_result_path, "train_ner.json", pre_list)
        # doc_tool.dump_json_file(select_result_path, "dev_ner.json", pre_list)
        doc_tool.dump_json_file(select_result_path, "test_ner.json", pre_list)

    def select_claim_doc(self):
        # path = config.NEW_TRAIN_DATA_PATH1
        # path = config.DEV_DATA_PATH
        path = config.TEST_DATA_PATH

        data_set = doc_tool.get_data_set(path)
        if type(data_set) != dict:
            return data_set

        index_dir = FSDirectory.open(Paths.get(index_root))
        reader = DirectoryReader.open(index_dir)
        searcher = IndexSearcher(reader)

        pre_list = {}
        for key in data_set:
            claim = data_set[key]['claim']
            label = "SUPPORTS"

            evidence_list = []

            new_claim = self.process_claim(claim)

            my_query = QueryParser("title", StandardAnalyzer()).parse(new_claim)

            total_hits = searcher.search(my_query, 2).scoreDocs

            tmp = []
            for hit in total_hits:
                doc = searcher.doc(hit.doc)
                tmp.append([doc.get("page_identifier"), hit.score])

            evidence_list.append([tmp[0][0]])
            if len(tmp) > 1 and (tmp[0][1] - tmp[1][1] < 1):
                evidence_list.append([tmp[1][0]])

            pre_list[key] = {}
            pre_list[key]['claim'] = claim
            pre_list[key]['label'] = label
            pre_list[key]['evidence'] = evidence_list
            print(len(pre_list))

        reader.close()
        index_dir.close()

        print("Start writing...")
        select_result_path = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
        doc_tool.mkdir(select_result_path)

        # doc_tool.dump_json_file(select_result_path, "train_claim.json", pre_list)
        # doc_tool.dump_json_file(select_result_path, "dev_claim.json", pre_list)
        doc_tool.dump_json_file(select_result_path, "test_claim.json", pre_list)

    def select_doc(self):
        select_result_path = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")

        # ner_result = doc_tool.load_json_file(select_result_path, "train_ner.json")
        # claim_result = doc_tool.load_json_file(select_result_path, "train_claim.json")
        # ner_result = doc_tool.load_json_file(select_result_path, "dev_ner.json")
        # claim_result = doc_tool.load_json_file(select_result_path, "dev_claim.json")
        ner_result = doc_tool.load_json_file(select_result_path, "test_ner.json")
        claim_result = doc_tool.load_json_file(select_result_path, "test_claim.json")

        pre_list = {}
        for key in claim_result:
            claim = claim_result[key]['claim']
            label = "SUPPORTS"

            ner_evidence_list = ner_result[key]["evidence"]
            claim_evidence_list = claim_result[key]["evidence"]
            evidence_list = []

            for evidence in claim_evidence_list:
                if evidence not in evidence_list:
                    evidence_list.append(evidence)

            for evidence in ner_evidence_list:
                if evidence not in evidence_list:
                    evidence_list.append(evidence)

            pre_list[key] = {}
            pre_list[key]['claim'] = claim
            pre_list[key]['label'] = label
            pre_list[key]['evidence'] = evidence_list
            print(len(pre_list))

        print("Start writing...")
        # doc_tool.dump_json_file(select_result_path, "train.json", pre_list)
        # doc_tool.dump_json_file(select_result_path, "dev.json", pre_list)
        doc_tool.dump_json_file(select_result_path, "test.json", pre_list)


if __name__ == '__main__':
    # lucene.initVM()
    # PyLuceneDocRetrieval().index_all_wiki()
    # PyLuceneDocRetrieval().select_doc()
    a = "Alive 2006/2007 was VNV Nation's first concert tour as a duo since 1997."
    print(PyLuceneDocRetrieval().process_claim(a))
