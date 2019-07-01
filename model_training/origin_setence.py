"""
get original sentence according to page identifier and sentence number
"""

import os
from collections import defaultdict
from util.doc_util import DocRetrievalTool
import config

doc_tool = DocRetrievalTool()


class OriginSentence(object):
    def get_origin_sent(self):
        path = os.path.join(config.SENT_RETRIEVAL_ROOT, "sent_retrieval_result", "dev.json")

        data_set = doc_tool.get_data_set(path)
        if type(data_set) != dict:
            return data_set

        file_path = os.path.join(config.SENT_RETRIEVAL_ROOT, "merge_doc")
        file_list = os.listdir(file_path)
        docs = defaultdict(dict)
        i = 0
        for file in file_list:
            docs[i] = doc_tool.load_json_file(file_path, file)
            i += 1

        pre_list = {}
        for key in data_set:
            claim = data_set[key]['claim']
            label = data_set[key]['label']
            evidence_list = data_set[key]['evidence']

            new_evidence = []
            for evidence in evidence_list:
                page = evidence[0]
                number = evidence[1]
                for j in range(i):
                    if page in docs[j]:
                        sentence_text = docs[j][page][str(number)]
                        new_evidence.append([page, number, sentence_text])

            pre_list[key] = {}
            pre_list[key]['claim'] = claim
            pre_list[key]['label'] = label
            pre_list[key]['evidence'] = new_evidence

            print(len(pre_list))

        path = os.path.join(config.MODEL_TRAINING_ROOT, "origin_sentence")
        doc_tool.mkdir(path)

        # doc_tool.dump_json_file(path, "train_origin_sentence.json", pre_list)
        doc_tool.dump_json_file(path, "dev.json", pre_list)
        # doc_tool.dump_json_file(path, "test.json", pre_list)


if __name__ == '__main__':
    OriginSentence().get_origin_sent()


