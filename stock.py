#-*- coding: UTF-8 -*-
#MACRO
USE_API=False
DEVELOP=True
EVERYDAY = False

import logging
from datetime import date
from datetime import time
from datetime import timedelta
logger = logging.getLogger("stock_log")
#formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
file_handler = logging.FileHandler("stock_log.txt",encoding='utf-8')
#file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
class oneday_input:
    today_date = None
    def __init__(self):
        self.total_post = 0
        self.online_peple=[]
        self.raise_post = 0
        self.down_post = 0
        self.all_postheader = []#list,每一项都是字符串，当天的帖子标题
    def get_online_peple(self,online_peple):
        self.online_peple=online_peple
    def get_all_postheader(self,all_postheader):
        self.all_postheader.append(all_postheader)
    def get_today_date(self,today_date):
        self.today_date = today_date
    def compute(self):
#计算total_post
        self.total_post = len(self.all_postheader)
#计算raise_post,down_post看多看空的帖子数
        raise_words = ['涨','多','弹','底','抄','买','牛','加']
        down_words = ['跌','空','顶','卖','水','减','熊','逃','跑']
        self.raise_post=0
        for post_header in self.all_postheader:
            for one_word in raise_words:
                if(one_word in post_header):
                    self.raise_post+=1
            for one_word in down_words:
                if(one_word in post_header):
                    self.down_post+=1
    def __del__(self):
        pass
def date_to_str(date):
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    if(len(month)==1):
        month="0"+month
    if(len(day)==1):
        day = "0"+day
    return year+'-'+month+'-'+day

class oneday_output:
    def __init__(self):
        self.shangzheng=0#百分比
        self.hushen300=0#百分比
        self.chengjiao=0#绝对值
        self.zhongxiaoban=0#百分比
class oneday_result:
    def __init__(self,date):
        import tushare as ts
        self.sh = ts.get_hist_data('sh',start=date_to_str(date),end=(date_to_str(date)),ktype='D')#获取上证指数k线数据，其它参数与个股一致，下同
def get_text_from_url(session,url,host,encoding):
    '''
    '''
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, compress',
            'Accept-Language': 'en-us;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36' }
    session.headers.update(headers)
    r = session.get(url)
    r.encoding = encoding
    return r.text

def str_to_date(date_str):
    '''
    把字符串日期或int日期转变为python date
    '''
    #from datetime import date
    if(type(date_str)==str):
        if(date_str[0:4]=="2015" or date_str[0:4]=='2016'):
            return date(int(date_str[0:4]), month=int(date_str[5:7]), day=int(date_str[8:10]))
        else:
            return None
    else:
        return None

if __name__ == "__main__" and DEVELOP:
    one_day_try = oneday_result(date(year=2016,month=2,day=4))
    print(one_day_try.sh.p_change)
    #url_top = "http://www.newsmth.net/nForum/#!board/Stock"
#登录
    url_list = "http://m.newsmth.net/board/Stock?p="
    host = 'm.newsmth.net'
    total_read_pages = 500
    days_input = [oneday_input()]
    import requests
    session = requests.Session()
    session.post('http://m.newsmth.net/user/login', data={'id':'yigo3000','passwd':'7227510', 'save':'on'})
