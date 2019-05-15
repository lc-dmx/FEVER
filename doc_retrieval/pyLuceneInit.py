#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import nltk
import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import DocIdSetIterator, IndexSearcher, ScoreDoc, TopDocs
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search.similarities import BM25Similarity
from java.nio.file import Paths
import zipfile

import os
from datetime import datetime

from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()
root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")


class PyLuceneDocRetrieval(object):
    def process_doc(self, sentence_text, norm_doc):
        for term in sentence_text:
            term = doc_tool.lemmatize(term.lower())
            if term not in doc_tool.stopwords:
                norm_doc.append(term)

    def process_claim(self, claim):
        """
        tokenize, lower, and lemmatize the claim
        """
        new_claim = []
        for token in nltk.word_tokenize(claim):
            token = re.sub('[\/|\?|\*|\(|\)]', '', token.lower())
            token = doc_tool.lemmatize(token)
            if token not in doc_tool.stopwords:
                new_claim.append(token)

        return " ".join(new_claim)

    def add(self, prev_identifier, sentence_text, ft1, ft2):
        doc = Document()
        doc.add(Field("page_identifier", prev_identifier, ft1))
        doc.add(Field("sentence_text", sentence_text, ft2))
        return doc

    def index(self, wiki_list):
        # if exists doc_retrieval_result, delete and create a new one
        doc_tool.cleardir(root)
        doc_tool.mkdir(root)

        index_dir = FSDirectory.open(Paths.get(root))
        writer_config = IndexWriterConfig(StandardAnalyzer())
        writer_config.setSimilarity(BM25Similarity())
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
                        writer.addDocument(self.add(prev_identifier, " ".join(norm_doc), ft1, ft2))

                        # Start a new document
                        prev_identifier = page_identifier
                        norm_doc.clear()

                        # Prevent the document only has one sentence
                        self.process_doc(sentence_text, norm_doc)

                total_docs += 1
                writer.addDocument(self.add(prev_identifier, " ".join(norm_doc), ft1, ft2))

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

    def select_doc(self, desired_length=-1):
        path = config.TEST_DATA_PATH
        if desired_length == -1:
            data_set = doc_tool.get_data_set(path)
        else:
            data_set = doc_tool.get_new_data_set(path, desired_length)

        if type(data_set) != dict:
            return data_set

        index_dir = FSDirectory.open(Paths.get(root))
        reader = DirectoryReader.open(index_dir)
        searcher = IndexSearcher(reader)
        searcher.setSimilarity(BM25Similarity())

        pre_list = {}
        for key in data_set:
            claim = data_set[key]['claim']
            label = 'SUPPORTS'
            evidence_list = []

            my_query = QueryParser("sentence_text", StandardAnalyzer()).parse(self.process_claim(claim))
            total_hits = searcher.search(my_query, 20).scoreDocs

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
        doc_tool.dump_json_file(config.DOC_RETRIEVAL_ROOT, "testoutput.json", pre_list)
        f = zipfile.ZipFile('testoutput.zip', 'w', zipfile.ZIP_DEFLATED)
        f.write(os.path.join(config.DOC_RETRIEVAL_ROOT, "testoutput.json"))
        f.close()


if __name__ == '__main__':
    lucene.initVM()
    PyLuceneDocRetrieval().index_all_wiki()
    # PyLuceneDocRetrieval().select_doc()

    # query = "Nikolaj Coster-Waldau worked with the Fox Broadcasting Company."
    # PyLuceneDocRetrieval().select_doc(query)
