# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 20:32:32 2020

@author: lu
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal   #滤波等
import matplotlib.dates as mdates    #處理日期
import datetime
from scipy.interpolate import make_interp_spline


#讀入日期
df = pd.read_csv('G:\\stockData\\002594.SZ.csv')
c_len = df.shape[0]#求行数
date=[]
low=[]
for j in range(c_len):
    # xx = list(df.loc[c_len-1-j])
    xt=str(df['trade_date'][c_len-1-j])
    xt=(datetime.datetime.strptime(xt, "%Y%m%d")).strftime('%Y-%m-%d')
    date.append(xt)
    low.append(float(df['low'][c_len-1-j]))

df1=df['low']
df1=df1.iloc[::-1].reset_index(drop=True) 
x = np.arange(0, c_len)
x_new = np.linspace(x.min(),x.max(),622) #300 represents number of points to make between T.min and T.max
y_smooth = make_interp_spline(x, low)(x_new)
#散点图
plt.scatter(x, low, c='black',alpha = 0.5)  #alpha:透明度) c:颜色
#折线图
plt.plot(x, low, linewidth=1)  #线宽linewidth=1
#平滑后的折线图
# plt.plot(x_new,y_smooth,c='red')
 
# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']  #SimHei黑体
plt.rcParams['axes.unicode_minus'] = False
 
plt.title("绘图", fontsize=24)#标题及字号
plt.xlabel("X", fontsize=24)#X轴标题及字号
plt.ylabel("Y", fontsize=24)#Y轴标题及字号
plt.tick_params(axis='both', labelsize=6)#刻度大小
num_peak_3 = signal.find_peaks(low, distance=30) #distance表极大值点的距离至少大于等于30个水平单位,存的是索引
# plt.plot(x_new, y_smooth, 'b',label='polyfit values')
peakDict={}
minDict={}
maxIndex=[]
maxValues=[]
for ii in range(len(num_peak_3[0])):
    plt.plot(num_peak_3[0][ii], y_smooth[num_peak_3[0][ii]],'*',markersize=14)
    peakDict[num_peak_3[0][ii]]=low[num_peak_3[0][ii]]#字典key-values保存峰值索引和值
    if ii == len(num_peak_3[0])-1:
        break
    df2=df1.iloc[num_peak_3[0][ii]:num_peak_3[0][ii+1]]
    minT=min(df2)#求最小值
    indexT=df2.idxmin()# 最小值的索引
    minDict[indexT]=minT
    # if indexT-num_peak_3[0][ii]>=10 & num_peak_3[0][ii+1]-indexT>=10 :
        # listIndex.append
    plt.plot(indexT, minT,'*',markersize=14)
# plt.savefig('C:\\Users\\lu\\Desktop\\f1.png')
plt.show()
temp1=list(peakDict.keys())
temp2=list(minDict.keys())
df3=pd.DataFrame(columns=['x_values','y_values','pointType','daysdiff','amplitude','dayAvg','dayVar','ampAvg','ampVar'])
# df3.head(5)

j=0
for i in range(len(temp1)):#
    df3.loc[j,'x_values']=temp1[i]#做标志，数据清洗
    df3.loc[j,'pointType']='peak'
    df3.loc[j,'y_values']=peakDict[temp1[i]]
    j=j+1
    if i==len(temp1)-1:
        break   
    df3.loc[j,'x_values']=temp2[i]
    df3.loc[j,'y_values']=minDict[temp2[i]]
    df3.loc[j,'pointType']='min'
    j=j+1

df3['daysdiff']=df3['x_values']-df3['x_values'].shift(1)#算相邻两行数值差值
df3['amplitude']=(df3['y_values']-df3['y_values'].shift(1))/df3['y_values'].shift(1)*100#


# df3=pd.read_csv('G:/stockData/test1.csv')
df3.loc[0,'dayAvg']=df3[df3['daysdiff']>=10]['daysdiff'].mean()
df3.loc[0,'dayVar']=df3[df3['daysdiff']>=10]['daysdiff'].std()
df3.loc[0,'ampAvg']=df3[df3['daysdiff']>=10]['amplitude'].abs().mean()
df3.loc[0,'ampVar']=df3[df3['daysdiff']>=10]['amplitude'].abs().std()
# df3.to_csv('G:/stockData/test1.csv')
# for i in range(df3.shape[0]-1):
#     j=i+1
#     # if j==df3.shape[0]:
#     #     break
#     df3.loc[i,'daysdiff']=df3.loc[j,'x_values']-df3.loc[i,'x_values']  
#     df3.loc[i,'amplitude']=round((df3.loc[j,'y_values']-df3.loc[i,'y_values'])/df3.loc[i,'y_values'],3)*100
# df3.head()

# daysDiff=[]
# amplitude=[]
# for i in range(temp1):
#     daysDiff.append(temp1[i]-temp2[i])
#     amplitude.append(peakDict[temp1[i]]-minDict[temp2[i]])
#     if i==len(temp1)-1:
#         break
#     daysDiff.append(temp1[i+1]-temp2[i])
#     amplitude.append(peakDict[temp1[i+1]]-minDict[temp2[i]])


xx = np.arange(0, 622)
# yy = np.sin(xxx*np.pi/180)
# tt=np.pi
yy=low
z1 = np.polyfit(xx, yy, 7) # 用7次多项式拟合
p1 = np.poly1d(z1) #多项式系数
print(p1) # 在屏幕上打印拟合多项式
yvals=p1(xx) 

plt.plot(xx, low, '*',label='original values')
plt.plot(xx, yvals, 'r',label='polyfit values')
plt.xlabel('x axis')
plt.ylabel('y axis')
plt.legend(loc=4)
plt.title('polyfitting')
plt.show()

# 极值
num_peak_3 = signal.find_peaks(yvals, distance=10) #distance表极大值点的距离至少大于等于10个水平单位
print(num_peak_3[0])
print('the number of peaks is ' + str(len(num_peak_3[0])))
plt.plot(date, low, '*',label='original values')
plt.plot(date, yvals, 'r',label='polyfit values')
plt.xlabel('x axis')
plt.ylabel('y axis')
plt.legend(loc=4)
plt.title('polyfitting')
for ii in range(len(num_peak_3[0])):
    plt.plot(num_peak_3[0][ii], yvals[num_peak_3[0][ii]],'*',markersize=10)
plt.show()




class testCurve:
    def __init__(self):
        pass
    # def smooth(self):
    #     x_new = np.linspace(x.min(),x.max(),300) #300 represents number of points to make between T.min and T.max
    #     y_smooth = spline(x,y,x_new)
    #     #散点图
    #     plt.scatter(x, y, c='black',alpha = 0.5)  #alpha:透明度) c:颜色
    #     #折线图
    #     plt.plot(x, y, linewidth=1)  #线宽linewidth=1
    #     #平滑后的折线图
    #     plt.plot(x_new,y_smooth,c='red')
        
    #     # 解决中文显示问题
    #     plt.rcParams['font.sans-serif'] = ['SimHei']  #SimHei黑体
    #     plt.rcParams['axes.unicode_minus'] = False
        
    #     plt.title("绘图", fontsize=24)#标题及字号
    #     plt.xlabel("X", fontsize=24)#X轴标题及字号
    #     plt.ylabel("Y", fontsize=24)#Y轴标题及字号
    #     plt.tick_params(axis='both', labelsize=14)#刻度大小
    #     #plt.axis([0, 1100, 1, 1100000])#设置坐标轴的取值范围
    #     plt.show()