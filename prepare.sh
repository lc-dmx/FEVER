#!/bin/bash
"""
create file folders
"""

# check data folder exists or not
if [ ! -d "data" ]; then
	echo "You need download data first!"

# check dev_package folder exists or not
if [ ! -d "dev_package" ]; then
	mkdir dev_package

# check doc_retrieval folder exists or not
if [ ! -d "doc_retrieval" ]; then
	mkdir doc_retrieval

# check model_training folder exists or not
if [ ! -d "model_training" ]; then
	mkdir model_training

# check sentence_retrieval folder exists or not
if [ ! -d "sentence_retrieval" ]; then
	mkdir sentence_retrieval

# check util folder exists or not
if [ ! -d "util" ]; then
	mkdir util


# Start stanford corenlp server
echo "Start downloading stanford corenlp file"
cd dev_package
wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip
unzip stanford-corenlp-full-2018-10-05.zip
cd stanford-corenlp-full-2018-10-05
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer status_port 9000 -port 9000 -timeout 15000