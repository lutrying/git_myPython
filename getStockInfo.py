
"""
Created on Sat Jul 25 09:35:47 2020

@author: lu
"""

import datetime
import tushare as ts
import pymysql
import baostock as bs
import pandas as pd
import time
import os



# 获取股票的信息
class getStockInfo:
    # 类的构造函数
    def __init__(self):
        # 设置tushare pro的token并获取连接
        ts.set_token('19cf1077f3823655b388a7b92ef066a406293ae2ed656dfb2a524cd9')
        self.pro = ts.pro_api()
        # df = self.pro.daily(trade_date='20200325')
        # pass

# 数据库连接
    def initMysqlConn(self):
        # 建立数据库连接,剔除已入库的部分
        self.db = pymysql.connect(
        host='127.0.0.1', user='root', passwd='1', db='stock', charset='utf8')
        self.cursor = self.db.cursor()

    # 获取所有的股票信息列表
    def getAllStockList(self):
        try:
          self.initMysqlConn()
         # 查询当前所有正常上市交易的股票列表
          df = self.pro.stock_basic(
              exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
          df.to_csv('G:\\stockData\\allStockList.csv',encoding='utf_8_sig')#指数直接覆盖掉
          return
          c_len = df.shape[0]  # 行数
        except Exception as aa:
            print(aa)
            print('get error')
        for j in range(c_len):  # 按行读取股票列表
            resu0 = list(df.loc[c_len-1-j])
            resu = []
            for k in range(len(resu0)):  # 读取股票的字段
                if str(resu0[k]) == 'nan':
                    resu.append(-1)
                else:
                    resu.append(resu0[k])
            try:
                sql_insert = "INSERT INTO allStockList(ts_code,symbol,name,area,industry,list_date) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (
                    str(resu[0]), str(resu[1]), str(resu[2]), str(resu[3]), str(resu[4]), str(resu[5]))
                self.cursor.execute(sql_insert)
                self.db.commit()
            except Exception as err:
                continue
        self.cursor.close()
        self.db.close()
        print('getAllStockList Finished!')

# 获取A50成分股列表
    def getA50StockList(self):
        try:
          self.initMysqlConn()
         # 查询当前所有正常上市交易的股票列表
          df = ts.get_sz50s()  # 不能用了？返回值是none
        # 登陆系统
          lg = bs.login()
          rs = bs.query_sz50_stocks()
          # 打印结果集
          sz50_stocks = []
          while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            sz50_stocks.append(rs.get_row_data())
          result = pd.DataFrame(sz50_stocks, columns=rs.fields)
        #   result['code']='\t'+result['code'].str[3:]
        #   ex=os.path.isfile('sz50s')
        #   if ex==False:
          result.to_csv('G:\\stockData\\sz50s.csv',encoding='utf_8_sig')#指数直接覆盖掉
          rs = bs.query_hs300_stocks()
          # 打印结果集
          hs300_stocks = []
          while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            hs300_stocks.append(rs.get_row_data())
          result1 = pd.DataFrame(hs300_stocks, columns=rs.fields)
        #   result1['code']=result1['code'].str[3:]
        #   ex=os.path.isfile('sz50s')
        #   if ex==False:
          result1.to_csv('G:\\stockData\\hs300s.csv',encoding='utf_8_sig')#指数直接覆盖掉
          # result1.to_csv('G:\\stockData\\hs300s.csv',encoding='gbk')#指数直接覆盖掉
          rs = bs.query_zz500_stocks()
          # 打印结果集
          zz500_stocks = []
          while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            zz500_stocks.append(rs.get_row_data())
          result2 = pd.DataFrame(zz500_stocks, columns=rs.fields)
        #   result2['code']=result2['code'].str[3:]#没有t的话会丢掉前面的0
        #   ex=os.path.isfile('sz50s')
        #   if ex==False:
          result2.to_csv('G:\\stockData\\zz500s.csv',encoding='utf_8_sig')#指数直接覆盖掉
          # 登出系统
          bs.logout()
          print('getsz50StockList & hs300s & zz500s Finished!')
          return
          c_len = 0
          if(df == None):
              df = result
          c_len = df.shape[0]  # 行数
        except Exception as aa:
            print(aa)
            print('get error')
        for j in range(c_len):  # 按行读取股票列表
            resu0 = list(df.loc[c_len-1-j])
            resu = []
            for k in range(len(resu0)):  # 读取股票的字段
                if str(resu0[k]) == 'nan':
                    resu.append(-1)
                else:
                    resu.append(resu0[k])
            try:
                sql_insert = "INSERT INTO sz50StockList(date,code,name) VALUES ('%s', '%s', '%s')" % (
                    str(resu[0]), str(resu[1]), str(resu[2]))
                self.cursor.execute(sql_insert)
                self.db.commit()
            except Exception as err:
                continue
        self.cursor.close()
        self.db.close()
        # 登出系统
        bs.logout()
        print('getsz50StockList Finished!')

