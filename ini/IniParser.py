import configparser
import os

class IniParser:
    def __init__(self,file):
        cf = configparser.ConfigParser()
        cf.read(os.getcwd() + file, encoding="utf-8")
        try:
            self.vote_url = cf.get('vote','vote_url')
            self.vote_getproxyurl = cf.get('vote','vote_getproxyurl')
            self.vote_number = cf.get('vote', 'vote_number')
            self.vote_p_ashtwo_cn = cf.get('vote', 'vote_p_ashtwo_cn')
        except configparser.NoOptionError:
            print('不能读取配置文件！')
            os.exit(1)
