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

def stockList(fileName):#普通股票选择
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

def indexList():#指数选择
    print('index start')
    return ['000001_sh','399006_cyb','399001_sz']
def everydayList(fileName):#选取每天操作的个股代码
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
    # df['code']=df[(df['buy_sellNum']!=0)|(df['holdNum']!=0)]['code']
    df=df.drop_duplicates(['code'])
    df['code']=df['code'].str.extract('(\d+)')#正则表达式截取数字
    stockList=df['code']
    ret=list(stockList)
    return ret

#选股,从沪深300和中证500选吧
def selectStocks(stockList,startDate,endDate,isShow):  
    start0 =  time.perf_counter()
    filePath1='G:\\stockData\\originData\\'

    KLine2=kLine()   
    if isShow==True:#显示的进入单线程
        for code in stockList:#循环股票
            code=str(code)
            KLine2.myDrawKLine(filePath1,code,endDate,isShow)
    else:#不显示多线程
        executor=ProcessPoolExecutor(max_workers=6)#线程池线程数量
        futures=[]#返回结果
        threads = []
        # isShow=False#显示测试  isShow date_seq filePath1 code
        for code in stockList:#循环股票
            code=str(code)
            future=executor.submit( KLine2.myDrawKLine,filePath1,code,endDate,isShow)
            futures.append(future)
             # t = threading.Thread(target=myThreadRun,args=(code,filePath1,date_seq,isShow,))
            # threads.append(t)#单个普通多线程添加，也不快啊，还是需要分布式计算，分成阶段，多个进程
        executor.shutdown(True)#立即返回，并不会等待池内的任务执行完毕
        # for i in range(len(threads)):#开始
        #     threads[i].start()
        # for i in range(len(threads)):
        #     threads[i].join()#等待完成
   
    elapsed = (time.perf_counter()- start0)
    print('select finish.time use:',elapsed)
###############    
######回测开始######    
def backTrace(stockList,startDate,endDate):
    print('......回测开始......')
    start = time.perf_counter()#计时开始   
    #用上证指数获取时间序列
    try:
        df=pd.read_csv('G:\\stockData\\originData\\000001_sh.csv')#00开头丢失   ,converters = {u'code':str}        
    except Exception as err:
        print('read szIndex.csv err', err)
    df=df.drop_duplicates(['date'])
    df = df.sort_values('date')#降序
    date_seq=list(df[(df['date']>=startDate) & (df['date']<=endDate)]['date'])
    #上证指数获取时间序列结束
    path1='G:\\stockData\\myData\\'
    # files= os.listdir(path1) #得到文件夹下的所有文件名称
    files=[(x+'.csv') for x in stockList]
    executor=ProcessPoolExecutor(max_workers=6)#线程池线程数量
    futures=[]#返回结果
    threads = []
    for code in files: #遍历文件夹
        # myThreadRun(code,date_seq)
        future=executor.submit(myThreadRun,code,date_seq)
        futures.append(future)
             # t = threading.Thread(target=myThreadRun,args=(code,filePath1,date_seq,isShow,))
            # threads.append(t)#单个普通多线程添加，也不快啊，还是需要分布式计算，分成阶段，多个进程
    executor.shutdown(True)#立即返回，并不会等待池内的任务执行完毕

    for backTraceDate in date_seq:#循环日期
        everyDayOperator(backTraceDate)#按照日期分类文件
    elapsed = (time.perf_counter()- start)
    print('backTrace finish.time use:',elapsed)
######回测结束######
#####多线程开始######
def myThreadRun(code=None,date_seq=None):#回测按照日期提取买卖数据
    KLine1=kLine()    
    tempStock=[]
    dfTemp1=pd.DataFrame()#空
    holdNum=0
    profit=0
    filename='G:\\stockData\\tradeInfo\\'+code
    ex=os.path.isfile(filename)  #当前文件是否存在，存在即添加，不存在新建
    # if ex==True:
    #     try:
    #         dfTemp1=pd.read_csv(filename,encoding='utf_8_sig')#新建保存每个的数据
    #     except Exception as err:
    #         print('read_csv err', err) 
    start1 =  time.perf_counter()
    filename3='G:\\stockData\\myData\\'+code
    try:
        stock = pd.read_csv(filename3,encoding='utf_8_sig')#index_col=flase 不会将第一列作为index ,converters={'trade_date':str}
    except Exception as err:
        print('read_csv err', err)
    print(code+'  回测开始 ')
    for backTraceDate in date_seq:#循环日期
        df=stock[stock['date']==backTraceDate]
        dfTemp=df.tail(1)#取最后一行
        if ('code' not in list(dfTemp))&('ts_code' not in list(dfTemp)):
            dfTemp.insert(0, 'code', ['ts.'+code[:6]])  
        # turtleBuy=(dfTemp['turtleBuy'].isnull().any()==False)
        # turtleSell=(dfTemp['turtleSell'].isnull().any()==False)
        turtleBuy=(dfTemp['bandBuy'].isnull().any()==False)
        turtleSell=(dfTemp['bandSell'].isnull().any()==False)
        if (turtleBuy) | (turtleSell):
            tempStock.append((dfTemp.iloc[0,:]))
            dfTemp1=dfTemp
    result = pd.DataFrame(tempStock, columns=list(dfTemp1))       
    elapsed = (time.perf_counter()- start1)
    print(code[:6]+" :allTime used:",elapsed)
    if result.empty==True:
        return False
    result=result.drop_duplicates()#删除重复行
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

