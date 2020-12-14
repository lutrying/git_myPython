import datetime
import tushare as ts
import pymysql
import baostock as bs
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal   #滤波等
import matplotlib.dates as mdates    #處理日期
import mpl_finance as mpf
from matplotlib.pylab import date2num
import matplotlib.ticker as ticker
from sympy import *
import os
from kLine import *
from getStockInfo import *
import configparser
from apscheduler.schedulers.blocking import BlockingScheduler#定时运行
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor#线程池
import threading

def stockList(fileName):
    filePath='G:\\stockData\\'
    print(fileName+' :start')
    try:
        df=pd.read_csv(filePath+fileName+'.csv')#00开头丢失   ,converters = {u'code':str}        
    except Exception as err:
        print('read_csv err', err)
    # stockList=df['code'].str[1:]#截取字符串
    if 'ts_code' in list(df):
        df=df.rename(columns={'ts_code': 'code'})
    df['code']=df['code'].str.extract('(\d+)')#正则表达式截取数字
    stockList=df['code']
    ret=list(stockList)
    return ret

def indexList():
    print('index start')
    return ['399006_cyb','000001_sh','399001_sz']
def everydayList(fileName):
    print('everyList start')
    filePath='G:\\stockData\\everydayOp\\'
    print(fileName+' :start')
    try:
        df=pd.read_csv(filePath+fileName+'.csv')#00开头丢失   ,converters = {u'code':str}        
    except Exception as err:
        print('read_csv err', err)
    # stockList=df['code'].str[1:]#截取字符串
    if 'ts_code' in list(df):
        df=df.rename(columns={'ts_code': 'code'})
    df['code']=df[(df['buy_sellNum']!=0)|(df['holdNum']!=0)]['code']
    df=df.drop_duplicates(['code'])
    df['code']=df['code'].str.extract('(\d+)')#正则表达式截取数字
    stockList=df['code']
    ret=list(stockList)
    return ret

#选股,从沪深300和中证500选吧
def selectStocks(stockList,startDate,endDate,isShow):  
    start0 =  time.perf_counter()
    length=len(stockList)
    filePath1='G:\\stockData\\originData\\'
    # filePath1='G:\\stockData\\'
#建回测时间序列开始
    ts.set_token('19cf1077f3823655b388a7b92ef066a406293ae2ed656dfb2a524cd9')
    pro = ts.pro_api()
    # year = 2018
    date_seq_start = startDate
    date_seq_end = endDate
    # backTraceDate='2019-01-01'
    back_test_date_start = (datetime.datetime.strptime(date_seq_start, '%Y-%m-%d')).strftime('%Y%m%d')
    back_test_date_end = (datetime.datetime.strptime(date_seq_end, "%Y-%m-%d")).strftime('%Y%m%d')
    # df = pro.trade_cal(exchange_id='', is_open=1, start_date=back_test_date_start, end_date=back_test_date_end)
    # date_temp = list(df.iloc[:, 1])
    # date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y-%m-%d') for x in date_temp]
#建回测时间结束
#用上证指数获取时间序列
    try:
        df=pd.read_csv('G:\\stockData\\originData\\000001_sh.csv')#00开头丢失   ,converters = {u'code':str}        
    except Exception as err:
        print('read szIndex.csv err', err)
    df=df.drop_duplicates(['date'])
    df = df.sort_values('date')#降序
    date_seq=list(df[(df['date']>=startDate) & (df['date']<=endDate)]['date'])
#上证指数获取时间序列结束
       
    if isShow==True:#显示的进入单线程
        for code in stockList:#循环股票
            code=str(code)
            myThreadRun(code,filePath1,date_seq,isShow)#=False
    else:#不显示多线程
        executor=ProcessPoolExecutor(max_workers=6)#线程池线程数量
        futures=[]#返回结果
        threads = []
        # isShow=False#显示测试  isShow date_seq filePath1 code
        for code in stockList:#循环股票
            code=str(code)
            future=executor.submit(myThreadRun,code,filePath1,date_seq,isShow)
            futures.append(future)
             # t = threading.Thread(target=myThreadRun,args=(code,filePath1,date_seq,isShow,))
            # threads.append(t)#单个普通多线程添加，也不快啊，还是需要分布式计算，分成阶段，多个进程
        executor.shutdown(True)#立即返回，并不会等待池内的任务执行完毕
        # for i in range(len(threads)):#开始
        #     threads[i].start()
        # for i in range(len(threads)):
        #     threads[i].join()#等待完成

    for backTraceDate in date_seq:#循环日期
        everyDayOperator(backTraceDate)
    elapsed = (time.perf_counter()- start0)
    print('backTrace finish.time use:',elapsed)
