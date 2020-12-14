import numpy as np
import pandas as pd
import talib
import os
import datetime
import scipy.stats as stats

print('hello python git test')
def test():
    data={'a':[35,44,111,72],'b':['ST天山',3,5,0],'c':[400,66,8,0]}
    df=pd.DataFrame(data)
    print(df)
    am=np.mean(df['a'])
    at=np.std(df['a'])
    z= (df.loc[3,'a'] - am) / at#Z变换
    ap=stats.norm.cdf(z)

    def func1(pam):
        pass
        t=pam['b']
        # print(pam['b'])
        l=len(str(t))
        if l > 1:
            print('2')
        # a1=df[df['b']==pam['a']]['c']
        # a1=df.loc[(df['b']=='3'),'c']
    df.apply(func1,axis=1)
test()


import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import Ui_untitled

def buttonClicked(girl):
    girl.textBrowser.append("hello world")

# app = QtWidgets.QApplication(sys.argv)
# MainWindow = QtWidgets.QMainWindow()
# ui = Ui_untitled.Ui_MainWindow()
# ui.setupUi(MainWindow)
# ui.pushButton.clicked.connect(lambda:buttonClicked(ui))
# MainWindow.show()
# sys.exit(app.exec_())
