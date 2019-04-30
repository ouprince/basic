# -*- coding:utf-8 -*-
'''
Author:oyp
Commonly used class
'''
from __future__ import print_function
import sys,os,re,time
import pandas as pd
from .decorators import distinct_class

'''
WordsMatch 类提供实体或公司精确匹配和模糊匹配的功能
wordbook 以列表的形式输入词库
'''
@distinct_class
class WordsMatch(object,metaclass = type):
    '''wordbook 是词库列表'''
    def __init__(self, wordbook:list = None) -> None:
        self.wordbook = wordbook
        self.ByteDf = None
        if wordbook:
            self.__buildByteDataFrame()
    
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type:None,exc_value:None,traceback:None) -> exit:
        if exc_type is not None:
            print("this is an error({})".format(exc_value))
        del self.wordbook
        del self.ByteDf

    def __buildByteDataFrame(self):
        id = []
        word = []
        wordlen = []
        wordorder = []
        word_type = []
        for i,(j,t) in enumerate(self.wordbook):
            if j.isdigit():
                id.append(i)
                word.append(j)
                wordlen.append(1)
                wordorder.append(0)
                word_type.append(t)
            else:
                id.extend([i]*len(j))
                word.extend(list(j))
                wordlen.extend([len(j)]*len(j))
                wordorder.extend(range(len(j)))
                word_type.extend([t]*len(j))
        self.ByteDf = pd.DataFrame({"id":id,"word":word,"wordlen":wordlen,"wordorder":wordorder,"type":word_type})
        self.ByteDf.set_index("word")

    def __deal(self,v):
        result = []
        res = []
        last_wordid = None
        for wordid,word in v:
            if last_wordid is None or wordid == last_wordid + 1:
                res.append(word);last_wordid = wordid
            else:
                if len(res) >= 2:
                    result.append("".join(res));
                res = [word];last_wordid = wordid
        if len(res) >= 2 or len(res[0]) >= 2:
            result.append("".join(res))
        return max(result,key = lambda x:len(x)) if result else None
        
    ''' supportsFuzzyMatching 是否支持模糊匹配 注意模糊匹配可能包含精确匹配的结果 '''
    def matching(self,sentence:str ,supportsFuzzyMatching:bool = False) -> list:
        sentence = sentence.upper()
        digits = re.compile('[0-9]+')
        digits_res = digits.findall(sentence)
        digits_id = [0] * len(digits_res)
        sentence = re.sub('[0-9]+|\.','',sentence)
        assert self.ByteDf is not None,"The WordBook Byte DataFrame is None"
        digits_df = pd.DataFrame({"wordid":digits_id,"word":digits_res})
        sentenceid,sentence = zip(*enumerate(list(sentence)))
        wordDf = pd.DataFrame({"wordid":sentenceid,"word":sentence})
        wordDf = wordDf.append(digits_df)
        wordDf = pd.merge(self.ByteDf,wordDf,how = "inner")
        wordDf.drop_duplicates(subset = ["id","wordorder"],keep = "first",inplace = True) # distinct id,wordorder
        if wordDf.empty:return []
        # 至少大于两个字
        wordCount = wordDf["wordorder"].groupby(wordDf["id"]).count()
        sentenceid,sentence = zip(*wordCount.items())
        wordCount = pd.DataFrame({"id":sentenceid,"count":sentence})
        wordDf = pd.merge(wordDf,wordCount,how = "inner").query("count >= 2") if supportsFuzzyMatching else \
                        pd.merge(wordDf,wordCount,how = "inner").query("count >= wordlen")
                        
        if supportsFuzzyMatching:
            # 定位每个 id 最前的 wordorder,并至少 minorder <= 1
            wordCount = wordDf["wordorder"].groupby(wordDf["id"]).min()
            sentenceid,sentence = zip(*wordCount.items())
            wordCount = pd.DataFrame({"id":sentenceid,"minorder":sentence})
            wordDf = pd.merge(wordDf,wordCount,how = "inner").query("minorder <= 1") # maby minorder < wordlen/2

        dic = dict()
        for id,wordid,word in zip(list(wordDf["id"]),list(wordDf["wordid"]),list(wordDf["word"])):
            if id in dic:dic[id].append([wordid,word])
            else:dic[id] = [[wordid,word]]
        del wordDf
        if not supportsFuzzyMatching:
            dic = {k:self.__deal(sorted(v,key = lambda x:x[0])) for k,v in dic.items() if self.__deal(sorted(v,key = lambda x:x[0])) is not None}
        
        # 将结果按照原文顺序输出
        for k,v in dic.items():
            source = "".join(self.ByteDf.query("id == %d" %k)["word"])
            wtype = list(self.ByteDf.query("id == %d" %k)["type"])[0]
            if not supportsFuzzyMatching:
                if v.find(source) != -1:yield {"ner":source,"type":wtype}
                continue
            last_num = None
            matching = []
            for x in v:
                if last_num is None:
                    last_num = x[0];res = [x[1]]
                elif last_num is not None and x[0] == last_num + 1:
                    last_num = x[0];res.append(x[1])
                else:
                    if source.index(res[0]) <= 1:matching.append("".join(res)) 
                    last_num = x[0];res = [x[1]]
            matching.append("".join(res))
            matching = list(filter(lambda x:len(set(x)&set(source)) >= 2,matching))
            if matching:
                yield {"ner":source,"matching":matching,"type":wtype}
            
    def __repr__(self):
        return "<class 'WordsMatch'>"
        
    def _setWordBook(self,wordbook:list) -> set:
        self.wordbook = wordbook
        if self.wordbook is not None:
            self.__buildByteDataFrame()
            
    def _getWordBook(self):
        return self.wordbook
    
    def _delWordBook(self):
        self.wordbook = None
        self.ByteDf = None
        
    '''元编程模式'''
    wbook = property(fget = _getWordBook, fset = _setWordBook, fdel = _delWordBook, doc = "WordMatch wordbook reset")

''' 实体类 '''
class NER(object):
    def __repr__(self):
        return "NER(name = '%s', shortname = '%s', type = '%s')" %(self.name,self.shortname,self.type)
         
    @property
    def loadData(self):
        res = [(self.name,self.type)]
        if self.shortname is not None:
            [res.append((x,self.type)) for x in self.shortname]
        return res

    @loadData.setter
    def loadData(self,value:tuple):
        self.name = value[0]
        self.shortname = value[1].split(',') if value[1] is not None else None
        self.type = value[2]

import psycopg2
class DataBaseOperation(object):
    def __init__(self,config):
        self.session = psycopg2.connect(**config)
        self.cursor = self.session.cursor()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print("this is an error in ({})".format(exc_value))
        self.close()
    
    def download(self,table):
        ner = NER()
        self.cursor.execute("select * from {}".format(table))
        for data in iter(self.cursor.fetchall()):
            ner.loadData = data
            yield ner
            
    def close(self):
        self.session.close()
        self.cursor.close()
        
if __name__ == "__main__":
    config = {
    "host":"10.128.3.131",
    "port":5432,
    "user":"gfrobot",
    "password":"gfrobot",
    "database":"gfrobot"
    }
    
    datas = []
    with DataBaseOperation(config) as database:
        for data in database.download('conceptual_entity'):
            datas.extend(data.loadData)

    wm = WordsMatch()
    wm.wbook = datas
    t1 = time.time()
    print(list(wm.matching("隆华科技：一季度净利同比增126% 隆华科技(300263)4月18日晚发布一季报，一季度营收为3.53亿元，同比增长59%；净利为2984万元，同比增长126%。")))
    t2 = time.time()
    print("Spend %.3f s" %(t2-t1))


