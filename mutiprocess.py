# -*- coding: UTF-8 -*-
from multiprocessing import Process, Queue
import multiprocessing
import os, time
from urllib import request
import json
import re
from ini.IniParser import IniParser

iniParser = IniParser("/ini/config.ini")
vote_url=iniParser.vote_url
vote_getproxyurl=iniParser.vote_getproxyurl
vote_number=int(iniParser.vote_number)

# 单条返回函数
def getproxy():
    url=vote_getproxyurl
    req = request.Request(url)
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36")
    try:
        response = request.urlopen(req, timeout=10)
        return response.read().decode("utf-8")
    except:
        print( "proxy获取失败")
        return ""

# 免费http://p.ashtwo.cn返回函数
def getfreeproxy():
    url="http://p.ashtwo.cn"
    req = request.Request(url)
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36")
    try:
        response = request.urlopen(req, timeout=10)
        reResult= re.findall(r'(?:(?:[0,1]?\d?\d|2[0-4]\d|25[0-5])\.){3}(?:[0,1]?\d?\d|2[0-4]\d|25[0-5]):\d{0,5}',response.read().decode("utf-8"))
        return reResult[0]
    except:
        print("proxy获取失败")
        return ""

# 递归访问投票
def gorequest(req,proxy,i,count):
    res=0
    try:
        if count.value >= vote_number:
            print('投票任务完成，%d进程停止运行' % i)
            kill(os.getpid())
        else:
            response = request.urlopen(req, timeout=10)
            data = json.loads(response.read().decode("utf-8"))
            res=data["result"]
    except:
        print("进程%d:%s失效" % (i,proxy))
        pass

    if res == 0:
        print("进程%d,%s达到投票上限" % (i,proxy))
        pass
    elif res==1:
        count.value = count.value + 1
        print("进程%d号，代理%s成功投票,累记投票%d张" % (i,proxy,count.value))
        gorequest(req,proxy,i,count)
    else:
        print(proxy+"未知错误")
        pass

# 处理消费事件
def exec(proxy,i,count):
    url = vote_url

    req = request.Request(url)
    req.set_proxy(proxy, 'http')

    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36")

    gorequest(req,proxy,i,count)

# 写数据进程执行的代码:
def write(q):
    print('进程%s开始写入代理池' % os.getpid())
    while True:
        if q.qsize()>10:
            time.sleep(5)
            print('队列过长，代理线程池停止5秒')
        else:
            proxy=getfreeproxy()
            print('代理地址%s写入代理池' % proxy)
            q.put(proxy)
            time.sleep(0.5)

# 读数据进程执行的代码:
def read(q,i,count):
    print('进程%s加入投票序列，进程编号%d' % (os.getpid(),i))
    while True:
        value = q.get(True)
        exec(value,i,count)

# 停止进程
def kill(pid):
    # 本函数用于中止传入pid所对应的进程
    if os.name == 'nt':
        # Windows系统
        cmd = 'taskkill /pid ' + str(pid) + ' /f'
        try:
            os.system(cmd)
            # print('%s进程已被停止'% pid)
        except Exception as e:
            print(e)
    elif os.name == 'posix':
        # Linux系统
        cmd = 'kill ' + str(pid)
        try:
            os.system(cmd)
            # print('%s进程已被停止' % pid)
        except Exception as e:
            print(e)
    else:
        print('Undefined os.name')


if __name__=='__main__':
    count=multiprocessing.Value("d",0)
    # 父进程创建Queue，并传给各个子进程：
    q = Queue()
    pw = Process(target=write, args=(q,))
    pw.start()

    for i in range(11):
        pr=Process(target=read,args=(q,i,count))
        pr.start()

    pw.join()
    pw.close()