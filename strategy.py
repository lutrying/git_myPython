# -*- coding: utf-8 -*-
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
import os


class strategy:
    pass

    def __init__(self):
        # 设置tushare pro的token并获取连接
        # ts.set_token(
        #     '8375715c8253a8ea5a06b0b805182ef6dc5ff70cb243c5a6403088bc')
        # self.pro = ts.pro_api()
        # df = self.pro.daily(ts_code='000001.SH', start_date='20180701', end_date='20180718')

        pass

#均线系统
    def myMA(self,data):
        data['MA5']=data['close'].rolling(5).mean()
        data['MA10']=data['close'].rolling(10).mean()
        data['MA20']=data['close'].rolling(20).mean()
        # data['MA30']=data['close'].rolling(30).mean()
        # data['MA60']=data['close'].rolling(60).mean()
        return (data)

    #乖离率
    def myBIAS(self,data):
        # ma5=data['close'].rolling(5).mean()
        # ma6=data['close'].rolling(6).mean()
        # ma12=data['close'].rolling(12).mean()
        ma20=data['MA20']
        # ma60=data['MA60']
        # data['BIAS5']=(data['close']-ma5)/ma5*100
        # data['BIAS6']=(data['close']-ma6)/ma6*100
        # data['BIAS12']=(data['close']-ma12)/ma12*100
        data['BIAS20']=(data['close']-ma20)/ma20*100
        # data['BIAS60']=(data['close']-ma60)/ma60*100
        return(data)
        pass

#布林线
    def myBoll(self,tsPrice,period=20,times=2):
        upBoll=pd.Series(0.0,index=tsPrice.index)
        middleBoll=pd.Series(0.0,index=tsPrice.index)
        downBoll=pd.Series(0.0,index=tsPrice.index)
        sigma=pd.Series(0.0,index=tsPrice.index)
        for i in range(period-1,len(tsPrice)):#从period-1开始到len(tsPrice)递增1
            #中线20日均线
            middleBoll[i]=np.nanmean(tsPrice[i-(period-1):(i+1)])#切片前period个数，要求日期升序
            #20日标准差
            sigma[i]=np.nanstd(tsPrice[i-(period-1):(i+1)])
            #上轨
            upBoll[i]=middleBoll[i]+times*sigma[i] 
            #下轨
            downBoll[i]=middleBoll[i]-times*sigma[i]   
        BBands=pd.DataFrame({'upBoll':upBoll[period-1:],\
                             'middleBoll':middleBoll[period-1:],\
                             'downBoll':downBoll[period-1:],\
                             'sigma':sigma[period-1:]}) 
        return(BBands)

#归一化
    def myNormalize(self,arr):
        # arr = np.asarray([-10, -300, 0.0, 18, 1])
        # arr=arr[arr>=0]
        print(abs(arr))
        # arr2=arr[arr<0]
        for x in arr:
            # if x>0:
                x = float(x - np.min(abs(arr)))/(np.max(abs(arr))- np.min(abs(arr)))#归一化
                # x = float(x - np.mean(arr1))/(np.max(arr1)- np.min(arr1))#均值归一
                # x = float(x - np.mean(arr))/np.std(arr)#标准化
                print ('>0== ',x)
        from sklearn import preprocessing
        arr=arr.reshape(-1,1)
        tt= preprocessing.MaxAbsScaler().fit_transform(arr)#归一化到[-1,1],这个合适，不然就分开[-1,0],[0,1]
        # tt= preprocessing.StandardScaler().fit_transform(arr)#标准化到均值0，方差1
        # tt= preprocessing.MinMaxScaler().fit_transform(arr)#归一化到[0,1]
        # tt= preprocessing.Normalizer().fit_transform(arr)#归一化到-1,0,1，三者
        # tt= preprocessing.RobustScaler().fit_transform(arr)#归一化到统一的量纲，
        print(tt)

#
    def leadingStock(self): 
        pass
        codeList=[]
        limitUpNum=[]
        temp=pd.DataFrame()
        startDate='2019-01-01'
        endDate='2020-11-25'
        path1='G:\\stockData\\originData\\'
        path2='G:\\stockData\\'
        files= os.listdir(path1) #得到文件夹下的所有文件名称
        i=0
        for code in files: #遍历文件夹
            # i+=1
            # if(i>20):
            #     break
            if code in ['399006_cyb.csv','000001_sh.csv','399001_sz.csv']:
                continue
            filename=path1+code  
            try:     
                df=pd.read_csv(filename,encoding='utf_8_sig')#
                df=df.drop_duplicates()#删除重复行
            except Exception as err:
                print('read_csv err', err)
                continue
            df['trade_date']=df['trade_date'].apply(lambda x:(datetime.datetime.strptime(str(int(x)), "%Y%m%d")).strftime('%Y-%m-%d'))
            df=df[(df['trade_date']>startDate)&(df['trade_date']<endDate)]#选择回测的截止日期数据
            # df=df.sort_values('pct_chg')#降序
            # print (df['pct_chg']>9.8)
            df=df[(df['pct_chg']>9.8)]
            length=len(df)
            if length>1:#还真多没有涨停的！！
                # a=df.loc[1,'ts_code']
                print(df.iloc[0]['ts_code'],',len='+str(length))
                codeList.append((df.iloc[0]['ts_code']))
                limitUpNum.append(length)
        temp['code']=codeList
        temp['limitUpNum']=limitUpNum
        temp = temp.sort_values('limitUpNum',ascending=False)#降序 ,ascending=False
        temp=temp.iloc[:200]#取前200
        temp.to_csv(path2+'limitUpNum'+'.csv',index=None,encoding='utf_8_sig')#新建保存每个的数据 

    def addName(self):
        path='G:\\stockData\\'
        filename =path+'allStockList.csv'
        filename1 =path+'limitUpNum.csv'
        try:     
            df=pd.read_csv(filename,encoding='utf_8_sig')#
            df1=pd.read_csv(filename1,encoding='utf_8_sig')#
        except Exception as err:
            print('read_csv err', err)

        for index,row in df1.iterrows():
            code=str(row.code)
            df1.loc[index,'name']=(df[df['ts_code']==code]['name'].values)
        pass
        df1.to_csv(filename1,index=None,encoding='utf_8_sig')#新建保存每个的数据 
if __name__ == '__main__':
    t=strategy()
  
    # t.myNormalize(arr)
    # print(mapminmax(arr))
    # print(int(3.1))
    t.leadingStock()
    # t.addName()
