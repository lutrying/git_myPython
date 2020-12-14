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
import os
from strategy import *
from myOperator2 import *

def myRead_csv(_code):
    code=_code
    filename3='G:\\stockData\\myData\\'+code
    try:
        df = pd.read_csv(filename3,encoding='utf_8_sig')#index_col=flase 不会将第一列作为index ,converters={'trade_date':str}
        pass
    except Exception as err:
        print('myRead_csv err', err)
    return df
def myPlot(_code):#画图单个显示K线
    code=_code
    stock= myRead_csv(code)
    start = time.perf_counter()#计时开始
 ###画图开始
    spaceDays=10 #显示间隔日期数
    # stock=stock[stock['date']>'2016-01-01']#选择回测的截止日期数据
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

    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签 
    plt.rcParams['axes.unicode_minus']=False #用来正常显示负号 
    fig = plt.figure(figsize=(20,12), dpi=100,facecolor="white") #创建fig对象
    gs = gridspec.GridSpec(1, 1, left=0.05, bottom=0.12, right=0.98, top=0.96, wspace=None, hspace=0.2)#, height_ratios=[3.5,1,1,1]
    graph_KAV = fig.add_subplot(gs[0,:])

    # 添加网格
    graph_KAV.grid(True)       
    graph_KAV.set_title(code)
    mpf.candlestick_ohlc(graph_KAV,quotes,width=0.5,colorup='r',colordown='green') # 上涨为红色K线，下跌为绿色，K线宽度为0.7

    graph_KAV.plot(x_ticks,stock['MA5'],'b')
    # graph_KAV.plot(x_ticks,stock['MA10'] ,'y')#画出5/10金叉
    graph_KAV.plot(x_ticks,stock['MA120'],'k')
    graph_KAV.plot(x_ticks,stock['middleBoll'],'m--')#这样可以加进去新的线
    # graph_KAV.plot(x_ticks,stock['upBoll'],'r')
    # graph_KAV.plot(x_ticks,stock['downBoll'],'g')
    # graph_KAV.plot(x_ticks, stock['buyBoll'],'y.',markersize=11,label = "buyBoll")#标志处买点
    # graph_KAV.plot(x_ticks, stock['sellBoll'],'k.',markersize=11)#标志处卖点 ,label = "sellBoll"
    graph_KAV.plot(x_ticks,stock['buyBIAS120'] ,'y+',markersize=18,label = "buyBIAS120")#画出乖离率都大的
    graph_KAV.plot(x_ticks,stock['sellBIAS120'] ,'k+',markersize=18)#画出乖离率都大的 ,label = "sellBIAS120"
    graph_KAV.plot(x_ticks, stock['turtleBuy'],'y*',markersize=9,label = "turtleBuy")
    graph_KAV.plot(x_ticks, stock['turtleSell'],'k*',markersize=9)# ,label = "turtleSell"
    graph_KAV.plot(x_ticks, stock['bandBuy'],'y^',markersize=9,label = "bandBuy")
    graph_KAV.plot(x_ticks, stock['bandSell'],'kv',markersize=9)# ,label = "peak"
    #同图绘制KDJ
    b=stock['low'].min()#平移小于最小值以下
    b=0.618 *b #黄金比例
    coef=(stock.loc[stock.index.max(),'close'])#放大的倍率
    coef=0.1 *coef
    # graph_KAV.plot(np.arange(0, length), coef*stock['K']+b, 'y', label='K')  # K
    # graph_KAV.plot(np.arange(0, length), coef*stock['D']+b, 'c-', label='D')  # D
    # graph_KAV.plot(np.arange(0, length), coef*stock['J']+b, 'm-', label='J')  # J
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
    b=0.382 *b
    coef=(stock.loc[stock.index.max(),'close'])#放大的倍率
    coef=0.0618 *coef
    # graph_KAV.plot(np.arange(0, length), coef*stock['macd_dif']+b, 'red', label='macd_dif')  # dif
    # graph_KAV.plot(np.arange(0, length), coef*stock['macd_dea']+b, 'blue', label='macd_dea')  # dea
    # stock['bar_red'] = np.where(stock['macd_bar'] > 0,  stock['macd_bar'], 0)# 绘制BAR>0 柱状图
    # stock['bar_green'] = np.where(stock['macd_bar'] < 0, stock['macd_bar'], 0)# 绘制BAR<0 柱状图
    # graph_KAV.bar(np.arange(0, length), coef*stock['bar_red'], bottom=b, facecolor='red')#上移0轴 bottom=b
    # graph_KAV.bar(np.arange(0, length), coef*stock['bar_green'], bottom=b,facecolor='green')
      ######实际买卖点位的可视检测开始##########  
    filename3='G:\\stockData\\tradeInfo\\'+code[:6]+'.csv'
    ex=os.path.isfile(filename3)  #当前文件是否存在
    if ex==True:
        try:
            df3=pd.read_csv(filename3,encoding='utf_8_sig')#
            df3=df3[(df3['bandBuy']>0) | (df3['bandSell']>0)]
            stock['trade']=stock[stock['date'].isin(list(df3['date']))]['close']
            graph_KAV.plot(x_ticks,stock['trade'] ,'c+',markersize=15,label = "trade")#显示实际买卖点
        except Exception as err:
            print('read_csv err', err)
   ##实际操作可视化结束######## 
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

    for label in graph_KAV.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_fontsize(11)  # 设置标签字体

    plt.legend()
    plt.show()
