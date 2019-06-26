# -*- coding: UTF-8 -*-
from multiprocessing import Process, Queue
import multiprocessing
import os, time,sys,getopt
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
    url=iniParser.vote_p_ashtwo_cn
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
        return

    if res == 0:
        print("进程%d,%s达到投票上限" % (i,proxy))
        return
    elif res==1:
        count.value = count.value + 1
        print("进程%d号，代理%s成功投票,累记投票%d张" % (i,proxy,count.value))
        gorequest(req,proxy,i,count)
    else:
        print(proxy+"未知错误")
        return

# 处理消费事件
def exec(proxy,i,count):
    url = vote_url

    req = request.Request(url)
    req.set_proxy(proxy, 'http')

    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")

    gorequest(req,proxy,i,count)

# 写数据进程执行的代码:
def write_freeproxy(q):
    print('免费代理进程%s开始写入代理池' % os.getpid())
    while True:
        len=q.qsize()
        if len>10:
            time.sleep(5)
            print('队列过长，代理线程池停止5秒')
        else:
            proxy=getfreeproxy()
            print('免费代理地址%s写入代理池,当前线程池长度%d' % (proxy,len))
            q.put(proxy)
            time.sleep(0.5)

def write_daxiang(q):
    print('大象代理写入进程%s开始写入代理池' % os.getpid())
    while True:
        len = q.qsize()
        if len > 10:
            time.sleep(5)
            print('队列过长，代理线程池停止5秒')
        else:
            proxy = getproxy()
            print('大象代理地址%s写入代理池,当前线程池长度%d' % (proxy, len))
            q.put(proxy)
            time.sleep(0.5)


def write_proxys(q):
    print('代理文件写入进程%s开始写入代理池' % os.getpid())
    result=[]
    with open('proxys.txt', 'r') as f:
        for line in f:
            result.append(line.strip('\n'))
    for proxy in result:
        q.put(proxy)
        print('文件代理地址%s写入代理池' % proxy)



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


def main(argv):
    write_file_proxys_bool=False
    write_free_proxys_number=0
    write_daxiang_proxys_number=0
    read_proxys_number=0
    try:
        opts, args = getopt.getopt(argv, "hf:e:d:r:", ["isusefileproxy=", "freeproxynumber=","daxiangproxynumber","readproxynumber"])
    except getopt.GetoptError:
        print('mutiprocess.py -f <isusefileproxy>[False,True] -e <freeproxynumber>[int] -d <daxiangproxynumber>[int] -r <readproxynumber>[int]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'mutiprocess.py -f <isusefileproxy>[False,True] -e <freeproxynumber>[int] -d <daxiangproxynumber>[int] -r <readproxynumber>[int]')
            sys.exit()
        elif opt in ("-f", "--isusefileproxy"):
            write_file_proxys_bool = arg
        elif opt in ("-e", "--freeproxynumber"):
            write_free_proxys_number = arg
        elif opt in ("-d", "--daxiangproxynumber"):
            write_daxiang_proxys_number = arg
        elif opt in ("-r", "--readproxynumber"):
            read_proxys_number = arg
    print('使用文件袋里：', write_file_proxys_bool)
    print('免费代理进程数：', write_free_proxys_number)
    print('大象类代理进程数：', write_daxiang_proxys_number)
    print('读取代理进程数：', read_proxys_number)


    count = multiprocessing.Value("d", 0)
    # 父进程创建Queue，并传给各个子进程：
    q = Queue()

    if write_file_proxys_bool:
        # 开启一条文件写入进程
        for i in range(1):
            pw = Process(target=write_proxys, args=(q,))
            pw.start()

    # 开启三个免费写入进程
    for i in range(int(write_free_proxys_number)):
        pw = Process(target=write_freeproxy, args=(q,))
        pw.start()

    # 开启一个单条大象代理写入进程
    for i in range(int(write_daxiang_proxys_number)):
        pw=Process(target=write_daxiang,args=(q,))
        pw.start()

    for i in range(int(read_proxys_number)):
        pr = Process(target=read, args=(q, i, count))
        pr.start()

    pw.join()
    pw.close()

if __name__=='__main__':
    main(sys.argv[1:])
