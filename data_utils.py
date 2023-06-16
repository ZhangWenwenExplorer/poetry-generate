#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import numpy as np
import mxnet as mx
from mxnet import nd
from mxnet import gluon as g


class TextConverter(object):
    def __init__(self, text_path, max_vocab=5000):
        with codecs.open(text_path, mode='r', encoding='utf-8') as f:
            text_file = f.readlines()
        word_list = [v for s in text_file for v in s]
        vocab = set(word_list)
        # 如果单词超过最长限制，则按单词出现频率去掉最小的部分
        vocab_count = {}
        for word in vocab:
            vocab_count[word] = 0
        for word in word_list:
            vocab_count[word] += 1
        vocab_count_list = []
        for word in vocab_count:
            vocab_count_list.append((word, vocab_count[word]))
        vocab_count_list.sort(key=lambda x: x[1], reverse=True)
        if len(vocab_count_list) > max_vocab:
            vocab_count_list = vocab_count_list[:max_vocab]
        vocab = [x[0] for x in vocab_count_list]
        self.vocab = vocab

        self.word_to_int_table = {c: i for i, c in enumerate(self.vocab)}
        self.int_to_word_table = dict(enumerate(self.vocab))

    @property
    def vocab_size(self):
        return len(self.vocab) + 1

    def word_to_int(self, word):
        if word in self.word_to_int_table:
            return self.word_to_int_table[word]
        else:
            return len(self.vocab)

    def int_to_word(self, index):
        if index == len(self.vocab):
            return '<unk>'
        elif index < len(self.vocab):
            return self.int_to_word_table[index]
        else:
            raise Exception('Unknow index!')

    def text_to_arr(self, text):
        arr = []
        for word in text:
            arr.append(self.word_to_int(word))
        return np.array(arr)

    def arr_to_text(self, arr):
        words = []
        for index in arr:
            words.append(self.int_to_word(index))
        return "".join(words)


class TextData(g.data.Dataset):
    def __init__(self, text_path, n_step, arr_to_idx):
        self.n_step = n_step

        with codecs.open(text_path, mode='r', encoding='utf-8') as f:
            data = f.readlines()
        text = [v for s in data for v in s]
        num_seq = int(len(text) / n_step)
        self.num_seq = num_seq
        text = text[:num_seq * n_step]  # 截去最后不够长的部分
        arr = arr_to_idx(text)
        arr = arr.reshape((num_seq, -1))
        self.arr = arr

    def __getitem__(self, index):
        x = self.arr[index, :]
        y = np.zeros(x.shape)
        y[:-1], y[-1] = x[1:], x[0]
        return nd.array(x), nd.array(y)

    def __len__(self):
        return self.num_seq
