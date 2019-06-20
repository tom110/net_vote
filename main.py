from urllib import request
import json
from ini.IniParser import IniParser

iniParser = IniParser("/ini/config.ini")
vote_url=iniParser.vote_url

def gorequest(request):
    global count
    data = ""
    res=0
    try:
        response = request.urlopen(req, timeout=4)
        data = json.loads(response.read().decode("utf-8"))
        res=data["result"]
    except:
        print(proxy + "失效")
        return 0


    if res == 0:
        print(proxy + "达到投票上限")
        return 0
    elif res==1:
        count = count + 1
        print(proxy + "成功1票")
        gorequest(request)
    else:
        print(proxy+"未知错误");

result = []
with open('proxys.txt', 'r') as f:
    for line in f:
        result.append(line.strip('\n'))
print(result)

count=0

for proxy in result:
    proxy_host = proxy  # host and port of your proxy
    url = vote_url

    req = request.Request(url)
    req.set_proxy(proxy_host, 'http')

    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36")

    if(gorequest(request)==0):
        continue

print("一共投票成功"+str(count)+"票")