#####多线程开始######
def myThreadRun(code=None,filePath1=None,date_seq=None,isShow=False):
    KLine1=kLine()    
    tempStock=[]
    dfTemp1=pd.DataFrame()#空
    holdNum=0
    profit=0
    filename='G:\\stockData\\tradeInfo\\'+code+'.csv'
    ex=os.path.isfile(filename)  #当前文件是否存在，存在即添加，不存在新建
    if ex==True:
        try:
            dfTemp1=pd.read_csv(filename,encoding='utf_8_sig')#新建保存每个的数据
        except Exception as err:
            print('read_csv err', err) 
        holdNum=dfTemp1['buy_sellNum'].sum()       
    # start = time.clock()#计时开始
    start1 =  time.perf_counter()
    for backTraceDate in date_seq:#循环日期
        # start = time.clock()#计时开始            
        df=KLine1.myDrawKLine(filePath1,code,backTraceDate,isShow)
        # print("returnTime used:",(time.clock() - start))
        if ((isShow==1) | (not len(df))):
            continue
        dfTemp=df.tail(1)#取最后一行
        # dfTemp['code']=[code]
        if ('code' not in list(dfTemp))&('ts_code' not in list(dfTemp)):
            dfTemp.insert(0, 'code', ['ts.'+code])  
        dfTemp.loc[dfTemp.index.max(),'buy_sellNum']=0
        dfTemp.loc[dfTemp.index.max(),'holdNum']=[0]   
        # dfTemp['profit']=[0]      
        buyBoll=(dfTemp['buyBoll'].isnull().any()==False)
        buyValleyMA5=(dfTemp['buyValleyMA5'].isnull().any()==False)
        buyValleyMA20=(dfTemp['buyValleyMA20'].isnull().any()==False)
        # buyUpMA20=(dfTemp['buyUpMA20'].isnull().any()==False)
        buyUpMA120=(dfTemp['buyUpMA120'].isnull().any()==False)
        buyBIAS120=(dfTemp['buyBIAS120'].isnull().any()==False)
        sellBoll=(dfTemp['sellBoll'].isnull().any()==False)
        sellPeakMA5=(dfTemp['sellPeakMA5'].isnull().any()==False)
        sellDeathCross=(dfTemp['sellDeathCross'].isnull().any()==False)
        sellDownMA20=(dfTemp['sellDownMA20'].isnull().any()==False)
        sellPeakMA20=(dfTemp['sellPeakMA20'].isnull().any()==False)
        sellBIAS120=(dfTemp['sellBIAS120'].isnull().any()==False)
        # turtelBuy=
        if ( sellPeakMA20 | sellBIAS120 | sellPeakMA5  | sellDownMA20 | sellDeathCross):
            money=0
            holdMoeny=holdNum * float(list(dfTemp['close'])[0])
            if holdNum>0:  
                money=20000
                if money>holdMoeny:
                    money= holdMoeny
            buy_sellNum=sell(price=dfTemp['close'],money=money)#按照当日收盘价买
            dfTemp.loc[dfTemp.index.max(),'buy_sellNum']=[buy_sellNum]
            buy_sellTax=(-1)*buy_sellNum * (list(dfTemp['close'])[0]) * (0.0003+0.001+0.00002)#佣金+印花税+过户费
            if (buy_sellTax < 5)&(buy_sellTax > 0):
                buy_sellTax=5
            dfTemp.loc[dfTemp.index.max(),'buy_sellTax']=[buy_sellTax]
            holdNum += buy_sellNum
            dfTemp.loc[dfTemp.index.max(),'holdNum']=[holdNum]
            tempStock.append((dfTemp.iloc[0,:]))
            dfTemp1=dfTemp
        elif (buyValleyMA20 | buyBIAS120 | buyValleyMA5 | buyBIAS120) :
            money=20000
            buy_sellNum=buy(price=dfTemp['close'],money=money)#按照当日收盘价买
            dfTemp.loc[dfTemp.index.max(),'buy_sellNum']=[buy_sellNum]
            buy_sellTax=buy_sellNum * (list(dfTemp['close'])[0]) * 0.0003#佣金
            if (buy_sellTax < 5)&(buy_sellTax > 0):
                buy_sellTax=5
            dfTemp.loc[dfTemp.index.max(),'buy_sellTax']=[buy_sellTax]
            holdNum += buy_sellNum
            dfTemp.loc[dfTemp.index.max(),'holdNum']=[holdNum]
            tempStock.append((dfTemp.iloc[0,:]))
            dfTemp1=dfTemp    
    # print(dfTemp1)
    result = pd.DataFrame(tempStock, columns=list(dfTemp1))       
    # print(tempStock)
    # elapsed = (time.clock() - start)
    elapsed = (time.perf_counter()- start1)
    print(code+" :allTime used:",elapsed)
    if result.empty==True:
        return False
    result=result.drop_duplicates()#删除重复行
    length=len(result)#!!有错耶
    tt1=result['buy_sellTax'].cumsum()
    result['allTax']=tt1
    tt2=(result['buy_sellNum']*result['close']).cumsum()
    tt3=result['holdNum']*result['close']
    result['profit']=-1*tt2+tt3-tt1
    if ex==False:            
        result.to_csv(filename,index=None,encoding='utf_8_sig')#新建保存每个的数据  
    else :
        result.to_csv(filename,mode='a',index=None,header=False,encoding='utf_8_sig')#后尾追加保存每个的数据  
    return True

