#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime

from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()
root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_process")
doc_tool.mkdir(root)


class MergeDoc(object):
    def merge_wiki(self, wiki_list):
        prev_identifier = ""
        total_doc = dict()
        for i in range(len(wiki_list)):
            print()
            print("Processing %s..." % wiki_list[i])
            localtime = datetime.now()
            with open(os.path.join(config.WIKI_PAGE_ROOT, wiki_list[i]), 'r', encoding="utf8") as f_input:
                line_number = -1

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
                        total_doc[prev_identifier] = {}

                    if page_identifier == prev_identifier:
                        # This is one document
                        total_doc[prev_identifier][sentence_number] = " ".join(sentence_text)
                    else:
                        # Start a new document
                        prev_identifier = page_identifier

                        # Prevent the document only has one sentence
                        total_doc[prev_identifier] = {}
                        total_doc[prev_identifier][sentence_number] = " ".join(sentence_text)

            localtime2 = datetime.now()
            print('Time: %.2fs' % (localtime2 - localtime).total_seconds())

        print()
        print("Start writing...")
        doc_tool.dump_json_file(root, "total_doc.json", total_doc)

    def start_process(self):
        wiki_list = doc_tool.load_wiki()
        # print(wiki_list)

        print("Start preprocessing the wiki pages...")
        self.merge_wiki(wiki_list)

        print()
        print("Complete all wiki pages!")


if __name__ == '__main__':
    MergeDoc().start_process()
