# -*- coding:utf-8 -*-
'''
Author:oyp
Commonly used functions
'''
from __future__ import print_function
import jieba
from .decorators import ner_except

'''编辑距离函数'''
def edit_distance(str1,str2):
    matrix = [[i+j for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]
    for i in range(1,len(str1)+1):
        for j in range(1,len(str2)+1):
            d = 0 if str1[i-1] == str2[j-1] else 1
            matrix[i][j] = min(matrix[i-1][j]+1,matrix[i][j-1]+1,matrix[i-1][j-1]+d)
    return matrix[len(str1)][len(str2)]

'''精确切割函数'''
def finesegment(sentence):
    res = jieba.lcut(sentence,cut_all = True)
    res_sort = sorted(res,key = lambda x:len(x))
    cut_res = []
    for x in res_sort:
        if x in sentence:sentence = sentence.strip(x);cut_res.append(x)
    cut_res.sort(key = lambda x:res.index(x))
    return cut_res
    
'''连续标记法 '''
@ner_except()
def con_marking(labels:list) -> +1:
    if not isinstance(labels,(list,tuple)):
        raise TypeError("labels is not list")
    last_label = None
    for i,label in enumerate(labels):
        if last_label is None:
            start = i;last_label = label
        elif label != last_label:
            yield(start,i,last_label);last_label = label;start = i
    else:
        yield(start,len(labels),label)
        
''' BIO 表示法 '''
def bio_marking(labels:list) -> +1:
    if not isinstance(labels,(list,tuple)):
        raise TypeError("labels is not list")
    last_label = None
    for i,label in enumerate(labels):
        if last_label is None and label.startswith('B'):
            start = i;last_label = label[2:]
        elif last_label is not None and label.startswith('B'):
            if last_label:yield(start,i,last_label)
            start = i;last_label = label[2:]
        elif last_label is not None and label[2:] != last_label:
            if last_label:yield(start,i,last_label)
            start = i;last_label = label[2:]
    else:
        if last_label:yield(start,i+1,last_label)
    
if __name__ == "__main__":
    pass