#####多线程结束######    
##########    
def buy(price=None,money=None):
    # if price==None:
        # return
    price=list(price)    
    num = money/price[0]  
    shouNum=0
    if num>=100:
        shouNum=int(num/100)#手数
    return shouNum*100
##########
def sell(price=None,money=None):    
    ret= -1*buy(price,money)
    return ret

def everyDayOperator(_date):
    path1='G:\\stockData\\tradeInfo\\'
    path2='G:\\stockData\\everydayOp\\'
    files= os.listdir(path1) #得到文件夹下的所有文件名称
    for code in files: #遍历文件夹
        filename=path1+code  
        try:     
            df=pd.read_csv(filename,encoding='utf_8_sig')#
            df=df.drop_duplicates()#删除重复行
        except Exception as err:
            print('read_csv err', err)
            continue
        df=df[df['date']==_date]
        ex=os.path.isfile(path2+_date+'.csv')  #当前文件是否存在，存在即添加，不存在新建
        if ex==False :            
            df.to_csv(path2+_date+'.csv',index=None,encoding='utf_8_sig')#新建保存每个的数据  
        else :
            df.to_csv(path2+_date+'.csv',mode='a',index=None,header=False,encoding='utf_8_sig')#后尾追加保存每个的数据  
    print(_date+':everydayList finish')

############       
def job():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # return
    config = configparser.ConfigParser() # ini文件类实例化
    # 定义文件路径
    path=os.getcwd()
    path = path+'\\config.ini'
    config.read(path)
    fileName=str(config['mysetting']['fileName']) # 'hs300s'#回测的数据
    days=int(config['mysetting']['days'])    #20  #从今天回测天数   
    isShow=int(config['mysetting']['isShow'])  #False#显示测试,true显示
    #获取前0天交易数据                   
    historyDays=int(config['mysetting']['historyDays'])  #0
    updateData=int(config['mysetting']['updateData']) #是否开启更新股票数据
    #回测开始日期
    startDate=str(config['mysetting']['startDate'])
    # 回测结束日期 
    endDate=str(config['mysetting']['endDate'])
    #是否按照从今日往后回测天数填回测日期
    isTodayAsEnd=int(config['mysetting']['isTodayAsEnd'])
    ##'''
    ################################
    if (updateData==1):
        t=getStockInfo()
        t.getAllIndexHistoryData(days=historyDays)#获取前x天的指数数据
        t.getAllStockHistoryData(days=historyDays)#获取前x天的所有数据
    ################################
    if isTodayAsEnd==1:
        today=datetime.datetime.now().strftime('%Y%m%d')
        startDate=(datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y%m%d')
        startDate = (datetime.datetime.strptime(startDate, "%Y%m%d")).strftime('%Y-%m-%d')
        endDate = (datetime.datetime.strptime(today, "%Y%m%d")).strftime('%Y-%m-%d')
    
    # selectStocks(['300033'],startDate,endDate,isShow) , return
    # stockList1=indexList()
    # selectStocks(stockList1,startDate,endDate,isShow)
    stockList2=stockList(fileName)
    # stockList2=everydayList(fileName)
    selectStocks(stockList2,startDate,endDate,isShow)  
    fileName='zz500s' 
    stockList3=stockList(fileName)
    # selectStocks(stockList3,startDate,endDate,isShow)
    ##'''
    # everyDayOperator('2020-09-02') 
if __name__=='__main__':
    config = configparser.ConfigParser() # ini文件类实例化
    # 定义文件路径
    path=os.getcwd()
    path = path+'\\config.ini'
    config.read(path)
    myTimer=int(config['mysetting']['myTimer'])  #0
    if (myTimer==0):
        job()
    else:
        scheduler = BlockingScheduler()
        scheduler.add_job(job, "cron", day_of_week="1-5", hour=0, minute=1)
        scheduler.start()



