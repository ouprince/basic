# -*- coding:utf-8 -*-
'''
Author:oyp
Commonly used decorators
'''
import time
import hashlib
import pickle
from functools import wraps

''' 为 WordsMatch 类定制的 distinct 函数修饰器 '''
def distinct(func):
    @wraps(func)
    def wrapped(obj,sentence,supportsFuzzyMatching = False):
        result = func(obj,sentence,supportsFuzzyMatching)
        if supportsFuzzyMatching:
            for x in result:
                x["matching"] = list(set(x["matching"]))
                yield x
    return wrapped
    
''' 为 WordsMatch 类定制的 distinct 类修饰器 '''
def distinct_class(cls):
    class dis_cls(cls):
        # 跟定义一般类方法类似 同样 self,xxx
        def __repr__(self):
            return "<class distinct '%s'>" %cls.__name__
            
        def matching(self,sentence,supportsFuzzyMatching = False):
            result = super(dis_cls,self).matching(sentence,supportsFuzzyMatching)
            for x in result:
                if supportsFuzzyMatching:
                    x["matching"] = list(set(x["matching"]))
                yield x
            
    return dis_cls
    
''' 定义一个缓存修饰器， 修饰一些运算函数，可以在一定时间内保存结果 
    eg: 假设函数 f(a,b) 在有效时间内已经调用过， 那么重新调用 f(a,b) 会直接从缓存获取结果
    duration 自定义缓存有效时间，默认 10 s
'''
def memoize(duration = 10):
    class Memoize(object):
        def __init__(self,func):
            self.func = func
            self.cache = {}
        
        def __call__(self,*args,**kwargs):
            key = self.__compute_key(self.func,args,kwargs)
            # 是否已经在 cache
            if key in self.cache and not self.__is_obsolete(self.cache[key],duration):
                print("we got a winner from cache in last %d senconds" %duration)
                return self.cache[key]['value']
            # 计算
            result = self.func(*args,**kwargs)
            self.cache[key] = {'value':result,'time':time.time()}
            self.cache = {k:v for k,v in self.cache.items() if not self.__is_obsolete(v,duration)}
            return result
            
        def __compute_key(self,func,args,kw):
            key = pickle.dumps((func.__name__,args,kw))
            return hashlib.sha1(key).hexdigest()
        
        def __is_obsolete(self,entry,duration):
            return time.time() - entry['time'] > duration
    return Memoize

''' 实体识别修饰器，去掉不需要的 label '''
def ner_except(except_labels:list = ['O']) -> +1:
    class excp(object):
        def __init__(self,func):
            self.func = func
            
        def __call__(self,*args,**kwargs):
            for res in self.func(*args,**kwargs):
                if res[2] not in except_labels:
                    yield res
    return excp

		