#只运行一次，用于开发该程序
    for i in range(31,32):#total_read_pages+1):
        temp_posts=[]
        temp_text = get_text_from_url(session,url_list+str(i),host,"utf-8")
        #logger.debug(temp_text)
        #得到标题和日期
        import re
        onepost_patten = re.compile(r'(?P<post_url>/article/.*?(?=">))">(?P<post_header>.*?(?=</a>)).*?(?=<div>)<div>(?P<post_time>.*?)(?=&nbsp)')
        #  .*?  .匹配任意字符，？非贪婪。 <job_infos>正则表达式的关键在于：卡住开头和结尾（固定字符），中间任意（.*?）
        temp_posts += onepost_patten.findall(temp_text)
        if(len(temp_posts)<20):
            logger.debug('page=%s: cant find post!' %i)
        #得到这个页面的所有标题，分配到对应的days_input的item中
        for k in range(len(temp_posts)):#每一个标题计算一次
            temp_date = str_to_date(temp_posts[k][2])#日期取出来
            if(temp_date!=None):
                if(days_input[0].today_date==None):#还没确定今天的日期
                    days_input[0].get_today_date(temp_date)
                    days_input[0].get_all_postheader(temp_posts[0][1])
                else:
                    j=0
                    while(j!=len(days_input)):#看看该归到哪个日期下面
                        if(temp_date==days_input[j].today_date):
                            days_input[j].get_all_postheader(temp_posts[k][1])
                            break
                        else:
                            j+=1
                    if(j==len(days_input)):#如果没有这个日期
                        days_input.append(oneday_input())#增加一个新对象，有新的日期
                        days_input[-1].get_today_date(temp_date)#设置日期
                        days_input[-1].get_all_postheader(temp_posts[k][1])#把帖子标题添加进来
        #time.sleep(2)#避免被封号
        pass
    import pickle
    with open('smth_stock.pkl','wb') as pk:
        pickle.dump(days_input,pk)


if __name__ == "__main__" and EVERYDAY:
    import pickle
    with open('smth_stock.pkl','rb') as pk:
        days_input = pickle.load(pk)
#得到昨天的日期
    yesterday_date = date.today()-timedelta(1)
#登录
    url_list = "http://m.newsmth.net/board/Stock?p="
    host = 'm.newsmth.net'
    total_read_pages = 500
    days_input = [oneday_input()]
    import requests
    session = requests.Session()
    session.post('http://m.newsmth.net/user/login', data={'id':'yigo3000','passwd':'7227510', 'save':'on'})
    not_the_day_wanted_count = 0#不属于我们想要的天
    page_num=1
    while(not_the_day_wanted_count>10):
        temp_posts=[]
        temp_text = get_text_from_url(session,url_list+str(page_num),host,"utf-8")
        #logger.debug(temp_text)
        #得到标题和日期
        import re
        onepost_patten = re.compile(r'(?P<post_url>/article/.*?(?=">))">(?P<post_header>.*?(?=</a>)).*?(?=<div>)<div>(?P<post_time>.*?)(?=&nbsp)')
        #  .*?  .匹配任意字符，？非贪婪。 <job_infos>正则表达式的关键在于：卡住开头和结尾（固定字符），中间任意（.*?）
        temp_posts += onepost_patten.findall(temp_text)
        #得到这个页面的所有标题，分配到对应的days_input的item中

        for i in range(len(temp_posts)):#每一个标题计算一次
            temp_date = str_to_date(temp_posts[i][2])#日期取出来
            if(temp_date!=None):
                if(temp_date!=yesterday_date):#不想要
                    not_the_day_wanted_count+=1
                    pass
                else:
                    j=0
                    if(j==0):#如果没有这个日期
                        days_input.append(oneday_input())#增加一个新对象，有新的日期
                        days_input[-1].get_today_date(temp_date)#设置日期
                        days_input[-1].get_all_postheader(temp_posts[i][1])#把帖子标题添加进来
                        not_the_day_wanted_count=0
                        j+=1
                    else:
                        days_input[-1].get_all_postheader(temp_posts[i][1])#把帖子标题添加进来

        page_num+=1
        time.sleep(3)#避免被封号
#每天运行：
    '''
    import datetime
    while(1):
        now = datetime.datetime.now()
        if(now.minute ==25):#整点时读取主页的“在线人数”等
            temp_text = get_text_from_url(url_list,"http://www.newsmth.net","utf-8")
            datetime.time.sleep(3590)
        else:
            datetime.time.sleep(50)
'''


if __name__ == "__main__" and USE_API:
    import byrapi
    token = 'xxxxx'
    API = byrapi.Byr(token)
    print(API.get_user_info("yigo3000"))
    pass