# 获取沪深300成分股列表
    def getHS300StockList(self):
        try:
          self.initMysqlConn()
         # 查询当前所有正常上市交易的股票列表
          df = ts.get_hs300s()
          df.to_csv('G:\\stockData\\hs300s.csv',encoding='utf_8_sig')
          return
          c_len = df.shape[0]  # 行数
        except Exception as aa:
            print(aa)
            print('get error')
        for j in range(c_len):  # 按行读取股票列表
            resu0 = list(df.loc[c_len-1-j])
            resu = []
            for k in range(len(resu0)):  # 读取股票的字段
                if str(resu0[k]) == 'nan':
                    resu.append(-1)
                else:
                    resu.append(resu0[k])
            try:
                sql_insert = "INSERT INTO hs300StockList(date,code,name,weight) VALUES ('%s', '%s', '%s', '%.2f')" % (
                    str(resu[0]), str(resu[1]), str(resu[2]), float(resu[3]))
                self.cursor.execute(sql_insert)
                self.db.commit()
            except Exception as err:
                continue
        self.cursor.close()
        self.db.close()
        print('geths300StockList Finished!')

# 获取中证500成分股列表
    def getZZ500StockList(self):
        try:
          self.initMysqlConn()
         # 查询当前所有正常上市交易的股票列表
          df = ts.get_zz500s()
          df.to_csv('G:\\stockData\\zz500s.csv',encoding='utf_8_sig')
          return
          c_len = df.shape[0]  # 行数
        except Exception as aa:
            print(aa)
            print('get error')
        for j in range(c_len):  # 按行读取股票列表
            resu0 = list(df.loc[c_len-1-j])
            resu = []
            for k in range(len(resu0)):  # 读取股票的字段
                if str(resu0[k]) == 'nan':
                    resu.append(-1)
                else:
                    resu.append(resu0[k])
            try:
                sql_insert = "INSERT INTO zz500StockList(date,code,name,weight) VALUES ('%s', '%s', '%s', '%.2f')" % (
                    str(resu[0]), str(resu[1]), str(resu[2]), float(resu[3]))
                self.cursor.execute(sql_insert)
                self.db.commit()
            except Exception as err:
                continue
        self.cursor.close()
        self.db.close()
        print('getzz500StockList Finished!')

# 循环获取daily数据，提高稳定性
    def get_daily(self, ts_code='', trade_date='', start_date='', end_date=''):
        for _ in range(3):
            try:
                    if trade_date:
                        df = self.pro.daily(
                            ts_code=ts_code, trade_date=trade_date)
                    else:
                        df = self.pro.daily(
                            ts_code=ts_code, start_date=start_date, end_date=end_date)
            except:
                        time.sleep(1)
            else:
                        return df


# 获取所有股票的每日K线数据
    def getAllStockHistoryData(self,days=1):
        self.initMysqlConn()  # 连接数据库
        print('update all stock data...')
        # 设定获取日线行情的初始日期和终止日期，其中终止日期设定为昨天。
        time_temp = datetime.datetime.now()#今日
        end_dt = time_temp.strftime('%Y%m%d')
        start_dt=(time_temp - datetime.timedelta(days=days)).strftime('%Y%m%d')
        # start_dt = '19901219'
        # end_dt='20201016'
        allStockList = pd.read_csv('G:\\stockData\\allStockList.csv',encoding='utf_8_sig')
        for i in allStockList['ts_code'].values:
            print (i)
            try:
                df = ts.pro_bar(ts_code=i, adj='qfq', start_date=start_dt, end_date=end_dt)
                pass
            except Exception as aa:
                print(aa)
                print('get error')
            filename='G:\\stockData\\originData\\'+i[:6]+'.csv'
            ex=os.path.isfile(filename)  #当前文件是否存在，存在即添加，不存在新建
            if ex==False:
                df.to_csv(filename,encoding='utf_8_sig')#新建保存每个的数据  index=None,
            else :
                df.to_csv(filename,mode='a',header=False,encoding='utf_8_sig')#后尾加保存每个的数据
                df1=pd.read_csv(filename,encoding='utf_8_sig')
                df1=df1.dropna()#删除所有包含空值的行
                # df=df.drop(df.tail(4).index)
                df1=df1.drop_duplicates(['trade_date'])
                df1 = df1.sort_values('trade_date')#降序
                df1.to_csv(filename,index=None,encoding='utf_8_sig')
                
                pass
        print('getAllStockHistoryData Finished!')  
        return
