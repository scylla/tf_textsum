import argparse
import collections
import csv
import simplejson as json
import codecs
from bs4 import BeautifulSoup
import pickle
import nltk
from nltk.tokenize import sent_tokenize
import re
from collections import namedtuple
from spacy.en import English


MetaData = namedtuple('MetaData', 'id, sentences, stars, funny, cool')

json_dict = {
	"review_id": "encrypted review id",
	"user_id": "encrypted user id",
	"business_id": "encrypted business id",
	"stars": "star rating, rounded to half-stars",
	"date": "date formatted like 2009-12-19",
	"text": "review text",
	"useful": "number of useful votes received",
	"funny": "number of funny votes received",
	"cool": "number of cool review votes received",
	"type": "review"
}

meta_dict = {}
url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
nlp = English()


def create_review_file(json_path, out_path):
	rev_id = 0
	reviews_list = []
	with open(json_path) as fin:
		import sys
		reload(sys)
		sys.setdefaultencoding('utf8')
		for line in fin:
					print "on rview ", rev_id
					line_contents = json.loads(line)
					text = line_contents["text"]
					if bool(re.search('[a-z0-9]', text, re.IGNORECASE)):
						text = BeautifulSoup(text, 'lxml')
					else:
						continue
					clean_text = text.get_text()
					doc = nlp(clean_text)
					# sent_tokenize_list = sent_tokenize(clean_text)
					sent_tokenize_list = [sent.string.strip() for sent in doc.sents]
					num_valid_sent = 0
					valid_sents = []
					for sent in sent_tokenize_list:
						cur_sent = sent.lstrip().rstrip()
						cur_sent = " ".join(cur_sent.split())
						print rev_id, " || ", num_valid_sent, cur_sent
						if bool(re.search('[a-z0-9]', cur_sent, re.IGNORECASE)) and cur_sent:
							urls = re.findall(url_regex, cur_sent)
							if len(urls) == 0:
								valid_sents.append(cur_sent)
								# outfile.write("%s \n" % cur_sent)
								num_valid_sent += 1

					if num_valid_sent > 0:
						# meta_dict[rev_id] = MetaData(rev_id, valid_sents, line_contents[
																		# "stars"], line_contents["funny"], line_contents["cool"])
						reviews_list.append(valid_sents)
						rev_id += 1

					if rev_id % 10000 == 0:
						with codecs.open(out_path + 'sents_data_' + str(rev_id) + '.txt', 'wb', 'utf-8') as outfile:
							for items in reviews_list:
								for item in items:
									outfile.write("%s \n" % item)
						reviews_list = []

					if rev_id == 100000:
						print "process complete"
						break

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description='Convert Yelp Dataset Challenge data from JSON format to CSV.',
	)
	parser.add_argument(
		'json_file',
		type=str,
		help='The json file to convert.',
	)
	parser.add_argument(
		'output_file',
		type=str,
		help='The output file to write to.',
	)
	args = parser.parse_args()
	json_file = args.json_file
	output_file = args.output_file
	create_review_file(json_file, output_file)