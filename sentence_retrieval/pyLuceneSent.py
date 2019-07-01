#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is used to do sentence retrieval
"""

import re
import nltk
import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, ScoreDoc
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

import os

from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()
index_root = os.path.join(config.SENT_RETRIEVAL_ROOT, "sent_index")


class PyLuceneSentRetrieval(object):
    def process_sent(self, sentence_text):
        new_sentence = []
        for token in sentence_text.split(' '):
            token = re.sub("(-LRB-)|(-RRB-)|(-LSB-)|(-RSB-)|(-LCB-)|(-RCB-)", ' ', token)
            token = doc_tool.lemmatize(token.lower())
            if token not in doc_tool.stopwords and token != '':
                new_sentence.append(token)

        return " ".join(new_sentence)

    def process_claim(self, claim):
        """
        tokenize the claim
        """
        new_claim = []
        for token in nltk.word_tokenize(claim):
            token = re.sub('[\/|\?|\*|\(|\)|\!|\[|\]|\{|\}]', ' ', token)
            token = doc_tool.lemmatize(token.lower())
            if token not in doc_tool.stopwords and token != '':
                new_claim.append(token)

        return " ".join(new_claim)

    def doc(self):
        # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "train.json")
        # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "dev_claim.json")
        selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "test_claim.json")
        doc_list = set()
        for key in selected_doc:
            for page_identifier in selected_doc[key]['evidence']:
                doc_list.add(page_identifier[0])
        return doc_list

    def index(self):
        # if exists sent_index, delete and create a new one
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

        doc_list = self.doc()
        file_path = os.path.join(config.SENT_RETRIEVAL_ROOT, "merge_doc")
        file_list = os.listdir(file_path)

        num = 0
        for file in file_list:
            docs = doc_tool.load_json_file(file_path, file)
            for page_identifier in docs:
                if page_identifier in doc_list:
                    num += 1
                    for sent_number in docs[page_identifier]:
                        sentence_text = self.process_sent(docs[page_identifier][sent_number])
                        doc = Document()
                        doc.add(Field("page_identifier", page_identifier, ft1))
                        doc.add(Field("sentence_number", sent_number, ft1))
                        doc.add(Field("sentence_text", sentence_text, ft2))
                        writer.addDocument(doc)
                    print(num)

        writer.commit()
        writer.close()
        index_dir.close()

    def select_sent(self):
        # path = config.NEW_TRAIN_DATA_PATH1
        # path = config.DEV_DATA_PATH
        path = config.TEST_DATA_PATH

        data_set = doc_tool.get_data_set(path)
        if type(data_set) != dict:
            return data_set

        index_dir = FSDirectory.open(Paths.get(index_root))
        reader = DirectoryReader.open(index_dir)
        searcher = IndexSearcher(reader)

        # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "train.json")
        # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "dev_claim.json")
        selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "test_claim.json")

        pre_list = {}
        for key in data_set:
            claim = data_set[key]['claim']
            label = 'SUPPORTS'

            evidence_list = []

            new_claim = self.process_claim(claim)

            my_query = QueryParser("sentence_text", StandardAnalyzer()).parse(new_claim)
            total_hits = searcher.search(my_query, 10).scoreDocs

            tmp = []
            for hit in total_hits:
                doc = searcher.doc(hit.doc)
                for i in range(len(selected_doc[key]["evidence"])):
                    if doc.get("page_identifier") == selected_doc[key]["evidence"][i][0] and len(tmp) < 3:
                        tmp.append([doc.get("page_identifier"), int(doc.get("sentence_number")), hit.score])

            if len(tmp) > 0:
                evidence_list.append([tmp[0][0], tmp[0][1]])
                if len(tmp) > 1 and (tmp[0][2] - tmp[1][2] < 1):
                    evidence_list.append([tmp[1][0], tmp[1][1]])
                    if len(tmp) > 2 and (tmp[1][2] - tmp[2][2] < 1):
                        evidence_list.append([tmp[2][0], tmp[2][1]])

            doc1 = searcher.doc(total_hits[0].doc)
            if [doc1.get("page_identifier"), int(doc1.get("sentence_number"))] not in evidence_list:
                evidence_list.append([doc1.get("page_identifier"), int(doc1.get("sentence_number"))])

            pre_list[key] = {}
            pre_list[key]['claim'] = claim
            pre_list[key]['label'] = label
            pre_list[key]['evidence'] = evidence_list
            print(len(pre_list))

        reader.close()
        index_dir.close()

        print("Start writing...")
        select_result_path = os.path.join(config.SENT_RETRIEVAL_ROOT, "sent_retrieval_result")
        doc_tool.mkdir(select_result_path)

        # doc_tool.dump_json_file(select_result_path, "train.json", pre_list)
        # doc_tool.dump_json_file(select_result_path, "dev.json", pre_list)
        doc_tool.dump_json_file(select_result_path, "test.json", pre_list)

    # def select_sent(self):
        # index_dir = FSDirectory.open(Paths.get(index_root))
        # reader = DirectoryReader.open(index_dir)
        # searcher = IndexSearcher(reader)
        #
        # # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "new_train9_selected_doc.json")
        # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "dev_selected_doc.json")
        # # selected_doc = doc_tool.load_json_file(os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result"), "test_selected_doc.json")
        #
        # pre_list = {}
        # for key in selected_doc:
        #     claim = selected_doc[key]['claim']
        #     label = selected_doc[key]['label']
        #
        #     if label == 'NOT ENOUGH INFO':
        #         new_evidence_list = []
        #
        #         new_claim = self.process_claim(claim)
        #
        #         my_query = QueryParser("sentence_text", StandardAnalyzer()).parse(new_claim)
        #
        #         total_hits = searcher.search(my_query, 15).scoreDocs
        #
        #         for hit in total_hits:
        #             doc = searcher.doc(hit.doc)
        #             for i in range(len(selected_doc[key]["evidence"])):
        #                 if doc.get("page_identifier") == selected_doc[key]["evidence"][i][0] and len(new_evidence_list) < 1:
        #                     new_evidence_list.append([doc.get("page_identifier"), int(doc.get("sentence_number"))])
        #
        #         doc1 = searcher.doc(total_hits[0].doc)
        #         if [doc1.get("page_identifier"), int(doc1.get("sentence_number"))] not in new_evidence_list:
        #             new_evidence_list.append([doc1.get("page_identifier"), int(doc1.get("sentence_number"))])
        #
        #         if len(total_hits) > 2:
        #             doc2 = searcher.doc(total_hits[1].doc)
        #             if total_hits[0].score - total_hits[1].score < 2 and \
        #                     [doc2.get("page_identifier"), int(doc2.get("sentence_number"))] not in new_evidence_list:
        #                 new_evidence_list.append([doc2.get("page_identifier"), int(doc2.get("sentence_number"))])
        #     else:
        #         new_evidence_list = selected_doc[key]['evidence']
        #
        #     pre_list[key] = {}
        #     pre_list[key]['claim'] = claim
        #     pre_list[key]['label'] = label
        #     pre_list[key]['evidence'] = new_evidence_list
        #     print(len(pre_list))
        #
        # reader.close()
        # index_dir.close()
        #
        # print("Start writing...")
        # select_result_path = os.path.join(config.SENT_RETRIEVAL_ROOT, "sent_retrieval_result")
        # doc_tool.mkdir(select_result_path)
        #
        # # doc_tool.dump_json_file(select_result_path, "new_train9_selected_sentence.json", pre_list)
        # doc_tool.dump_json_file(select_result_path, "dev_selected_sentence.json", pre_list)
        # # doc_tool.dump_json_file(select_result_path, "test_selected_sentence.json", pre_list)


if __name__ == '__main__':
    # lucene.initVM()
    # PyLuceneSentRetrieval().index()
    print(len(PyLuceneSentRetrieval().doc()))