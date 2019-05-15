#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pickle
import nltk
from nltk.corpus import stopwords

import config


class DocRetrievalTool(object):
    """
    doc retrieval tool
    """
    def __init__(self):
        self.lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english'))

    def lemmatize(self, word):
        """
        Get the lemmatized word
        :param word:
        :return: lemmatized word
        """
        lemma = self.lemmatizer.lemmatize(word, 'v')
        if lemma == word:
            lemma = self.lemmatizer.lemmatize(word, 'n')
        return lemma

    def cleardir(self, top):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def mkdir(self, path):
        """
        If the path doesn't exist, then create
        """
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)

    def dump_json_file(self, root, file_name, content):
        f_output = open(os.path.join(root, file_name), 'w')
        json.dump(content, f_output)
        f_output.close()

    def dump_pickle_file(self, root, file_name, content):
        f_output = open(os.path.join(root, file_name), 'wb')
        pickle.dump(content, f_output)
        f_output.close()

    def load_json_file(self, root, file_name):
        f_input = open(os.path.join(root, file_name), 'r')
        content = json.load(f_input)
        f_input.close()
        return content

    def load_pickle_file(self, root, file_name):
        f_input = open(os.path.join(root, file_name), 'rb')
        content = pickle.load(f_input)
        f_input.close()
        return content

    def load_wiki(self):
        """
        Load wiki file
        :return: wiki file name list
        """
        dir_exist = os.path.exists(config.WIKI_PAGE_ROOT)
        if not dir_exist:
            return "Wiki pages directory doesn't exist."
        else:
            wiki_list = []
            for filename in os.listdir(config.WIKI_PAGE_ROOT):
                wiki_list.append(filename)
            return wiki_list

    def get_data_set(self, path):
        """
        Get the dataset
        :return: if file exists, return data_set as a dict object;
                    otherwise, report file doesn't exist
        """
        file_exist = os.path.isfile(path)
        if not file_exist:
            return "This file doesn't exist."
        else:
            with open(path, 'r') as f:
                data_set = json.load(f)
                return data_set

    def get_new_data_set(self, path, desired_length):
        """
        Get the new train dataset of the specified length
        :return: new_train_set as a dict object
        """
        data_set = self.get_data_set(path)
        if type(data_set) != dict:
            return data_set

        if desired_length is None:
            return "You should indicate the length of train file you want to get first."

        number = 1
        new_data_set = {}
        for key in data_set:
            new_data_set[key] = data_set[key]
            number += 1

            if number > desired_length:
                return new_data_set


if __name__ == '__main__':
    a = dict()
    a[1] = 1
    a[2] = 2
    doc_tool = DocRetrievalTool()
    root = os.path.join(config.DOC_RETRIEVAL_ROOT, "doc_retrieval_result")
    file_name = "1.json"
    doc_tool.dump_json_file(root, file_name, a)
    file_name = "1"
    doc_tool.dump_pickle_file(root, file_name, a)