def everyDayOperator(_date):#根据日期分类股票操作记录文件
    path1='G:\\stockData\\tradeInfo\\'
    path2='G:\\stockData\\everydayOp\\'
    files= os.listdir(path1) #得到文件夹下的所有文件名称
    for code in files: #遍历文件夹
        filename=path1+code  
        try:     
            df=pd.read_csv(filename,encoding='utf_8_sig')#
            df=df.drop_duplicates()#删除重复行
        except Exception as err:
            print(filename+'read_csv err', err)
            continue
        df=df[df['date']==_date]
        ex=os.path.isfile(path2+_date+'.csv')  #当前文件是否存在，存在即添加，不存在新建
        if ex==False :            
            df.to_csv(path2+_date+'.csv',index=None,encoding='utf_8_sig')#新建保存每个的数据  
        else :
            df.to_csv(path2+_date+'.csv',mode='a',index=None,header=False,encoding='utf_8_sig')#后尾追加保存每个的数据  
    print(_date+':everydayList finish')

def chooseNewHigh(beforeDays):#龙头选股,更新每天的历史新高股
    start = time.perf_counter()#计时开始
    print('...choose start....')
    filename='allStockList' 
    codeList= stockList(filename) #得到目标股票池下的所有代码名称
    for code in codeList: #遍历文件夹
        path1='G:\\stockData\\originData\\'+ code[:6] +'.csv'
        try:
            df=pd.read_csv(path1,encoding='utf_8_sig')#新建保存每个的数据
        except Exception as err:
            print(code +'read_csv err', err)
            continue
        if len(df) < 100 | df['ts_code'].str.contains('ST')[0]:
            continue
        today=datetime.datetime.now().strftime('%Y%m%d')
        # today='20201120'
        filename1 = 'G:\\stockData\\newHighPool\\'+ today +'.csv'
        ex=os.path.isfile(filename1)  #当前文件是否存在，存在即添加，不存在新建
        d=str(df.iloc[-1]['trade_date'])
        if  d== today :
            # length=len(df)
            m=df['high'].max()
            for row in  range(-beforeDays,0):
                t=df.iloc[row]['high']
                if t >= m:
                    df=df.loc[[0]]
                    df=df[['ts_code']]
                    if ex==False:            
                        df.to_csv(filename1,index=None,encoding='utf_8_sig')#新建保存每个的数据  
                    else :
                        df.to_csv(filename1,mode='a',index=None,header=False,encoding='utf_8_sig')#后尾追加保存每个的数据
                    break
        else:
            continue
    if ex==True:
        df=pd.read_csv(filename1,encoding='utf_8_sig')#
        f='G:\\stockData\\newHighPool\\'+ today +'.txt'
        df.to_csv(f, sep='\t', index=False)
    # print('choose end.')
    elapsed = time.perf_counter() - start
    print("all Time used:",elapsed)
# 
############       
def job():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # return
    config = configparser.ConfigParser() # ini文件类实例化
    # 定义文件路径
    path=os.getcwd()
    path = path+'\\config.ini'
    config.read(path)#,encoding='utf-8'
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
    #是回测还是选股
    backTrace1=int(config['mysetting']['backTrace'])
    ##'''
    ################################
    if (updateData==1):
        t=getStockInfo()
        t.getAllIndexHistoryData(days=historyDays)#获取前x天的指数数据
        t.getAllStockHistoryData(days=historyDays)#获取前x天的所有数据
        chooseNewHigh(1)#选出前n=1 日的历史新高股
    ################################
    if isTodayAsEnd==1:
        today=datetime.datetime.now().strftime('%Y%m%d')
        startDate=(datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y%m%d')
        startDate = (datetime.datetime.strptime(startDate, "%Y%m%d")).strftime('%Y-%m-%d')
        endDate = (datetime.datetime.strptime(today, "%Y%m%d")).strftime('%Y-%m-%d')
    ##############
    if (backTrace1==0):
        # selectStocks(['300033'],startDate,endDate,isShow) , return
        # stockList1=indexList()
        # selectStocks(stockList1,startDate,endDate,isShow)
        stockList2=stockList(fileName)
        selectStocks(stockList2,startDate,endDate,isShow)  
        fileName='zz500s' 
        # stockList3=stockList(fileName)
        # selectStocks(stockList3,startDate,endDate,isShow)
        # everyDayOperator('2020-09-02') 
    else :
        stockList2=stockList(fileName)
        backTrace(stockList2,startDate,endDate)

if __name__=='__main__':
    config = configparser.ConfigParser() # ini文件类实例化
    # 定义文件路径
    path=os.getcwd()
    path = path+"\\config.ini"
    config.read(path)#,encoding='UTF-8'
    myTimer=int(config['mysetting']['myTimer'])  #0
    if (myTimer==0):
        job()
    else:
        print('定时测试 5:01 ')
        scheduler = BlockingScheduler()
        scheduler.add_job(job, "cron", day_of_week="1-5", hour=5, minute=1)
        scheduler.start()



