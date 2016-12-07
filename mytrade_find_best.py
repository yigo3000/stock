#-*- coding: UTF-8 -*-
#运行 mpiexec.exe -np 16 python mytrade_find_best.py
#第一次测试结果显示，一段时间表现最差的中，很少有未来表现好的。
#
#macro
HS300_SUB_RAISE=0.1 #指标：个股涨幅减去沪深300涨幅10%
REBOUND_FROM_LOWEST=0.1
VOLUME_RAISE_FROM_LOWEST=0.5
def get_ultra_plunge(df_start_date,df_end_date):
    '''
    找到跌幅大于PLUNGE_RANGE的,且沪指涨幅减去该股涨幅小于PLUNGE_SUB_HUZHI
    :return: dict{"ticker0":这段时间的涨幅，"ticker":涨幅，...}, 沪指涨幅
    '''
    PLUNGE_RANGE=0.10
    pass

def get_long_one():
    pass

def get_raise_rate_of_one_stock(code,start_date,end_date,ktype="D"):
    import tushare as ts
    df = ts.get_hist_data(code,start=start_date,end=end_date,ktype=ktype)
    if(len(df)>0):
        _price_open=df["open"][len(df)-1]
        _price_close=df["close"][0]
        _raise=(_price_close-_price_open)/_price_open
        _price_lowest=99999
        _volume_close=df["volume"][0]#结束日的成交量
        _volume_lowest=9999999999
        for i in range(len(df)):
            if(df["low"][i]<_price_lowest):
                _price_lowest=df["low"][i]
            if(df["volume"][i]<_volume_lowest):
                _volume_lowest=df["volume"][i]
    else:
        return 0,0,0,0,0,0
    return _raise,_price_open,_price_close,_price_lowest,_volume_close,_volume_lowest

if __name__ == "__main__":
    import mpi4py.MPI as MPI
    comm = MPI.COMM_WORLD
    comm_rank = comm.Get_rank()#my rank()my position)
    comm_size = comm.Get_size()#number of total work items
    import tushare as ts
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

    start_date="2016-08-02"
    end_date="2016-08-17"

    hs300_raise,hs300_open,hs300_close,hs300_lowest,hs300_volume,hs300_volume_lowest=get_raise_rate_of_one_stock("hs300",start_date,end_date)

#step 1: 寻找涨幅最大的股票。这里开始多个线程做不同的工作
    from pandas import *
    result=DataFrame(columns=["code","NAME","raise","open","close"],index=[0])
    num_of_stocks_per_thread=len(yeji_profit)//comm_size +1
    for i in range(0,num_of_stocks_per_thread):
        #if(i==15):
            #print(yeji_profit.iloc[_stock_index,0])
        _stock_index=comm_rank*num_of_stocks_per_thread+i
        if(_stock_index>=len(yeji_profit)):
            break
        tmp_raise,tmp_open,tmp_close,tmp_lowest,tmp_volume,tmp_volume_lowest=get_raise_rate_of_one_stock(yeji_profit.iloc[_stock_index,0],start_date,end_date)
        #if hs300_raise-tmp_raise>HS300_SUB_RAISE:
        #if hs300_raise-tmp_raise>HS300_SUB_RAISE and (tmp_close-tmp_lowest)/tmp_lowest<0.05:#找到跌幅比沪深300多10%，且从最低点反弹小于5%的
        #if hs300_raise-tmp_raise>HS300_SUB_RAISE and (tmp_close-tmp_lowest)/tmp_lowest<0.10 and tmp_raise>-0.20:#找到跌幅比沪深300多10%，且从最低点反弹小于5%的
        if tmp_raise-hs300_raise>HS300_SUB_RAISE and (tmp_close-tmp_lowest)/tmp_lowest>REBOUND_FROM_LOWEST and tmp_raise>0.10 and (tmp_volume-tmp_volume_lowest)/tmp_volume_lowest>VOLUME_RAISE_FROM_LOWEST:#找到跌幅比沪深300多10%，且从最低点反弹小于5%的
            result.ix[_stock_index]=Series([yeji_profit.iloc[_stock_index,0],yeji_profit.iloc[_stock_index,1],tmp_raise,tmp_open,tmp_close],index=result.columns)

        #result.ix[len(result)]=Series([yeji_profit.iloc[i,0],yeji_profit.iloc[i,1],tmp_raise,tmp_open,tmp_close],index=result.columns)
        #print(i)


#各个线程把结果发给rank0，由rank0合并、输出结果
    if(comm_rank!=0):
        comm.send(result.drop(0),dest=0)
    else:
        for i in range(comm_size-1):
            result=concat([result, comm.recv(source=i + 1)])
        print(result.drop(0))
    print("process %s finished." %comm_rank)
    result.to_csv("result.csv")
    #print(result)


#把时间跨度设为一个月的记录: 只搜低估10%，会搜出很多（以2016年6月1日至30日为例，找到153个）。
#增加条件：从最低点反弹不超过5%，得到的几乎全都是分红股
#增加条件:(tmp_close-tmp_lowest)/tmp_lowest<0.10 and tmp_raise>-0.20,得到的大部分ok，不行的股：300083，002496
#测试从3月15到4月15（上涨，之后从4月16大盘开始暴跌），得出结论：大盘跌，几乎不能找到赚钱的个股。

#增加条件：成交量缩减