# 获取开始结束之间所有有交易的日期
        df1 = self.pro.trade_cal(exchange='SSE', is_open='1',
                            start_date=start_dt,
                            end_date=end_dt,
                            fields='cal_date')

        # c_len1 = df1.shape[0]#行数
        for date in df1['cal_date'].values:
            try:
                # 查询当天所有正常上市交易的股票数据,这是不复权的数据，不符合要求
                df = self.get_daily(trade_date=date)
                c_len = df.shape[0]  # 行数
            except Exception as aa:
                print(aa)
                print('get error')
            for j in range(c_len):  # 按行读取股票列表
                resu0 = list(df.loc[c_len-1-j])
                resu = []
                for k in range(len(resu0)):  # 读取股票的字段
                    if str(resu0[k]) == 'nan':
                        resu.append(-1)
                    else:
                        resu.append(resu0[k])
                state_dt = (datetime.datetime.strptime(
                    resu[1], "%Y%m%d")).strftime('%Y-%m-%d')
                # try:
                    # sql_insert = "INSERT INTO stock_all(state_dt,stock_code,open,close,high,low,vol,amount,pre_close,amt_change,pct_change) VALUES ('%s', '%s', '%.2f', '%.2f','%.2f','%.2f','%i','%.2f','%.2f','%.2f','%.2f')" % (
                        # state_dt, str(resu[0]), float(resu[2]), float(resu[5]), float(resu[3]), float(resu[4]), float(resu[9]), float(resu[10]), float(resu[6]), float(resu[7]), float(resu[8]))
                    # self.cursor.execute(sql_insert)
                    # self.db.commit()
                # except Exception as err:
                    # continue
        self.cursor.close()
        self.db.close()
        print('getAllStockHistoryData Finished!')


# 获取三个指数的历史数据
    def getAllIndexHistoryData(self,days=1):
        self.initMysqlConn()  # 连接数据库
        # 设定获取日线行情的初始日期和终止日期，其中终止日期设定为昨天。
        # start_dt = '19901219'
        time_temp = datetime.datetime.now()
        end_dt = time_temp.strftime('%Y%m%d')
        end_dt1 = (datetime.datetime.strptime(
            end_dt, "%Y%m%d")).strftime('%Y-%m-%d')
        start_dt=(time_temp - datetime.timedelta(days=days)).strftime('%Y%m%d')
        start_dt = (datetime.datetime.strptime(
            start_dt, "%Y%m%d")).strftime('%Y-%m-%d')
# 获取开始结束之间所有有交易的日期
        # df1 = self.pro.trade_cal(exchange='SSE', is_open='1',
        #                     start_date=start_dt,
        #                     end_date=end_dt,
        #                     fields='cal_date')

