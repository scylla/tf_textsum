"""Example of Converting TextSum model data.
Usage:
python data_convert_example.py --command binary_to_text --in_file data/data --out_file data/text_data
python data_convert_example.py --command text_to_binary --in_file data/text_data --out_file data/binary_data
python data_convert_example.py --command binary_to_text --in_file data/binary_data --out_file data/text_data2
diff data/text_data2 data/text_data
"""

import struct
import sys
import nltk
import codecs
import os
import pickle

import tensorflow as tf
from tensorflow.core.example import example_pb2

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('command', 'binary_to_text',
                           'Either binary_to_text or text_to_binary.'
                           'Specify FLAGS.in_file accordingly.')
tf.app.flags.DEFINE_string('in_file', ' ', 'path to file')
tf.app.flags.DEFINE_string('out_file', ' ', 'path to file')
tf.app.flags.DEFINE_string('suffix', 'dev', 'suffix for data file')



class CorpusNode(object):
    def __init__(self):
        self.summ_data = []
        self.sentence_data = []
        self.summ_amrs = []
        self.sentence_amrs = []
        self.sentence_alignments = []
        self.summ_alignments = []
        self.sentence_pos = []
        self.summ_pos = []
    def appendSummText(self, data):
        self.summ_data.append(data)
    def appendSentenceText(self, data):
        self.sentence_data.append(data)
    def appendSummAmr(self, data):
        self.summ_amrs.append(data)
    def appendSentenceAmr(self, data):
        self.sentence_amrs.append(data)
    def appendSentenceAlignments(self, data):
        self.sentence_alignments.append(data)
    def appendSummAlignments(self, data):
        self.summ_alignments.append(data)
    def appendSentencePOS(self, data):
        self.sentence_pos.append(data)
    def appendSummPOS(self, data):
        self.summ_pos.append(data)

def _binary_to_text():
  reader = open(FLAGS.in_file, 'rb')
  writer = open(FLAGS.out_file, 'w')
  while True:
    len_bytes = reader.read(8)
    if not len_bytes:
      sys.stderr.write('Done reading\n')
      return
    str_len = struct.unpack('q', len_bytes)[0]
    tf_example_str = struct.unpack('%ds' % str_len, reader.read(str_len))[0]
    tf_example = example_pb2.Example.FromString(tf_example_str)
    examples = []
    for key in tf_example.features.feature:
      examples.append('%s=%s' % (key, tf_example.features.feature[key].bytes_list.value[0]))
    writer.write('%s\n' % '\t'.join(examples))
  reader.close()
  writer.close()


def _text_to_binary():
  inputs = open(FLAGS.in_file, 'r').readlines()
  writer = open(FLAGS.out_file, 'wb')
  for inp in inputs:
    tf_example = example_pb2.Example()
    for feature in inp.strip().split('\t'):
      (k, v) = feature.split('=')
      tf_example.features.feature[k].bytes_list.value.extend([v])
    tf_example_str = tf_example.SerializeToString()
    str_len = len(tf_example_str)
    writer.write(struct.pack('q', str_len))
    writer.write(struct.pack('%ds' % str_len, tf_example_str))
  writer.close()

def _text_to_pos():
  import sys
  reload(sys)
  sys.setdefaultencoding('utf8')
  inputs = open(FLAGS.in_file, 'r').readlines()
  writer = open(FLAGS.out_file, 'w')
  for inp in inputs:
    tokens = nltk.word_tokenize(inp)
    tagged = nltk.pos_tag(tokens)
    str_out = " ".join(item[1] for item in tagged)
    writer.write(str_out + '\n')
  writer.close()

def main(unused_argv):
  # assert FLAGS.command and FLAGS.in_file and FLAGS.out_file
  if FLAGS.command == 'binary_to_text':
    _binary_to_text()
  elif FLAGS.command == 'text_to_binary':
    _text_to_binary()
  elif FLAGS.command == 'text_to_pos':
    _text_to_pos()
  elif FLAGS.command == 'pkl_to_txtsum':
    prepareTextSumData(FLAGS.suffix)
  elif FLAGS.command == 'prepare_vocab':
    prepareVocab(FLAGS.suffix)

def prepareTextSumData(suffix_str):

  dir_suff = "/home/amitn/Documents/m-tech-thesis/code/semantic_summ/src/fei/mixed_all/"
  data_dir = "/home/amitn/Documents/m-tech-thesis/code/seq2graph-master/amr2seq/data_prep/run_dir/"
  output_dir = "amr_seqs/"

  filehandler = open(dir_suff + "amr_meta_data" + suffix_str + ".pkl","rb")

  corpus_dict = pickle.load(filehandler)
  filehandler.close()

  with codecs.open(output_dir + suffix_str + "_txtsum", "w", "utf-8") as output_file:
    with codecs.open(data_dir + "summ_" + suffix_str + "_amrseq", 'r', 'utf-8') as summ_file:
      with codecs.open(data_dir + "sent_" + suffix_str + "_amrseq", "r", "utf-8") as sent_file:
        for x,v in corpus_dict.iteritems():
          num_summs = len(v.summ_amrs)
          num_sents = len(v.sentence_amrs)
          print num_summs, num_sents

          if num_summs == 0:
            for _ in xrange(num_sents):
              sent_file.readline()
            continue

          output_file.write("abstract= <d> <p> ")
          for _ in xrange(num_summs):
            line_summ = summ_file.readline()
            output_file.write("<s> %s </s> " % line_summ.rstrip().lstrip())
          output_file.write("</p> </d>\tarticle= <d> <p> ")
          for _ in xrange(num_sents):
            line_sent = sent_file.readline()
            output_file.write("<s> %s </s> " % line_sent.rstrip().lstrip())
          output_file.write("</p> </d> \n")


def prepareVocab(suffix_str):

  from collections import Counter

  with open("amr_seqs/train_txtsum") as train_data, open("amr_seqs/dev_txtsum") as dev_data, open("data/vocab_" + suffix_str, 'w') as v:
    all_data = train_data.read().split()
    all_data = all_data + dev_data.read().split()
    wordcount = Counter(all_data)
    wordcount = wordcount.most_common(5000)
    print len(wordcount)
    for item in wordcount:
      print >>v, ("{} {}".format(*item))



if __name__ == '__main__':
  tf.app.run()
