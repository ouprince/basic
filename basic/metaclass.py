# -*- coding:utf-8 -*-
'''
Author:oyp
Commonly used metaclass
定义元类
'''

class BaseMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        '''2. 创建类 类似 type(name,bases,namespace) '''
        return super().__new__(mcs, name, bases, namespace)
    
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        '''1. 准备名称空间 生成namespace ，所以这里还没有 namespace 参数 '''
        return super().__prepare__(name, bases, **kwargs)
        
    def __init__(cls, name, bases, namespace, **kwargs):
        '''3. 此时已经创建完成，生成 cls'''
        super().__init__(name, bases, namespace)
        
    def __call__(cls, *args, **kwargs):
        '''4. 只有在构建的类生成实例时才会调用 '''
        return super().__call__(*args, **kwargs)