# 登陆系统
        lg = bs.login()
        # 显示登陆返回信息
        print('login respond error_code:'+lg.error_code)
        print('login respond  error_msg:'+lg.error_msg)

        # 设定需要获取数据的股票池
        stock_pool = ['sh.000001', 'sz.399001', 'sz.399006']
        ss=['000001_sh', '399001_sz', '399006_cyb']
        name_pool = ['上证指数', '深证成指', '创业板']
        # startDate = ['1990-12-19', '1990-12-01', '2009-10-30']
        startDate = [start_dt, start_dt,start_dt]#追加一天的数据
        total = len(stock_pool)
        for i in range(len(stock_pool)):
            # for date in df1['cal_date'].values:
                try:
                    # 详细指标参数，参见“历史行情指标参数”章节
                    rs = bs.query_history_k_data_plus(stock_pool[i],
                        "date,code,open,high,low,close,preclose,volume,amount,pctChg",
                        start_date=startDate[i], end_date=end_dt1, frequency="d")
                    print('query_history_k_data_plus respond error_code:'+rs.error_code)
                    print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

                    # 打印结果集
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        # 获取一条记录，将记录合并在一起
                        data_list.append(rs.get_row_data())
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    filename='G:\\stockData\\originData\\'+ss[i]+'.csv'
                    ex=os.path.isfile(filename)  #当前文件是否存在，存在即添加，不存在新建
                    if ex==False:
                        df.to_csv(filename,encoding='utf_8_sig')
                    else :
                        df.to_csv(filename,mode='a',header=False,encoding='utf_8_sig')
                        df1=pd.read_csv(filename,encoding='utf_8_sig')
                        df1=df1.dropna()#删除所有包含空值的行
                        # df=df.drop(df.tail(4).index)
                        df1=df1.drop_duplicates(['date'])
                        df1 = df1.sort_values('date')#降序
                        df1.to_csv(filename,index=None,encoding='utf_8_sig')
                    continue
                    # 查询当天所有正常上市交易的股票数据
                    # df = ts.get_h_data(stock_pool[i],start=start_dt1,end=end_dt1,index=True)
                    # print(df.index[i])
                 #   df = ts.get_h_data('399006', index=True)
                    c_len = df.shape[0]
                except Exception as aa:
                    print(aa)
                    print('get error')
                for j in range(c_len):  # 按行读取股票列表
                    resu0 = list(df.iloc[c_len-1-j])
                    resu = []
                    for k in range(len(resu0)):  # 读取股票的字段
                        if str(resu0[k]) == 'nan':
                            resu.append(-1)
                        else:
                            resu.append(resu0[k])
                    # state_dt = (datetime.datetime.strptime(str(df.index[i]), "%Y%m%d")).strftime('%Y-%m-%d')
                    # state_dt = str(df.index[c_len-1-j])
                    state_dt = str(resu[0])
                    try:
                        pass
                        # sql_insert = "INSERT INTO index_data(date,code,name,open,high,low,close,preclose,volume,amount,p_change,price_change) VALUES ('%s','%s','%s','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f')" % (state_dt,str(stock_pool[i]),str(name_pool[i]),float(resu[2]),float(resu[3]),float(resu[4]),float(resu[5]),float(resu[6]),float(resu[7]),float(resu[8],float(resu[9]))
                        sql_insert = "INSERT INTO index_data_bs(date,code,name,open,high,low,close,preclose,volume,amount,p_change) VALUES ('%s','%s', '%s','%.2f', '%.2f','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f')" % (state_dt,str(stock_pool[i]),str(name_pool[i]),float(resu[2]),float(resu[3]),float(resu[4]),float(resu[5]),float(resu[6]),float(resu[7]),float(resu[8]),float(resu[9]))               
                        # sql_insert = "INSERT INTO index_data_bs(date,code,name,open,high,low,close,preclose,volume,amount,p_change) VALUES ('%s','%s','%s','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f','%.2f')" % (state_dt, str(stock_pool[i]), str(name_pool[i]), float(resu[2]), float(resu[3]), float(resu[4]), float(resu[5]), float(resu[6]), float(resu[7]), float(resu[8], float(resu[9]))
                        self.cursor.execute(sql_insert)
                        self.db.commit()
                        # pass
                    except Exception as err:
                        print('insert err', err)
                        continue
        self.cursor.close()
        self.db.close()
        # 登出系统
        bs.logout()
        print('getAllIndexHistoryData Finished!')

#获取近3年的前复权数据
    def getInfoCSV(self,ts_code):
        days=0
        endDate=(datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y%m%d')
        endDate = (datetime.datetime.strptime(endDate, "%Y%m%d")).strftime('%Y-%m-%d')
        # startDate=(datetime.datetime.now() - datetime.timedelta(days=(days+1))).strftime('%Y%m%d')
        # startDate = (datetime.datetime.strptime(startDate, "%Y%m%d")).strftime('%Y-%m-%d')
        # startDate='2020-08-01'
        df = ts.get_hist_data(ts_code,start=endDate,end=endDate)#默认前复权，只能获取近3年数据
        
        filename='G:\\stockData\\'+ts_code+'.csv'
        ex=os.path.isfile(filename)  #当前文件是否存在，存在即添加，不存在新建
        if ex==False:
            df.to_csv(filename,encoding='utf_8_sig')
        else :
            df.to_csv(filename,mode='a', header=False,encoding='utf_8_sig')

if __name__ == '__main__':
    t=getStockInfo()
    t.getAllStockList()#更新股票列表
    t.getA50StockList()#更新上证50、沪深300、中证500指数列表
 
    # t.getAllIndexHistoryData(days=8)
    # t.getAllStockHistoryData(days=1)   
    # code='002216'
    # t.getInfoCSV(code)
    pass
