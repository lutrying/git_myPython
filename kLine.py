import datetime
import tushare as ts
import pymysql
import baostock as bs
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec#分割子图
import numpy as np
from scipy import signal   #滤波等
import matplotlib.dates as mdates    #處理日期
import mpl_finance as mpf
import talib
from matplotlib.pylab import date2num
import matplotlib.ticker as ticker
from sympy import *
import scipy.stats as stats  #该模块包含了所有的统计分析函数
import os
from strategy import *

class kLine:
    def _init_(self):
        pass
#从网上找的，x轴的日期是int连续的，无法解决周末节假日缺失的问题
#需要先转成int然后把日期整成xticks x轴刻度去自己改写进去

    def myDrawKLine(self,filePath,_code,backTraceDate,isShow):
 #       
        start = time.perf_counter()#计时开始
        code=_code
        # stock1 = pd.read_csv('G:\\stockData\\'+code+'.csv',index_col=0)
        stock1=pd.DataFrame()
        try:
            stock1 = pd.read_csv(filePath+code+'.csv',encoding='utf_8_sig')#index_col=flase 不会将第一列作为index ,converters={'trade_date':str}
        except Exception as err:
            print('read_csv err', err)
            return stock1
        stock1=stock1.dropna()#删除所有包含空值的行       
        if 'trade_date' in list(stock1):
            stock1=stock1.rename(columns={'trade_date': 'date'})
        if 'volume' in list(stock1):
            stock1=stock1.rename(columns={'volume': 'vol'})
        stock1=stock1.drop_duplicates(['date'])
        t1=str(list(stock1['date'])[0])
        if (t1.find('-') == -1):
            stock1['date']=stock1['date'].astype(str)
            stock1['date']=stock1['date'].str[:8]
            # stock1['date']=stock1['date'][0]
            stock1['date'] =[(datetime.datetime.strptime(str(x), "%Y%m%d")).strftime('%Y-%m-%d') for x in stock1['date'].values]
        stock = stock1.sort_values('date')#降序
        stock =stock.reset_index(drop=True)#去掉原序，重新0开始
        stock=stock[stock['date']<=backTraceDate]#选择回测的截止日期数据
        # if (backTraceDate in list(stock.iloc[-1,:]))==False:#不重最后一天
            # return (pd.DataFrame())
        length=len(stock)
#
#####日线换算成周线开始######
        # period_type = 'W'
        # stock_week=stock.copy()
        # stock_week.set_index('date', inplace=True)
        # # 把普通索引转换成时间索引，resample函数只支持时间索引
        # stock_week.index = pd.to_datetime(stock_week.index)
        # #进行转换，周线的每个变量都等于那一周中最后一个交易日的变量值
        # stock_week1 = stock_week.resample(period_type).last()
        # stock_week1['close']=stock_week['close'].resample(period_type).last()
        # stock_week1=stock_week1.dropna()
        # date_fri =[str(x)[:10] for x in stock_week1.index.values]
        # date_all=stock.date.values
        # def jian2(date_list):#算周线close值
        #     d3=[]
        #     for x in date_list:
        #         d1=(datetime.datetime.strptime(x, "%Y-%m-%d"))
        #         # d2=(d1 - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        #         d2=''
        #         for i in range(2,7):
        #             d2=(d1 - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        #             if d2 in date_all:
        #                 break
        #         d3.append(d2)
        #     return d3
        # date_week=jian2(date_fri)
        # stock_week1['date_week']=date_week
        # #周线MACD
        # stock_week1['macd_difWeek'], stock_week1['macd_deaWeek'], stock_week1['macd_barWeek'] = talib.MACD(stock_week1['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)     
        # stock_week1['macd_goldWeek']=stock_week1[(stock_week1['macd_difWeek']>stock_week1['macd_deaWeek'])&(stock_week1['macd_difWeek'].shift(1)<stock_week1['macd_deaWeek'].shift(1))]['close']       
        # gold_date=stock_week1[stock_week1['macd_goldWeek']>0]['date_week'].values
        # stock_week1['macd_deathWeek']=stock_week1[(stock_week1['macd_difWeek']<stock_week1['macd_deaWeek'])&(stock_week1['macd_difWeek'].shift(1)>stock_week1['macd_deaWeek'].shift(1))]['close']       
        # death_date=stock_week1[stock_week1['macd_deathWeek']>0]['date_week'].values
        # stock_week1.to_csv('G:\\stockData\\myData\\'+code+'_11.csv')
#####日线换算成周线结束######
        # stock['close_week']=stock[stock['date'].isin(date_week)]['close']
        # stock['macd_goldWeek']=stock[stock['date'].isin(gold_date)]['close']
        # stock['macd_deathWeek']=stock[stock['date'].isin(death_date)]['close']
        # stock['macd_difWeek']=np.where(stock['date'].isin(date_week),stock_week1['macd_difWeek'],np.nan)
        # stock['close_week']=stock['close_week'].fillna(0)
###画均线开始，右侧滞后##
        # stock=tt.myMA(stock)
        # stock['MA5']=stock['close'].rolling(3).mean()
        stock['MA5']=stock['close'].rolling(20).mean()
        stock['MA10']=stock['close'].rolling(120).mean()
        stock['MA20']=stock['close'].rolling(20).mean()
        stock['MA120']=stock['close'].rolling(120).mean()#作为趋势线！！！只操作上趋势
        turtleDays=55#斐波那契，入场
        turtleOut=20 #清仓
        stock['turtleMax']=stock['high'].shift(1).rolling(turtleDays).max()#天
        stock['turtleMin']=stock['low'].shift(1).rolling(turtleDays).min()#天
        stock['turtleOut']=stock['low'].shift(1).rolling(turtleOut).min()#天
#        #10天线是黑马线来的
        # stock['sell_MA10']=stock[(stock['close']<stock['MA10'])&(stock['MA10']<stock['MA10'].shift(1))]['close']
        #死叉5 \ 20     
        stock['sellDeathCross']=stock[(stock['MA5']<stock['MA10'])&(stock['MA5'].shift(1)>stock['MA10'].shift(1))]['close']       
        #金叉
        stock['buyGoldenCross']=stock[(stock['MA5']>stock['MA10'])&(stock['MA5'].shift(1)<stock['MA10'].shift(1))]['close']       
                
        stock['MA120_up']=stock[(stock['MA120'] > stock['MA120'].shift(1))]['MA120']# & 