########
def everyDayOperatorT(_date):##合并所有的交易数据，买卖信息，个股是分开存放的所以要合并
    path1='G:\\stockData\\tradeInfo\\'
    path2='G:\\stockData\\test\\'
    files= os.listdir(path1) #得到文件夹下的所有文件名称
    for code in files: #遍历文件夹
        print(code+' start')
        filename=path1+code  
        try:     
            df=pd.read_csv(filename)#,encoding='utf_8_sig'
            df=df.drop_duplicates()#删除重复行
        except Exception as err:
            print(filename+'read_csv err', err)
        # df=df.tail(1)
        df=df[(df['date']==_date) & (df['buy']> 0)]
        if len(df)==0:
            continue
        ex=os.path.isfile(path2+_date+'.csv')  #当前文件是否存在，存在即添加，不存在新建
        if ex==False :            
            df.to_csv(path2+_date+'.csv',index=None,encoding='utf_8_sig')#新建保存每个的数据  
        else :
            df.to_csv(path2+_date+'.csv',mode='a',index=None,header=False,encoding='utf_8_sig')#后尾追加保存每个的数据  
    print(_date+':everydayList finish')
# everyDayOperatorT('2020-12-08')

def buy_sellResult(df,buyName):#显示买卖回测数据统计结果
    df=df[(df['buy']>0) | (df['sell']>0)]#选出交易数据
    df =df.reset_index(drop=True)#去掉原序，重新0开始   
    df['profit_curve'] = df['profit'].cumsum()#资金曲线
    allTimes = len(df[(df['sell']>0)]) 
    if allTimes==0:
        return
    df.loc[0,'allTimes']= allTimes #卖出次数作为总次数
    winTimes= len(df[(df['profit']>0)])
    df.loc[0,'winTimes']= winTimes #盈利次数
    df.loc[0,'winRate']= winTimes / allTimes#胜率
    df.loc[0,'allMoney']= df[df['sell']>0]['money'].sum()#总盈利额
    df.loc[0,'allProfits']= df['profit'].sum()#总盈利额
    df.loc[0,'Risk']= (df['profit'].sum() / allTimes) / 800 #Risk 盈亏比 800= 200000 * 0.4% :总资产*风险因子
    q=df['days'].sum()
    df.loc[0,'daysMean']= (df['days'].sum() / allTimes)#持仓平均天数
    df.loc[0,'maxWin']= df['profit'].max()
    df.loc[0,'maxLose']= df['profit'].min()
    tempMax = -9999999
    maxReturn = -9999999#最大回撤
    for row in range(len(df)):#
        if df.loc[row,'profit_curve'] > tempMax:
            tempMax = df.loc[row,'profit_curve']
        if df.loc[row,'profit_curve'] <= tempMax:
            t= (tempMax - df.loc[row,'profit_curve'])
            if t > maxReturn:
                maxReturn = t
    df.loc[0,'maxReturn']= maxReturn #最大回撤
    code =(df.loc[0,'ts_code'])
    filename='G:\\stockData\\tradeInfo\\'+ code + '_'+buyName+'.csv'
    df.to_csv(filename,index=None,encoding='utf_8_sig')#新建保存每个的数据
    # df=df.loc[0,:] #取单行时默认返回series
    df=df.loc[[0]] #即可返回一个dataframe
    df=df[['ts_code','allTimes','winTimes','winRate','allMoney','allProfits','Risk','daysMean','maxWin','maxLose','maxReturn']]
    # df= df[df['allTimes']>0]
    filename = 'G:\\stockData\\test\\'+buyName+'.csv'
    ex=os.path.isfile(filename)  #当前文件是否存在，存在即添加，不存在新建
    if ex==False:            
        df.to_csv(filename,index=None,encoding='utf_8_sig')#新建保存每个的数据  
    else :
        pass
        df.to_csv(filename,mode='a',index=None,header=False,encoding='utf_8_sig')#后尾追加保存每个的数据
        # df1 = pd.read_csv(filename,encoding='utf_8_sig')#index_col=0 不新设index
        # df1=df.drop_duplicates(['ts_code']) #去掉重复的行
        # df1.to_csv(filename,index=None,encoding='utf_8_sig')#新建保存每个的数据


