## 主要介绍
* https://github.com/ouprince/basic.git
* 本模块主要是为了提供基础的工具包，目前提供的是词库匹配模块
* from basic.tools import WordsMatch

## 安装
* python setup.py install 
* pip install basic

## 卸载
* pip uninstall basic
* 最彻底的方法就是删除安装的egg 文件包

## 使用
```
    from basic.tools import WordsMatch
    datas = [(实体,类型) ... ]
    wm = WordsMatch(datas) | wm = WordsMatch(); wm.wbook = datas
    # supportsFuzzyMatching 表示是否支持模糊匹配
    print(list(wm.matching(待测句子,supportsFuzzyMatching = False)))
    
    # 如果datas 在数据库，支持从数据下载
    from basic.tools import DataBaseOperation
    config = {"user":xxx ..} # 数据库连接信息
    datas = []
    with DataBaseOperation(config) as db:
        for data in db.download('实体表(name,shortname,type)'):
            datas.extend(data.loadData)
```