# 
        stock['MA120_cross']=stock[(stock['close'] > stock['MA120'])&(stock['close'].shift(1) < stock['MA120'].shift(1))]['MA120']# 
        # stock['MA20_up']=stock[(stock['MA20'] > stock['MA20'].shift(1))]['MA20']# & 
        # stock['MA20_down']=stock[(stock['MA20'] < stock['MA20'].shift(1))]['MA20']#
        # stock['MA20_sell']=stock[(stock['close'] < stock['MA20'])&(stock['MA20_down']>0)]['MA20']#
        # #周期底部，估测周期时长
        # stock['down2up20']= stock[(stock['MA20'] > stock['MA20'].shift(1))&(stock['MA20'].shift(1) < stock['MA20'].shift(2))]['MA20']
        # #周期顶部
        # stock['up2down20']= stock[(stock['MA20'] < stock['MA20'].shift(1))&(stock['MA20'].shift(1) > stock['MA20'].shift(2))]['MA20']
        # stock['max20']=stock['high'].rolling(21).max()#天
        # stock['min20']=stock['low'].rolling(21).min()#天
        
#####求出当前20天内是否创历史新高，新高才操作 , 20 和 20周期和幅度均值和正态概率密度值
        tMax= -99999
#        # min20= -99
        # max20 =-99
        # MA20_up=0
        # MA20_upDays=0
        # MA20_upDaysList= []
        # MA20_upAmpList= []
        # MA20_down=0
        # MA20_downDays=0
        # MA20_downDaysList= []
#        # MA20_downAmpList= []
        for row in range(length):#
            if stock.loc[row,'high'] >= tMax:#历史新高标志位
                tMax = stock.loc[row,'high']
                stock.loc[row,'historyHigh']= 1
#
            #算20天的周期和幅度均值   
            # if stock.loc[row,'down2up20'] > 0:#涨的
            #     MA20_up= 1 #底部拐点标志位
            #     min20 = stock.loc[row,'min20']
            # if (MA20_up == 1):#算时长和幅度
            #     if (stock.loc[row,'MA20_up'] > 0):
            #         MA20_upDays += 1#时长
            #     if (stock.loc[row,'MA20_down'] > 0):    
            #         # stock.loc[row,'MA20_upDays']= MA20_upDays#时长MA20_upDays =0
            #         MA20_up =0
            #         if MA20_upDays < 5:#滤波，小于5天都不要
            #             MA20_upDays =0
            #             continue
            #         MA20_upDaysList.append(MA20_upDays)
            #         MA20_upDays =0
            #         tMean= np.mean(MA20_upDaysList)#均值
            #         tStd= np.std(MA20_upDaysList)#标准差
            #         tMedian=np.median(MA20_upDaysList)#中位数
            #         stock.loc[row,'MA20_upDaysMean']= tMean
            #         stock.loc[row,'MA20_upDaysMedian']= tMedian
            #         stock.loc[row,'MA20_upDaysStd']= tStd
            #         tAmp= (stock.loc[row,'max20'] - min20)/min20*100#需要整成百分比
            #         stock.loc[row,'MA20_upAmp']=  tAmp#幅度
            #         MA20_upAmpList.append(tAmp)
            #         tMean= np.mean(MA20_upAmpList)#均值
            #         tStd= np.std(MA20_upAmpList)#标准差
            #         tMedian=np.median(MA20_upAmpList)#中位数
            #         stock.loc[row,'MA20_upAmpMean']= tMean
            #         stock.loc[row,'MA20_upAmpMedian']= tMedian
            #         stock.loc[row,'MA20_upAmpStd']= tStd
                    
#            
            # if stock.loc[row,'up2down20'] > 0:#跌的
            #     MA20_down= 1 #顶部拐点标志位
            #     max20 = stock.loc[row,'max20']
            # if (MA20_down == 1):#算时长和幅度
            #     if (stock.loc[row,'MA20_down'] > 0):
            #         MA20_downDays += 1#时长
            #     if (stock.loc[row,'MA20_up'] > 0):   
            #         MA20_down =0
            #         if MA20_downDays < 5:#滤波，小于5天都不要
            #             MA20_downDays =0
            #             continue 
            #         MA20_downDaysList.append(MA20_downDays)
            #         MA20_downDays =0
            #         tMean= np.mean(MA20_downDaysList)#均值
            #         tStd= np.std(MA20_downDaysList)#标准差
            #         stock.loc[row,'MA20_upDaysMean']= -tMean
            #         stock.loc[row,'MA20_upDaysStd']= -tStd
            #         tAmp= (max20 - stock.loc[row,'min20'])/ max20
            #         stock.loc[row,'MA20_upAmp']=  -tAmp#幅度
            #         MA20_downAmpList.append(tAmp)
            #         tMean= np.mean(MA20_downAmpList)#均值
            #         tStd= np.std(MA20_downAmpList)#标准差
            #         stock.loc[row,'MA20_upAmpMean']= -tMean
            #         stock.loc[row,'MA20_upAmpStd']= -tStd
#
        # stock.to_csv('G:\\stockData\\te.csv',index=None,encoding='utf_8_sig')      
        # MA20_upDays =0
        # MA20_up =0
        # dMean=0
        # dStd=0
        # aMean =0
        # aStd =  0
        # for row in range(length):#正态概率密度值,再循环一遍求概率 
        #     if stock.loc[row,'MA20_upDaysMean']> 0:#涨的
        #         dMean = stock.loc[row,'MA20_upDaysMean']
        #         dStd =  stock.loc[row,'MA20_upDaysStd']
        #         aMean = stock.loc[row,'MA20_upAmpMean']
        #         aStd =  stock.loc[row,'MA20_upAmpStd']
        #     if stock.loc[row,'down2up20'] > 0:#涨的
        #         MA20_up= 1 #底部拐点标志位
        #         min20 = stock.loc[row,'min20']
        #         MA20_upDays =0
        #     if (MA20_up == 1):#算时长和幅度
        #         if (stock.loc[row,'MA20_up'] > 0):
        #             MA20_upDays += 1#时长
        #             stock.loc[row,'MA20_upDays']= MA20_upDays#时长MA20_upDays =0
        #             aAmp= (stock.loc[row,'close'] - min20)/min20
        #             if (dStd==0) | (aStd==0):#不能除0
        #                 continue
        #             z= (MA20_upDays - dMean) / dStd#Z变换
        #             stock.loc[row,'MA20_upDaysPro']= stats.norm.cdf(z)#关于时长的正太分布概率值
        #             z= (aAmp - aMean) / aStd#Z变换
        #             stock.loc[row,'MA20_upAmpPro']= stats.norm.cdf(z)#关于幅度的正太分布概率值
        #         if (stock.loc[row,'MA20_down'] > 0): 
        #             MA20_up=0
        #             MA20_upDays =0