def myFor():#显示mydata文件下所有回测数据
    # path1='G:\\stockData\\myData\\'
    path1='G:\\stockData\\tradeInfo\\'
    files= os.listdir(path1) #得到文件夹下的所有文件名称
    files=[(x[:6] + '.csv') for x in files]
    files=list(set(files))#set 可以去重复
    # files=['000629.csv']
    for code in files: #遍历文件夹
        myPlot(code)
# myFor()

def myFor1():#显示回测完成结果，有交易数据
    # everyDayOperatorT('test') #合并买卖所以个股数据  已经不用合并啦-20201119
    filename='G:\\stockData\\test\\120up&all_macd金叉死叉2.csv'
    try:
        df=pd.read_csv(filename,encoding='utf_8_sig')#新建保存每个的数据
    except Exception as err:
        print('myFor1 read_csv err', err) 
    codeList=list(df['ts_code'])
    for code in codeList: #遍历文件夹
        code=code[:6]+'.csv'
        myPlot(code)
myFor1()

def myFor3(filename):#统计回测数据：所有个股30年数据的成功率 、 交易次数、盈亏比R、盈利总数，并分别R和盈利总数排序，画出盈利曲线
    start = time.perf_counter()#计时开始
    print('count start....')
    path1='G:\\stockData\\myData\\'
    filename='allStockList' # allStockList  sz50s  zz500s hs300s
    codeList= stockList(filename) #得到目标股票池下的所有代码名称
    for code in codeList: #遍历文件夹
        try:
            code= code+'.csv'
            print(code + '  count start....')
            df= myRead_csv(code)
            df1=df.copy()
            #band
            df= df[['ts_code','date','ATR','top_level','buttom_level','bandBuy','bandSell','band_num','band_money','band_tax','band_profit','band_days']]
            df= df.rename(columns={'bandBuy': 'buy','bandSell': 'sell','band_num': 'num','band_money': 'money','band_tax': 'tax','band_profit': 'profit','band_days': 'days'})#选择性更改列名
            buyName='120up&all_macd金叉死叉2'
            buy_sellResult(df,buyName)#band
            #21 turtle
            df1= df1[['ts_code','date','ATR','turtleBuy','turtleSell','turtle_num','turtle_money','turtle_tax','turtle_profit','turtle_days']]
            df1= df1.rename(columns={'turtleBuy': 'buy','turtleSell': 'sell','turtle_num': 'num','turtle_money': 'money','turtle_tax': 'tax','turtle_profit': 'profit','turtle_days': 'days'})#选择性更改列名
            buyName='120up&allStockList_55天唐奇安突破0.618'
            # buy_sellResult(df1,buyName)
            # myPlot(code)#显示K线
        except Exception as err:
            print(code +'read_csv err', err)
            continue
    print('...count end...')
    elapsed = time.perf_counter() - start
    print("all Time used:",elapsed)        
myFor3('1')
# everyDayOperatorT('2020-12-11')
#
def chooseNewHigh1(beforeDays):#龙头选股,更新每天的历史新高股
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
        # today='20201126'
        filename1 = 'G:\\stockData\\newHighPool\\'+ today +'.csv'
        ex=os.path.isfile(filename1)  #当前文件是否存在，存在即添加，不存在新建
        d=str(df.iloc[-1]['trade_date'])
        if  d== today :
            # length=len(df)
            m=df['high'].max()
            for row in  range(-beforeDays,-1):
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
# chooseNewHigh1(5)
#       