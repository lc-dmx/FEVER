#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
from whoosh.fields import *
from whoosh.index import create_in, open_dir
from whoosh import qparser
from random import choice

import os
from datetime import datetime

from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()


class DocRetrieval(object):
    def get_schema(self):
        # define page_identifier, sentence_text
        return Schema(page_identifier=TEXT(stored=True), sentence_text=TEXT, path=TEXT(stored=True))

    def norm(self, sentence_text, norm_doc):
        for term in sentence_text:
            term = doc_tool.lemmatize(term.lower())
            if term not in doc_tool.stopwords:
                norm_doc.append(term)

    def init_search_wiki(self, wiki_list):
        root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
        # if exists doc_retrieval_result, delete and create a new one
        doc_tool.cleardir(root)
        doc_tool.mkdir(root)

        # create a schema index, named
        ix = create_in(root, schema=self.get_schema())
        writer = ix.writer()

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
                        self.norm(sentence_text, norm_doc)
                    else:
                        total_docs += 1
                        writer.add_document(page_identifier=prev_identifier, sentence_text=norm_doc, path=wiki_list[i])

                        # Start a new document
                        prev_identifier = page_identifier
                        norm_doc.clear()

                        # Prevent the document only has one sentence
                        self.norm(sentence_text, norm_doc)

                total_docs += 1
                writer.add_document(page_identifier=prev_identifier, sentence_text=norm_doc, path=wiki_list[i])

            localtime2 = datetime.now()
            print(localtime2)
            print('Time: %.2fs' % (localtime2 - localtime).total_seconds())

        print(total_docs)
        writer.commit()

    def index_all_wiki(self):
        wiki_list = doc_tool.load_wiki()
        # print(wiki_list)

        print("Start preprocessing the wiki pages...")
        self.init_search_wiki(wiki_list)

        print()
        print("Complete all wiki pages!")

    def process_claim(self, claim):
        """
        tokenize, lower, and lemmatize the claim
        """
        new_claim = []
        for token in nltk.word_tokenize(claim):
            token = doc_tool.lemmatize(token.lower())
            if token not in doc_tool.stopwords:
                new_claim.append(token)

        return " ".join(new_claim)

    def select_doc(self, desired_length=-1):
        path = config.TEST_DATA_PATH
        if desired_length == -1:
            data_set = doc_tool.get_data_set(path)
        else:
            data_set = doc_tool.get_new_data_set(path, desired_length)

        if type(data_set) != dict:
            return data_set

        root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
        ix = open_dir(root)
        with ix.searcher() as searcher:
            parser = qparser.QueryParser("sentence_text", ix.schema, group=qparser.OrGroup)

            pre_list = {}
            for key in data_set:
                claim = data_set[key]['claim']
                label = 'SUPPORTS'
                evidence_list = []

                myquery = parser.parse(self.process_claim(claim))
                result = searcher.search(myquery, limit=20)
                for res in result:
                    evidence_list.append([res['page_identifier']])
                    # print(res['path'])

                pre_list[key] = {}
                pre_list[key]['claim'] = claim
                pre_list[key]['label'] = label
                pre_list[key]['evidence'] = evidence_list
                print(len(pre_list))

            print("Start writing...")
            doc_tool.dump_json_file(config.DOC_RETRIEVAL_ROOT, "testoutput.json", pre_list)


if __name__ == '__main__':
    # DocRetrieval().index_all_wiki()

    query = "Nikolaj Coster-Waldau worked with the Fox Broadcasting Company."
    DocRetrieval().select_doc(10)