# #
            # if stock.loc[row,'MA20_upDaysMean']< 0:#跌的
            #     dMean = -stock.loc[row,'MA20_upDaysMean']
            #     dStd =  -stock.loc[row,'MA20_upDaysStd']
            #     aMean = -stock.loc[row,'MA20_upAmpMean']
            #     aStd =  -stock.loc[row,'MA20_upAmpStd']
            # if stock.loc[row,'up2down20'] > 0:#涨的
            #     MA20_up= 2 #底部拐点标志位
            #     max20 = stock.loc[row,'max20']
            #     MA20_upDays =0
            # if (MA20_up == 2):#算时长和幅度
            #     if (stock.loc[row,'MA20_down'] > 0):
            #         MA20_upDays += 1#时长
            #         stock.loc[row,'MA20_upDays']= -MA20_upDays#时长MA20_upDays =0
            #         aAmp= (max20 - stock.loc[row,'close'])/max20
            #         if (dStd==0) | (aStd==0):#不能除0
            #             continue
            #         z= (MA20_upDays - dMean) / dStd#Z变换
            #         stock.loc[row,'MA20_upDaysPro']= stats.norm.cdf(z)#关于时长的正太分布概率值
            #         z= (aAmp - aMean) / aStd#Z变换
            #         stock.loc[row,'MA20_upAmpPro']= stats.norm.cdf(z)#关于幅度的正太分布概率值
            #     if (stock.loc[row,'MA20_up'] > 0): 
            #         MA20_up=0
            #         MA20_upDays =0

#       
        #20天的一阶导斜率，判短期趋势：上、平、下，二阶导加速度
        # deltaY=stock['MA5']-stock['MA5'].shift(1)#▽Y,xy轴如何变换到同一数量级呢？
        #归一化到arctan[-1,1]是[-45,45]*2就是[-90,90]啦！！
        # deltaY=(deltaY - np.min(abs(deltaY)))/(np.max(abs(deltaY))- np.min(abs(deltaY)))
        # stock['k_ratio5']=np.arctan(deltaY)*180/np.pi*2#用斜率的定义求一阶导数斜率，弧度角度切换
        # k_ratio5=(stock['k_ratio5']>0)
        # #20天的一阶导斜率，判短期趋势：上、平、下，二阶导加速度
        # deltaY=stock['MA20']-stock['MA20'].shift(1)#▽Y,xy轴如何变换到同一数量级呢？
        # #归一化到arctan[-1,1]是[-45,45]*2就是[-90,90]啦！！
        # deltaY=(deltaY - np.min(abs(deltaY)))/(np.max(abs(deltaY))- np.min(abs(deltaY)))
        # stock['k_ratio20']=np.arctan(deltaY)*180/np.pi*2#用斜率的定义求一阶导数斜率，弧度角度切换
        # #归一化到arctan[-1,1]是[-45,45]*2就是[-90,90]啦！！
        # deltaY=stock['MA120']-stock['MA120'].shift(1)
        # deltaY=(deltaY - np.min(abs(deltaY)))/(np.max(abs(deltaY))- np.min(abs(deltaY)))
        # stock['k_ratio120']=np.arctan(deltaY)*180/np.pi*2#用斜率的定义求一阶导数斜率，弧度角度切换
        # # k_ratio120=(stock['k_ratio120']>0)
        # trendUp=((stock['close']>stock['MA120']) & (stock['k_ratio120']>0))
        # print(yy[signal.argrelextrema(yy, np.greater)]) #极大值的y轴, yvals为要求极值的序列
        # print(signal.argrelextrema(yy, np.greater))  #极大值的x轴
        # peak_ind = signal.argrelextrema(yy,np.greater)[0] #极大值点，改为np.less即可得到极小值点
###均线结束##

#画布林带开始，左侧超前，通道，均值回复#
        # tt=strategy()
        # _period=20
        # bBands=tt.myBoll(stock.close,period=_period)
        # stock['middleBoll']=bBands['middleBoll']
        # stock['upBoll']=bBands['upBoll']
