#-*- coding: UTF-8 -*-
#macro
HS300_SUB_RAISE=0.1 #指标：沪深300涨幅减去个股涨幅大于10%


def get_ultra_plunge(df_start_date,df_end_date):
    '''
    找到跌幅大于PLUNGE_RANGE的,且沪指涨幅减去该股涨幅小于PLUNGE_SUB_HUZHI
    :return: dict{"ticker0":这段时间的涨幅，"ticker":涨幅，...}, 沪指涨幅
    '''
    PLUNGE_RANGE=0.10
    pass

def get_long_one():
    pass

def get_hs300(start_date,end_date,ktype="D"):
    '''
    获得一段时间的沪深300增长比例，开盘价，收盘价
    :param start_date:
    :param end_date:
    :param ktype:
    :return:
    '''
    import tushare as ts
    df_end_date = ts.get_hist_data("hs300",start=start_date,end=end_date,ktype=ktype)
    price_open=df_end_date["open"][-1]
    price_close=df_end_date["close"][0]
    hs300_raise=(price_close-price_open)/price_open
    return hs300_raise,price_open,price_close

def get_raise_rate_of_one_stock(code,start_date,end_date,ktype="D"):
    import tushare as ts
    df = ts.get_hist_data(code,start=start_date,end=end_date,ktype=ktype)
    if(len(df)>0):
        _price_open=df["open"][len(df)-1]
        _price_close=df["close"][0]
        _raise=(_price_close-_price_open)/_price_open
    else:
        return 0,0,0
    return _raise,_price_open,_price_close

if __name__ == "__main__":
    import tushare as ts
    #history_sh = ts.get_hist_data('sh',start=date_to_str(date),end=(date_to_str(date)),ktype='D')#获取上证指数k线数据，其它参数与个股一致，下同
    #qdpj = ts.get_hist_data('600600',start='2008-01-05',end='2014-01-05',ktype='D')
    #qdpj.to_excel(r'c:/Users/yu/Documents/dayb600600.xlsx')

    import pickle
    '''
    yejis=ts.get_report_data(2016,1)#获取业绩报表
    with open('yejis.pkl',"wb") as f:
        pickle.dump(yejis,f)'''
    with open('yejis.pkl','rb') as f:#从文件获取业绩报表
        yejis = pickle.load(f)

    yejis_sort=yejis.sort(columns="eps")#按照eps列由小到大排序
    #print(yejis_sort)
    index_of_profitable=0
    for i in range(len(yejis_sort)):#找到eps（每股收益）是正值的点
        tmp=yejis_sort.iloc[i,2]
        if(yejis_sort.iloc[i,2]>0):
            index_of_profitable=i
            break
    #删除不盈利的
    yeji_profit=yejis_sort[index_of_profitable:]

    start_date="2016-08-01"
    end_date="2016-08-10"

    hs300_raise,hs300_open,hs300_close=get_raise_rate_of_one_stock("hs300",start_date,end_date)

    result_raise,result_open,result_close,result_code=[],[],[],[]
    for i in range(len(yeji_profit)):
        if(i==15):
            print(yeji_profit.iloc[i,0])
        tmp_raise,tmp_open,tmp_close=get_raise_rate_of_one_stock(yeji_profit.iloc[i,0],start_date,end_date)
        if hs300_raise-tmp_raise>HS300_SUB_RAISE:
            result_raise.append(tmp_raise)
            result_open.append(tmp_open)
            result_close.append(tmp_close)
            result_code.append(yeji_profit.iloc[i,0])#stock_condes.index[i]


        print(i)
#get_ultra_plunge(df_start_date,df_end_date)
    print(result_code)