#        # stock['downBoll']=bBands['downBoll']
        stock['upBoll'],stock['middleBoll'],stock['downBoll']=talib.BBANDS(stock.close.values,timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        stock['buyBoll']=stock[(stock['close'].shift(1) < stock['downBoll'].shift(1))&(stock['close'] > stock['downBoll'])]['close'] 
        # buyBoll=(stock['buyBoll'].rolling(8).count()>0)
        #昨日破上轨确认，今日下破确认，明天卖出       
        stock['sellBoll']=stock[(stock['close'].shift(1) > stock['upBoll'].shift(1))&(stock['close'] < stock['upBoll'])]['close']
#画布林带结束#
######乖离率开始,左侧超前，逆趋势，均值回复######
        stock['BIAS120']=(stock['close']-stock['MA120'])/stock['MA120']
        bias=0.55
        # #逃顶抄底！！
        # #正乖离，且上涨概率在15%范围内
        pTop=(stock['BIAS120']> bias)#34
        # #负乖离且上涨概率在
        pBottom=(stock['BIAS120']< -bias)
        stock['buyBIAS120']=stock[pBottom & (stock['buyBoll']>0)]['close']#结合boll抄底
        stock['sellBIAS120']=stock[pTop & (stock['sellBoll']>0)]['close']#逃顶
######乖离率结束####### 
# #绘制KDJ
        stock['K'], stock['D'] = talib.STOCH(stock.high.values, stock.low.values, stock.close.values,\
            fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        stock['J'] = 3 * stock['K'] - 2 * stock['D'] 
        stock['K']=0.01*stock['K']#缩放到0~1
        stock['D']=0.01*stock['D']
        stock['J']=0.01*stock['J']
##MACD开始##
        stock['macd_dif'], stock['macd_dea'], stock['macd_bar'] = talib.MACD(stock['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        # bar_red = np.where(stock['macd_bar'] > 0, 2 * stock['macd_bar'], 0)# 绘制BAR>0 柱状图
        # bar_green = np.where(stock['macd_bar'] < 0, 2 * stock['macd_bar'], 0)# 绘制BAR<0 柱状图
        # stock['macd_shift_1']=stock['macd_bar'].shift(1)  
#        #连续3天macd_bar 向下
        # stock['macd_sell']=stock[(stock['macd_bar'] < stock['macd_bar'].shift(1))&(stock['macd_bar'].shift(1) < stock['macd_bar'].shift(2))\
        #     &(stock['macd_bar'].shift(2) < stock['macd_bar'].shift(3))]['close']
        # #连续3天macd_bar 向上
        # stock['macd_buy']=stock[(stock['macd_bar'] > stock['macd_bar'].shift(1))&(stock['macd_bar'].shift(1) > stock['macd_bar'].shift(2))\
        #     &(stock['macd_bar'].shift(2) > stock['macd_bar'].shift(3))]['close']
##MACD结束##
#       #真实波动幅度
        stock['ATR']=talib.ATR(stock.high.values, stock.low.values, stock.close.values, timeperiod=14)
        stock['trend_close_up']=stock['close'].shift(1) + 0.5*stock['ATR'].shift(1)#用ATR预测走势
        stock['trend_close_down']=stock['close'].shift(1) - 0.5*stock['ATR'].shift(1)
# MACD金叉/死叉 波段开始#
#
        # yy=np.array(stock['MA20'])
        # xx=signal.argrelextrema(yy, np.less,order=2)
        # stock['valley']=stock.iloc[xx]['MA20']
        # xx2=signal.argrelextrema(yy, np.greater,order=2)
        # # xx2=signal.find_peaks(yy, distance=10)
        # stock['peak']=stock.iloc[xx2]['MA20']
#
        #macd死叉       
        # stock['macd_death']=stock[(stock['macd_dif']<stock['macd_dea'])&(stock['macd_dif'].shift(1)>stock['macd_dea'].shift(1))]['close']       
        #macd金叉
        # stock['macd_gold']=stock[(stock['macd_dif']>stock['macd_dea'])&(stock['macd_dif'].shift(1)<stock['macd_dea'].shift(1))]['close']       
        #macd_bar死叉       
        stock['macd_death']=stock[(stock['macd_bar']<0)&(stock['macd_bar'].shift(1)>0)]['close']       
        #macd_bar金叉
        stock['macd_gold']=stock[(stock['macd_bar']>0)&(stock['macd_bar'].shift(1)<0)]['close']       

#macd 顶背离开始  ：bar背离:面积，最长值，持续时间#########
        macd_mark= 0  ## 两批红柱 两批绿柱,标志位，默认从金叉开始
        macd_mark1= 0
        red_macd1={'bar_area':[],'bar_max':[],'dif_max':[],'p_high':[],'topDate':[]}#第一批红柱变量
        red_mark={'bar_area':0,'bar_max':-1,'dif_max':-99,'p_high':-1}#第二批红柱变量
        g_macd1={'bar_area':[],'bar_min':[],'dif_min':[],'p_low':[],'buttomDate':[]}
        g_mark={'bar_area':0,'bar_min':9999,'dif_min':9999,'p_low':9999}
        for row in range(length):#计算每一波红绿柱
            if stock.loc[row,'macd_gold'] > 0:#算每一批红柱，以金叉为开始，死叉为结束
                macd_mark = 1
            if macd_mark == 1:
                red_mark['bar_area'] += stock.loc[row,'macd_bar']#红柱面积
                if stock.loc[row,'macd_dif'] > red_mark['dif_max'] :
                    red_mark['dif_max'] = stock.loc[row,'macd_dif']#dif最大
                if stock.loc[row,'macd_bar'] > red_mark['bar_max'] :
                    red_mark['bar_max'] = stock.loc[row,'macd_bar']#红柱最长值
                if stock.loc[row,'high'] > red_mark['p_high'] :
                    red_mark['p_high'] = stock.loc[row,'high']#价格最高值
                if (stock.loc[row,'macd_death'] > 0):#出现死叉后结束这一次统计，压入红柱字典
                    red_mark['bar_area'] -= stock.loc[row,'macd_bar']
                    red_macd1['bar_area'].append(red_mark['bar_area'])
                    red_macd1['dif_max'].append(red_mark['dif_max'])
                    red_macd1['bar_max'].append(red_mark['bar_max'])
                    red_macd1['p_high'].append(red_mark['p_high'])
                    t= stock.loc[row,'date']
                    red_macd1['topDate'].append(t)
                    red_mark['bar_area'] =0
                    red_mark['dif_max']=-99
                    red_mark['bar_max'] = -1
                    red_mark['p_high'] = -1
                    macd_mark = 0

            if stock.loc[row,'macd_death'] > 0:#算每一批绿柱，以死叉为开始，金叉为结束
                macd_mark1 = 2
            if macd_mark1 == 2:
                g_mark['bar_area'] += stock.loc[row,'macd_bar']
                if stock.loc[row,'macd_dif'] < g_mark['dif_min'] :
                    g_mark['dif_min'] = stock.loc[row,'macd_dif']#dif最小
                if stock.loc[row,'macd_bar'] < g_mark['bar_min'] :
                    g_mark['bar_min'] = stock.loc[row,'macd_bar']
                if stock.loc[row,'low'] < g_mark['p_low'] :
                    g_mark['p_low'] = stock.loc[row,'low']
                if (stock.loc[row,'macd_gold'] > 0):
                    g_mark['bar_area'] -= stock.loc[row,'macd_bar']
                    g_macd1['bar_area'].append(g_mark['bar_area'])
                    g_macd1['dif_min'].append(g_mark['dif_min'])
                    g_macd1['bar_min'].append(g_mark['bar_min'])
                    g_macd1['p_low'].append(g_mark['p_low'])
                    t= stock.loc[row,'date']
                    g_macd1['buttomDate'].append(t)
                    g_mark['bar_area'] =0
                    g_mark['dif_min']= 9999
                    g_mark['bar_min'] = 9999
                    g_mark['p_low'] = 9999
                    macd_mark1 = 0
    ##########比较前后两波红柱，绿柱，出背离结果
        def func_back(pam_data):#计算背离，归类背离类型    
            df_temp=pd.DataFrame(pam_data)
            if 'p_high' in list(pam_data):
                p_back=(df_temp['p_high'] > df_temp['p_high'].shift(1))
                area=(df_temp['bar_area'] > df_temp['bar_area'].shift(1))            
                dif=(df_temp['dif_max'] > df_temp['dif_max'].shift(1))
                bar=(df_temp['bar_max'] > df_temp['bar_max'].shift(1))
            else:
                p_back=(df_temp['p_low'] < df_temp['p_low'].shift(1))
                area=(df_temp['bar_area'] < df_temp['bar_area'].shift(1))            
                dif=(df_temp['dif_min'] < df_temp['dif_min'].shift(1))
                bar=(df_temp['bar_min'] < df_temp['bar_min'].shift(1))
            ###7种背离方式：1、只有bar-area背离，2、只有dif背离，3、只有bar背离，4、bar-area & dif 背离
            ###5、bar-area & bar 背离，6、bar & dif 背离，7、bar-area & dif & bar 背离
            level_1= (p_back & (~area & dif & bar))
            level_2= (p_back & (area & ~dif & bar))
            level_3= (p_back & (area & dif & ~bar))
            level_4= (p_back & (~area & ~dif & bar))
            level_5= (p_back & (~area & dif & ~bar))
            level_6= (p_back & (area & ~dif & ~bar))
            level_7= (p_back &(~area & ~dif & ~bar))
            df_temp.loc[level_1,'level']='area'
            df_temp.loc[level_2,'level']='dif'
            df_temp.loc[level_3,'level']='bar'
            df_temp.loc[level_4,'level']='area + dif'
            df_temp.loc[level_5,'level']='area + bar'
            df_temp.loc[level_6,'level']='dif + bar'
            df_temp.loc[level_7,'level']='area + dif + bar'
            df_temp=df_temp.dropna()
            df_temp =df_temp.reset_index(drop=True)#去掉原序，重新0开始
            return df_temp
        df_temp = func_back(red_macd1)
        backDate= df_temp['topDate']
        stock['top_level']='0'
        for i,date in enumerate(backDate):#在主数据库里写入顶背离类型
            stock.loc[stock['date']== date,'top_level']=df_temp.loc[i,'level']
        df_temp = func_back(g_macd1)
        backDate= df_temp['buttomDate']
        stock['buttom_level']='0'
        for i,date in enumerate(backDate):#在主数据库里标志底背离类型
            stock.loc[stock['date']== date,'buttom_level']=df_temp.loc[i,'level']
        # df_temp.to_csv('G:\\stockData\\test\\'+code+'_back.csv')
#macd 背离结束#######
            
        mark1=[0,0]
        mark2=[0,0,0,0]
        ATR1=[0.0]
        buyDate1=[]
        sellDate1=[]
        buy_sell1=[0,0,0]
        band_max=[-99]
        ATR_max=[0]
        def func_band(pam):#  4 9 18 均线
            if (pam['buyGoldenCross'] > 0):
                mark2[1]=1
            if (pam['sellDeathCross'] > 0):
                mark2[1]=0
            #滤嘴：！ & (pam['close'] > pam['MA120'])& (pam['MA120_up'] > 0)&(pam['macd_gold'] > 0)
            if (pam['high'] != pam['low'])  &((pam['buyGoldenCross'] > 0)|((mark2[1]>0)&(pam['MA120_cross'] > 0))):#
                    buy_sell1[0]=pam['close']
                    buy_sell1[1]=pam['close']
                    buyDate1.append(pam['date'])
                    ATR1[0]=pam['ATR']
                    mark2[0] = 1
                    mark1[0] = 1
            if (mark2[0] != 0) :
                if (pam['high']>band_max[0]):#求出买进后的最大值
                    band_max[0]=pam['high']
                    ATR_max[0]=pam['ATR']
                if (band_max[0] - buy_sell1[1])/ buy_sell1[1] > 1:
                        mark1[1]=1
                        buy_sell1[2]= buy_sell1[1] + 0.75*(band_max[0] - buy_sell1[1])
                #赚钱的精髓是加仓！！ 加仓 3次 总亏损 （1.5 + 1 + 0.5 + 0 ）*R = 3R，R=0.04% * totalMoney
                if (mark2[0] < 5) & (pam['close'] > (buy_sell1[0]+1*ATR1[0])) & (pam['high'] != pam['low']):
                    buy_sell1[0]=pam['close']
                    buyDate1.append(pam['date'])
                    ATR1[0]=pam['ATR']
                    mark2[0] += 1
                    #1.5ATR止损,simple is the best  |(pam['macd_death'] >0) (pam['close'] < (buy_sell1[0]-5*ATR1[0]))
                if (pam['high'] != pam['low']) &( (pam['close'] < buy_sell1[2])|(pam['close'] <pam['MA120'])):
                    sellDate1.append(pam['date'])
                    mark1[0] = 0
                    mark1[1] = 0
                    mark2[0] = 0
                    band_max[0]=-99
                    buy_sell1[2]=-99
        #使用apply的用法，进行循环，实现低买高卖的波段操作
        stock.apply(func_band,axis=1)
        stock['bandBuy']=stock[stock['date'].isin(buyDate1)]['close']
        stock['bandSell']=stock[stock['date'].isin(sellDate1)]['close']
# 波段结束# 
#macd金叉+21海龟法则开始#突破暴力上涨，假突破多        
        stock['vol_21Mean']= stock['vol'].rolling(21).mean()#21天突破就21天量均值吧
        mark=[0,0,0,0]
        ATR=[0]
        buyDate=[]
        sellDate=[]
        buy_sell=[0,0,0,0]
        band_max[0]=-99
        ATR_max[0]=0
        price_mark=[0,0]
        def func_trend(pam):#  & (pam['MA120_up'] > 0) & (pam['close'] > pam['MA120']) 历史新高才买入 201120 & (pam['historyHigh'] > 0)
            mark[2] += 1
            #均线粘合
            if(abs(pam['MA5'] - pam['MA10'])/pam['MA5'] <0.03)&(abs(pam['MA5'] - pam['MA20'])/pam['MA5'] <0.03):
                mark[3] = mark[2]
                mark[1]=1

            if (mark[3]>0) & (mark[2]-mark[3] > 21):
                mark[1]=0
                mark[3]=0
            #滤嘴：周线柱子向上 + 144天乖离率小于21%,都是斐波那契  真不知道会涨到哪去  突破需要1.21倍的21天成交量均值
            if (mark[0]==0)  & (pam['MA120_up'] > 0) &(pam['high'] != pam['low']) :
                if (mark[1]==1)  &(pam['close'] > pam['turtleMax']) & (pam['vol'] > 1.13*pam['vol_21Mean']):#加上概率密度，时长和幅度过滤1125
                    buy_sell[0]=pam['close']
                    buy_sell[1]=pam['close']
                    buyDate.append(pam['date'])
                    ATR[0]=pam['ATR']
                    mark[0]=1
                    mark[1]=0
            if mark[0] != 0:
                if (pam['high']>band_max[0]):#求出买进后的最大值
                    band_max[0]=pam['high']
                    ATR_max[0]=pam['ATR']
                if (band_max[0] - buy_sell[1])/ buy_sell[1] > 0.5:
                        buy_sell[2]= buy_sell[1] + 0.7*(band_max[0] - buy_sell[1])
                #加仓 3次
                if (mark[0]<4) & (pam['close'] > (buy_sell[0]+1*ATR[0]))  & (pam['high'] != pam['low']) :
                    buy_sell[0]=pam['close']
                    buyDate.append(pam['date'])
                    ATR[0]=pam['ATR']
                    mark[0] += 1
                # if (pam['close'] < (buy_sell[0]-1.5*ATR[0])) | (pam['close'] < pam['turtleOut']) |(pam['macd_death'] >0):
                if (pam['high'] != pam['low']) &((pam['close'] < (buy_sell[0]-3*ATR[0])) | (pam['close'] < buy_sell[2]) |(pam['close'] < pam['turtleOut'])):
                    #止损或卖出止盈   | (pam['macd_sell'] > 0) 宽点止损
                    sellDate.append(pam['date'])
                    mark[0] = 0
                    band_max[0]=-99
                    buy_sell[2]=-99
    #使用apply的用法，进行循环
        stock.apply(func_trend,axis=1)
        stock['turtleBuy']=stock[stock['date'].isin(buyDate)]['close']
        stock['turtleSell']=stock[stock['date'].isin(sellDate)]['close']
#海龟法结束#
#######波段买卖回测开始#######
        per_share=200000 * 0.004  #总钱数20万，风险因子是0.4%
        stock['band_num']=0
        stock['band_num']=np.where(stock['bandBuy']>0,(per_share*0.01 // (stock['ATR']))*100,0) #买入股数
        stock['band_money']=-1*stock['bandBuy']*stock['band_num'] #买入钱数,减掉
        stock['band_tax']=0
        stock['band_profit']=0
        stock['band_days']= 0
        days= 0#持仓天数
        band_num=[0]
        band_money=[0]
        for row in range(length):
            if days !=0 :
                days += 1 #有买入后就累加天数
            if stock.loc[row,'band_num'] >0:
                if days ==0 :
                    days += 1 #买入当天开始计天数
                band_num[0] += stock.loc[row,'band_num']#建仓持股数
                stock.loc[row,'band_tax']= (stock.loc[row,'band_money']* 0.0003)#佣金
                if stock.loc[row,'band_tax'] > -5:
                    stock.loc[row,'band_tax']= -5
                stock.loc[row,'band_money'] += stock.loc[row,'band_tax']#加上佣金成本
                band_money[0] += stock.loc[row,'band_money']#市值额
                # stock.loc[row,'band_profit']=stock.loc[row,'close'] * band_num[0] + band_money[0]#利润
            if stock.loc[row,'bandSell'] > 0:
                stock.loc[row,'band_days']= days #持仓天数
                stock.loc[row,'band_num']= -1*band_num[0] #卖出股数
                stock.loc[row,'band_money']= stock.loc[row,'close'] * band_num[0]#卖出额
                t=stock.loc[row,'band_money']* 0.0003
                t=( t if t > 5 else 5)
                stock.loc[row,'band_tax']= -1*stock.loc[row,'band_money']* (0.001+0.00002) -t #佣金+印花税+过户费
                stock.loc[row,'band_money'] += stock.loc[row,'band_tax']#减去佣金税费
                band_money[0] += stock.loc[row,'band_money']#利润计算
                stock.loc[row,'band_profit'] = band_money[0]#利润
                band_num[0] = 0
                band_money[0]=0
                days=0
########波段买卖回测结束#############
#######突破买卖回测开始#######
        stock['turtle_num']=0
        stock['turtle_num']=np.where(stock['turtleBuy']>0,(per_share*0.01 // (stock['ATR']))*100,0) #买入股数
        stock['turtle_money']=-1*stock['turtleBuy']*stock['turtle_num'] #买入钱数,减掉
        stock['turtle_tax']=0
        stock['turtle_profit']=0
        stock['turtle_days']= 0
        days= 0#持仓天数
        turtle_num=[0]
        turtle_money=[0]
        for row in range(length):
            if days !=0 :
                days += 1 #有买入后就累加天数
            if stock.loc[row,'turtle_num'] >0:
                if days ==0 :
                    days += 1 #买入当天开始计天数
                turtle_num[0] += stock.loc[row,'turtle_num']#建仓持股数
                stock.loc[row,'turtle_tax']= (stock.loc[row,'turtle_money']* 0.0003)#佣金
                if stock.loc[row,'turtle_tax'] > -5:
                    stock.loc[row,'turtle_tax']= -5
                stock.loc[row,'turtle_money'] += stock.loc[row,'turtle_tax']#加上佣金成本
                turtle_money[0] += stock.loc[row,'turtle_money']#市值额
                # stock.loc[row,'turtle_profit']=stock.loc[row,'close'] * turtle_num[0] + turtle_money[0]#利润
            if stock.loc[row,'turtleSell'] > 0:
                stock.loc[row,'turtle_num']= -1*turtle_num[0] #卖出股数
                stock.loc[row,'turtle_money']= stock.loc[row,'close'] * turtle_num[0]#卖出额
                t=stock.loc[row,'turtle_money']* 0.0003
                t=( t if t > 5 else 5)
                stock.loc[row,'turtle_tax']= -1*stock.loc[row,'turtle_money']* (0.001+0.00002) -t #佣金+印花税+过户费
                stock.loc[row,'turtle_money'] += stock.loc[row,'turtle_tax']#减去佣金税费
                turtle_money[0] += stock.loc[row,'turtle_money']#利润计算
                stock.loc[row,'turtle_profit'] = turtle_money[0]#利润
                stock.loc[row,'turtle_days']= days #持仓天数
                days=0
                turtle_num[0] = 0
                turtle_money[0]=0
########突破买卖回测结束#############
        stock.to_csv('G:\\stockData\\myData\\'+code+'.csv')
        elapsed = time.perf_counter() - start
        print(code+' '+backTraceDate+" Time used:",elapsed)
        if isShow==0:
            return (stock.tail(1))
             
###画图开始
        spaceDays=10 #显示间隔日期数
        stock=stock[stock['date']>'2018-01-01']#选择回测的截止日期数据
        stock =stock.reset_index(drop=True)#去掉原序，重新0开始
        length=len(stock)
        quotes = []
        for row in range(length):
            sdate_plt = stock.index.values[row] #提取索引单个值             
            sopen = stock.loc[row,'open']
            shigh = stock.loc[row,'high']
            slow = stock.loc[row,'low']
            sclose = stock.loc[row,'close']
            datas = (sdate_plt,sopen,shigh,slow,sclose) # 按照 candlestick_ohlc 要求的数据结构准备数据
            quotes.append(datas)
        x_ticks = [i[0] for i in quotes]#从list矩阵里取出列元素的方法   

        # fig, ax = plt.subplots(facecolor=(0, 0.3, 0.5),figsize=(12,8))
        # fig.subplots_adjust(bottom=0.1)
        plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签 
        plt.rcParams['axes.unicode_minus']=False #用来正常显示负号 
        fig = plt.figure(figsize=(20,12), dpi=100,facecolor="white") #创建fig对象
        gs = gridspec.GridSpec(1, 1, left=0.05, bottom=0.12, right=0.98, top=0.96, wspace=None, hspace=0.2)#, height_ratios=[3.5,1,1,1]
        graph_KAV = fig.add_subplot(gs[0,:])
        # graph_VOL = fig.add_subplot(gs[1,:])
        # graph_MACD = fig.add_subplot(gs[1,:])
        # graph_KDJ = fig.add_subplot(gs[3,:])
        # 添加网格
        graph_KAV.grid(True)       
        graph_KAV.set_title(code)
        mpf.candlestick_ohlc(graph_KAV,quotes,width=0.7,colorup='r',colordown='green') # 上涨为红色K线，下跌为绿色，K线宽度为0.7
#        #绘制K线图
        # mpf.candlestick2_ochl(graph_KAV, stock.open, stock.close, stock.high, stock.low, width=0.5,colorup='r', colordown='g')  # 绘制K线走势
        # plt.grid(True)#网格
        #绘制成交量图
        # graph_VOL.bar(np.arange(0, length), stock.vol,color=['g' if stock.open[x] > stock.close[x] else 'r' for x in range(0,length)])
        # # graph_VOL.set_ylabel(u"成交量")
        # graph_VOL.set_xlim(0,length) #设置一下x轴的范围
        # graph_VOL.set_xticks(range(0,length,spaceDays))#X轴刻度设定 每15天标一个日期
 #绘制MACD
        # macd_dif, macd_dea, macd_bar = talib.MACD(stock['close'].values, fastperiod=21, slowperiod=55, signalperiod=13)
        # graph_MACD.plot(np.arange(0, length), stock['macd_dif'], 'red', label='macd dif')  # dif
        # graph_MACD.plot(np.arange(0, length), stock['macd_dea'], 'blue', label='macd dea')  # dea
        # bar_red = np.where(stock['macd_bar'] > 0, 2 * stock['macd_bar'], 0)# 绘制BAR>0 柱状图
        # bar_green = np.where(stock['macd_bar'] < 0, 2 * stock['macd_bar'], 0)# 绘制BAR<0 柱状图
        # graph_MACD.bar(np.arange(0, length), bar_red, facecolor='red')
        # graph_MACD.bar(np.arange(0, length), bar_green, facecolor='green')
        # graph_MACD.legend(loc='best',shadow=True, fontsize ='10')
        # # graph_MACD.set_ylabel(u"MACD")
        # graph_MACD.grid(True)
        # # graph_MACD.set_xlim(0,length) #设置一下x轴的范围
        # graph_MACD.set_xticks(range(0,length,spaceDays))#X轴刻度设定 每10天标一个日期

#        # graph_KAV.plot(x_ticks,stock['MA5'],'m')
        graph_KAV.plot(x_ticks,stock['MA5'],'b')
        # graph_KAV.plot(x_ticks,stock['MA10'] ,'y')#画出5/10金叉
        graph_KAV.plot(x_ticks,stock['MA120'],'k')
        graph_KAV.plot(x_ticks,stock['middleBoll'],'m--')#这样可以加进去新的线
        # graph_KAV.plot(x_ticks,stock['upBoll'],'r')
        # graph_KAV.plot(x_ticks,stock['downBoll'],'g')
        graph_KAV.plot(x_ticks, stock['buyBoll'],'y.',markersize=9,label = "buyBoll")#标志处买点
        graph_KAV.plot(x_ticks, stock['sellBoll'],'k.',markersize=9)#标志处卖点 ,label = "sellBoll"
#        #ma5谷底
        # graph_KAV.plot(x_ticks, stock['buyValleyMA5'],'y^',markersize=9,label = "buyValleyMA5")
        #ma5峰顶
        # graph_KAV.plot(x_ticks, stock['sellPeakMA5'],'kv',markersize=9,label = "sellPeakMA5")
        
        # graph_KAV.plot(x_ticks,stock['sellDeathCross'] ,'c*',markersize=9,label = "sellDeathCross")#画出10\5死叉
        # graph_KAV.plot(x_ticks, stock['buyValleyMA20'],'y*',markersize=9,label = "buyValleyMA20")#
        # graph_KAV.plot(x_ticks, stock['buyUpMA20'],'yx',markersize=15,label = "buyUpMA20")#
        # graph_KAV.plot(x_ticks, stock['sellDownMA20'],'k*',markersize=7,label = "sellDownMA20")#
        # graph_KAV.plot(x_ticks, stock['sellPeakMA20'],'k.',markersize=10,label = "sellPeakMA20")#
#        # graph_KAV.plot(x_ticks,stock['buyUpMA120'] ,'y>',markersize=9,label = "buyUpMA120")#
        graph_KAV.plot(x_ticks,stock['buyBIAS120'] ,'y+',markersize=18,label = "buyBIAS120")#画出乖离率都大的
        graph_KAV.plot(x_ticks,stock['sellBIAS120'] ,'k+',markersize=18)#画出乖离率都大的 ,label = "sellBIAS120"
        graph_KAV.plot(x_ticks, stock['turtleBuy'],'y*',markersize=9,label = "turtleBuy")
        graph_KAV.plot(x_ticks, stock['turtleSell'],'k*',markersize=9)# ,label = "turtleSell"
        # graph_KAV.plot(x_ticks, stock['valley'],'b2',markersize=22,label = "valley")
        # graph_KAV.plot(x_ticks, stock['peak'],'k1',markersize=22)# ,label = "peak"
        # graph_KAV.plot(x_ticks, stock['macd_gold'],'y*',markersize=9,label = "macd_gold")
        # graph_KAV.plot(x_ticks, stock['macd_death'],'k*',markersize=9)
        graph_KAV.plot(x_ticks, stock['bandBuy'],'y^',markersize=9,label = "bandBuy")
        graph_KAV.plot(x_ticks, stock['bandSell'],'kv',markersize=9)# ,label = "peak"
        # graph_KAV.plot(x_ticks, stock['macd_death'],'k*',markersize=9,label = "macd_death")
        # graph_KAV.plot(x_ticks, stock['trend_close_up'],'r')
        # graph_KAV.plot(x_ticks, stock['trend_close_down'],'g')

        #同图绘制KDJ
        b=stock['low'].min()#平移小于最小值以下
        b=0.618 *b #黄金比例
        coef=(stock.loc[stock.index.max(),'close'])#放大的倍率
        coef=0.1 *coef
        # graph_KAV.plot(x_ticks, coef*stock['K']+b, 'y', label='K')  # K
        # graph_KAV.plot(x_ticks, coef*stock['D']+b, 'c-', label='D')  # D
        # graph_KAV.plot(x_ticks, coef*stock['J']+b, 'm-', label='J')  # J
        # graph_KAV.axhline(y=coef*0.8+b, color='r', linestyle='-')#超买线
        # graph_KAV.axhline(y=coef*0.2+b, color='g', linestyle='-')#超卖线
        #同图绘制MACD
        #归一化映射到(-1,1)内
        macd_dif_max=stock['macd_dif'].max()
        macd_dif_min=stock['macd_dif'].min()
        stock['macd_dif'] = -1 + 2 / (macd_dif_max - macd_dif_min) * (stock['macd_dif'] - macd_dif_min)
        macd_dea_max=stock['macd_dea'].max()
        macd_dea_min=stock['macd_dea'].min()
        stock['macd_dea'] = -1 + 2 / (macd_dea_max - macd_dea_min) * (stock['macd_dea'] - macd_dea_min)
        macd_bar_max=stock['macd_bar'].max()
        macd_bar_min=stock['macd_bar'].min()
        stock['macd_bar'] = -1 + 2 / (macd_bar_max - macd_bar_min) * (stock['macd_bar'] - macd_bar_min)
        
        b=stock['low'].min()#平移小于最小值以下
        b=0.55 *b
        coef=(stock.loc[stock.index.max(),'close'])#放大的倍率
        coef=0.0618 *coef
        graph_KAV.plot(x_ticks, coef*stock['macd_dif']+b, 'red', label='macd_dif')  # dif
        graph_KAV.plot(x_ticks, coef*stock['macd_dea']+b, 'blue', label='macd_dea')  # dea
        stock['bar_red'] = np.where(stock['macd_bar'] > 0,  stock['macd_bar'], 0)# 绘制BAR>0 柱状图
        stock['bar_green'] = np.where(stock['macd_bar'] < 0, stock['macd_bar'], 0)# 绘制BAR<0 柱状图
        graph_KAV.bar(x_ticks, coef*stock['bar_red'], bottom=b, facecolor='red')#上移0轴 bottom=b
        graph_KAV.bar(x_ticks, coef*stock['bar_green'], bottom=b,facecolor='green')
          ######实际买卖点位的可视检测开始##########  
        filename3='G:\\stockData\\tradeInfo\\'+code+'.csv'
        ex=os.path.isfile(filename3)  #当前文件是否存在
        if ex==True:
            try:
                df3=pd.read_csv(filename3,encoding='utf_8_sig')#
                df3=df3[(df3['bandBuy']>0) | (df3['bandSell']>0)]
                stock['trade']=stock[stock['date'].isin(list(df3['date']))]['close']
                graph_KAV.plot(x_ticks,stock['trade'] ,'c+',markersize=15,label = "trade")#显示实际买卖点
            except Exception as err:
                print('read_csv err', err)
   ######实际操作可视化结束######## 
        # graph_KAV.set_xlim(0,length) #设置一下x轴的范围
        graph_KAV.legend(loc='best', shadow=True, fontsize='10') #主图生成的标签       
        # 生成横轴的刻度名字
        date_tickers=stock.date.values#日期
        def format_date(x,pos=None):#把int的x刻度转回日期格式y-m-d，回调函数
            if x<0 or x>len(date_tickers)-1:
                return ''
            return date_tickers[int(x)]
        graph_KAV.xaxis.set_major_locator(ticker.MultipleLocator(spaceDays))#原始显示间距6
        graph_KAV.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))#重设x轴日期格式
#        # graph_MACD.xaxis.set_major_locator(ticker.MultipleLocator(spaceDays))#原始显示间距6
        # graph_MACD.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))#重设x轴日期格式
    
        #绘制KDJ
        # stock['K'], stock['D'] = talib.STOCH(stock.high.values, stock.low.values, stock.close.values,\
        #     fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        # stock['J'] = 3 * stock['K'] - 2 * stock['D']
        # graph_KDJ.plot(np.arange(0, length), stock['K'], 'blue', label='K')  # K
        # graph_KDJ.plot(np.arange(0, length), stock['D'], 'g--', label='D')  # D
        # graph_KDJ.plot(np.arange(0, length), stock['J'], 'r-', label='J')  # J
        # graph_KDJ.legend(loc='best', shadow=True, fontsize='8')
        # # graph_KDJ.set_ylabel(u"KDJ")
        # # graph_KDJ.set_xlabel(u"日期")
        # graph_KDJ.set_xlim(0, length)  # 设置一下x轴的范围
        # graph_KDJ.set_xticks(range(0, length, spaceDays))  # X轴刻度设定 每15天标一个日期
        # graph_KDJ.set_xticklabels([stock.index.strftime('%Y-%m-%d')[index] for index in graph_KDJ.get_xticks()])  # 标签设置为日期

        # X-轴每个ticker标签都向右倾斜45度,修饰图片
        # for label in graph_KDJ.xaxis.get_ticklabels():
        #     label.set_visible(False)
        # for label in graph_VOL.xaxis.get_ticklabels():
        #     label.set_visible(False)
        # for label in graph_MACD.xaxis.get_ticklabels():
        #     # label.set_visible(False)
        #     label.set_rotation(45)
#        #     label.set_fontsize(10)  # 设置标签字体
        for label in graph_KAV.xaxis.get_ticklabels():
            label.set_rotation(45)
            label.set_fontsize(11)  # 设置标签字体

        plt.legend()
        plt.show()
        return (pd.DataFrame())


if __name__=='__main__':
    test=kLine()
    code='000001_test'#指数和股票还是有些区别的，名称不一样
    # test.drawKLine(code)
    filePath='G:\\stockData\\'
    backTraceDate='2020-08-08'
    df=pd.read_csv('G:\\stockData\\'+code+'.csv')
    i=len(df)-1
    print(df.loc[i,'date'])
    df.loc[i,'open']=11
    print(df.iloc[-1]['open'])
    print(df.iloc[1]['open'])
    # test.myDrawKLine(filePath,code,backTraceDate,True)