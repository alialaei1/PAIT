
from heapq import nsmallest
import json
from re import L
from time import sleep
from threading import Thread
from os.path import join, exists
from traceback import print_exc
from random import random
from datetime import datetime, timedelta

from api.dwx_client import dwx_client


from dash import Dash, Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
#import talib as ta
import json


run_program = datetime.utcnow()



output = pd.DataFrame()
output_in = pd.DataFrame()
last_open_time__ = datetime.utcnow()

stop_key_candel = ""
Get_Candle = 1
h_candel = 48

volum_list = []
open_list = []
high_list = []
low_list = []
close_list = []
time_list = []

orderhistory = [1]

point1 = 0.003

process = datetime.utcnow()

magicnumber = 0

######################################


zarib = [0.01,0.02,0.04,0.08,0.16,0.32,0.64,1.28] 

count = 0
######################################
nc = 0
nm = 0

ghozashte = 0 

numberorder = 0 
positionprice = 0

ok = 0
notok = 0

start_ = 0
buy = 0
sell = 0


x = {
  "count": 0,
  "ghozashte": 0,
  "positionprice": 0
  }



def proline(t_,o_,c_,p_):
    global zarib
    global ghozashte
    global count
    global numberorder
    global positionprice
    global orderhistory
    global ok
    global notok
    global start_
    global buy
    global sell
    
    data = []

    if numberorder != len(orderhistory) :
        numberorder = len(orderhistory)
        print("processsssssssssssssssssssssssssssssss")
        if ghozashte == 0 :
            if (count <= 2 or (count == 3 and orderhistory[-1] == 1)) :
                if orderhistory[-1] == 1 :
                    count = 0
                positionprice = zarib[count] * 3                  
                count = count + 1
                if count == 3 :
                    notok = zarib[count]
                    ok = zarib[0] * 3
                else:
                    notok = zarib[count] * 3
                    ok = zarib[0] * 3

            else:
                ghozashte = ghozashte + 3

        if ghozashte != 0 :

            if count < 8 :

                if orderhistory[-1] == 1 :
                    count = 3
                    ghozashte = ghozashte - 1

                if ghozashte == 0 :
                    count = 0
                    positionprice = zarib[count] * 3
                    count = count + 1
                    notok = zarib[count] * 3
                    ok = zarib[0] * 3
                else:
                    positionprice = zarib[count]
                    count = count + 1
                    notok = zarib[count]
                    ok = zarib[3]
            else :
                positionprice = -1
                ok = -1
                notok = -1
                       

    if t_ != 0 :
        for j in o_:
            if o_[j]['open_price'] == c_:
                if o_[j]['type'] == 'buy' :
                    buy = ok
                    sell = notok
                if o_[j]['type'] == 'sell' :
                    buy = notok
                    sell = ok
    else:
        pass

    if buy == 0 :
        buy = zarib[0] * 3
        count = 0 
    if sell == 0 :
        sell = zarib[0] * 3
        count = 0 

    data.append(["u","buystop", round(c_+p_, 5),buy])
    if t_ != 0 :
        for j in o_:
            if o_[j]['open_price'] == c_ and len(data) == 1 :
                data.append(["m",o_[j]['type'], round(c_, 5),positionprice])
    data.append(["d","sellstop", round(c_ - p_, 5),sell])

    return data 




def baseline(close_,p_):
    data = [0]
    for i in range(0,len(close_)):
        if ((close_[i] > data[-1]  + p_) or (close_[i] < data[-1]  - p_)) :
            data.append(close_[i])
        else:
            data.append(data[-1])
    
    data.pop(0)

    return pd.Series(data) 

def baseline2(close_,p_):
    data = []
    data.append((close_[0]//p_)*p_)
    for i in range(1,len(close_)):
        if (close_[i] > data[-1]  + p_) :
            data.append((close_[i]//p_)*p_)
        elif (close_[i] < data[-1]  - p_):
            data.append(((close_[i] + p_)//p_)*p_)
        else:
            data.append(data[-1])
    
    return pd.Series(data) 


def baseline3(open_,high_,low_,close_,p_):
    data = []
    data.append(round((close_[0]//p_)*p_,5))
    for i in range(1,len(close_)):
        if (high_[i] > data[-1]  + p_) :
            data.append(round((high_[i]//p_)*p_,5))
        elif (low_[i] < data[-1]  - p_):
            data.append(round(((low_[i] + p_)//p_)*p_,5))
        else:
            data.append(round(data[-1],5))

    return pd.Series(data) 


def parakandegi(close_):
    data = []
    data.append(0)
    for i in range(1,len(close_)):
        if (close_[i-1] == close_[i] ) :
            data.append(0)
        elif (close_[i-1] < close_[i] ) :
            data.append(1)
        elif (close_[i-1] > close_[i] ) :
            data.append(-1)
    return pd.Series(data) 


def parakandegi_(close_):
    data = []
    last = 0
    for i in range(0,len(close_)):

        if close_[i] == 0 :
            try:
                data.append(data[-1])
            except:
                data.append(0)
        elif close_[i] == 1 :
            if last == -1 :
                data.append(data[-1]+1)
            elif last == 1 :
                data.append(0)
            else :
                data.append(0)
            last = 1
        elif close_[i] == -1 :
            if last == 1 :
                data.append(data[-1]+1)
            elif last == -1 :
                data.append(0)
            else :
                data.append(0)
            last = -1
    return pd.Series(data)


app = Dash()
app.layout = html.Div([
    dcc.Graph(id='candles'),
    #dcc.Graph(id='candlesH'),
    dcc.Interval(id="interval",interval = 20000),
])

@app.callback(
    Output("candles","figure"),
    #Output("candlesH","figure"),
    Input("interval","n_intervals"),
)

def update_figure(n_intervals):
    
    global output

    global output_in
    global last_open_time__
    now = datetime.utcnow()

    try :
        if len(output['Date'])>=1 and (last_open_time__ > ( now - timedelta(seconds=58))):
            output_in = output
    except:
        pass
#######################################################################
    candles = make_subplots(rows=3, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, subplot_titles=('Candlestick', 'Volume'), 
               row_width=[0.2,0.2,0.6])
    
    candles.add_trace(go.Candlestick(x=output_in['Date'],
            open=output_in['Open'],
            high=output_in['High'],
            low=output_in['Low'],
            close=output_in['Close'], name="Candlestick"),row=1, col=1) 


    candles.add_trace(go.Candlestick(x=output_in['Date'],
            open=output_in['BaseClose'],
            high=output_in['BaseClose'],
            low=output_in['BaseClose'],
            close=output_in['BaseClose'], name="Base"),row=1, col=1) 


    candles.add_trace(go.Bar(x=output_in['Date'], y=output_in["Volume"]), row=2, col=1)
    candles.add_trace(go.Bar(x=output_in['Date'], y=output_in["Parakandegi"]), row=3, col=1)
    candles.update_layout(xaxis_rangeslider_visible = False,height = 600)

##########################################################################
    # candlesH = make_subplots(rows=1, cols=1, shared_xaxes=True, 
    #            vertical_spacing=0.03, subplot_titles=('Base'), 
    #            row_width=[0.6])
    
    # candlesH.add_trace(go.Candlestick(x=output_in['Date'],
    #         open=output_in['BaseClose'],
    #         high=output_in['BaseClose'],
    #         low=output_in['BaseClose'],
    #         close=output_in['BaseClose'], name="Base"),row=1, col=1) 
    
    
    # LAST = talib.MIN(output_in['LowH'],len(output_in['LowH']))
    
    # for i in range(0,len(output_in['Date'])):
    #     if (output_in["bay"].iloc[i] == 1):
    #         candlesH.add_trace(go.Scatter(x=[output_in['Date'].iloc[i]], y=[LAST.iloc[-1]],line_color='#00ff00'), row=1, col=1)
    #     elif (output_in["sell"].iloc[i] == 1):
    #         candlesH.add_trace(go.Scatter(x=[output_in['Date'].iloc[i]], y=[LAST.iloc[-1]],line_color='#ff0000'), row=1, col=1)
    #     elif (output_in["stop"].iloc[i] == 1):
    #         candlesH.add_trace(go.Scatter(x=[output_in['Date'].iloc[i]], y=[LAST.iloc[-1]],line_color='#ffff00'), row=1, col=1)
    #     else:
    #         candlesH.add_trace(go.Scatter(x=[output_in['Date'].iloc[i]], y=[LAST.iloc[-1]],line_color='#0000ff'), row=1, col=1)
    # #candlesH.add_trace(go.Scatter(x=output_in['Date'],y= [2,2,2,2,2,2],fill='tozeroy'),row=1, col=1)
    
    # candlesH.add_trace(go.Bar(x=output_in['Date'], y=output_in["VolumeH"]), row=2, col=1)



    # candlesH.add_trace(go.Bar(x=output_in['Date'], y=output_in["VolumeH"], showlegend=False, marker_color=output_in["Volum_color"]), row=3, col=1)
    # candlesH.add_trace(go.Scatter(x=output_in['Date'], y=output_in["ATR"],name="ATR"), row=4, col=1)
    # # candlesH.add_trace(go.Scatter(x=output_in['Date'], y=output_in["StochRSI_K"],name="StochRSI_K"), row=5, col=1)
    # # candlesH.add_trace(go.Scatter(x=output_in['Date'], y=output_in["StochRSI_D"],name="StochRSI_D"), row=5, col=1)
    # # candlesH.add_trace(go.Scatter(x=output_in['Date'], y=output_in["zero_cras"],name="RSI"), row=6, col=1)
    
    # candlesH.update_layout(xaxis_rangeslider_visible = False,height = 600)
    
##########################################################################
    
    return candles#,candlesH


class tick_processor():

    def __init__(self, MT4_directory_path, 
                 sleep_delay=0.005,             # 5 ms for time.sleep()
                 max_retry_command_seconds=10,  # retry to send the commend for 10 seconds if not successful. 
                 verbose=True
                 ):

        # if true, it will randomly try to open and close orders every few seconds. 
        self.open_test_trades = True

        self.last_open_time = datetime.utcnow()
        self.last_modification_time = datetime.utcnow()

        self.dwx = dwx_client(self, MT4_directory_path, sleep_delay, 
                              max_retry_command_seconds, verbose=verbose)
        sleep(1)

        self.dwx.start()
        
        # account information is stored in self.dwx.account_info.
        print("Account info:", self.dwx.account_info)

        # subscribe to tick data:
        self.dwx.subscribe_symbols(['EURUSD_o'])

        # subscribe to bar data:
        self.dwx.subscribe_symbols_bar_data([['EURUSD_o', 'M1']])

        # request historic data:
        # end = datetime.utcnow()
        # start = end - timedelta(days=30)  # last 30 days
        # self.dwx.get_historic_data('EURUSD_o', 'M1', start.timestamp(), end.timestamp())


    def on_tick(self, symbol, bid, ask):

        global Get_Candle
        global output
        global point1
        global magicnumber
        global process
        global nc
        global nm


        now = datetime.utcnow()

        print('on_tick:', now, symbol, bid, ask)

        if Get_Candle == 2 :
            if self.open_test_trades:

                if now > self.last_open_time + timedelta(seconds=1):
                    self.last_open_time = now
                    if now < process + timedelta(seconds=55) and now > process + timedelta(seconds=1) and nc != nm:

                        nm = nc


                        i = len(self.dwx.open_orders)
                        data__ = []
                        for j in self.dwx.open_orders:
                            data__.append([j,self.dwx.open_orders[j]['magic'],self.dwx.open_orders[j]['type'],self.dwx.open_orders[j]['open_price'],self.dwx.open_orders[j]['lots'],self.dwx.open_orders[j]['commission']])
                        #print(data__)

                        data_ = proline(i,self.dwx.open_orders,output['BaseClose'].iloc[-1] ,point1)
                        

                        print(data_)



                        for k in range(0,len(data__)) : #hazf
                            u = 0
                            for p in range(0,len(data_)) :
                                if data__[k][3] == data_[p][2] and data__[k][4] == data_[p][3]:
                                    u = u + 1
                            if u == 0 :
                                self.dwx.close_orders_by_magic(data__[k][1])


                        for k in range(0,len(data_)) : #add
                            u = 0
                            for p in range(0,len(data__)) :
                                if data_[k][2] == data__[p][3] :
                                    u = u + 1
                            if u == 0 :
                                upper =  data_[k][2] + point1
                                base =   data_[k][2]
                                lower =  data_[k][2] - point1



                                if (data_[k][1] == "buystop") :
                                    magicnumber = magicnumber + 1
                                    self.dwx.open_order(symbol=symbol, magic= magicnumber,order_type='buystop',price=base, lots=data_[k][3],stop_loss=lower,take_profit=upper)
                                if (data_[k][1] == "sellstop") :
                                    magicnumber = magicnumber + 1
                                    self.dwx.open_order(symbol=symbol, magic= magicnumber,order_type='sellstop',price=base, lots=data_[k][3],stop_loss=upper,take_profit=lower)



                        for k in range(0,len(data__)) : #tekrari
                            for p in range(0,len(data__)) :
                                if data__[p][2] == data__[k][2] and data__[p][3] == data__[k][3] and data__[p][4] == data__[k][4] and data__[p][5] == data__[k][5] and p != k :
                                    self.dwx.close_orders_by_magic(data__[p][1])
                   



        # global orderhistory
        # global output
        # global Get_Candle
        # global point1
        # global process


        # global moj1
        # global moj2
        # global moj3
        # global mem1
        # global mem2
        # global mem3
        # global size1
        # global size2
        # global size3
        # global count1
        # global count2
        # global count3
        # global zarib

        # global count
        # global lenn__

        # i = len(self.dwx.open_orders)
        # now = datetime.utcnow()

        # print('on_tick:', now, symbol, bid, ask)

        # Bay_Pice = (bid + ask)/2
        # defrent = abs(bid - ask)

        # size = 0.01
        # j = 0
        # upper = 0
        # lower = 0

        # try:
        #     lenn__ = orderhistory[-1]
        #     lenn__ = len(orderhistory)
        # except:
        #     lenn__ = lenn__

        # if i == 0 and Get_Candle == 2 and lenn__ != count:

        #     if self.open_test_trades:
        #         if now > self.last_open_time + timedelta(seconds=1):
        #             self.last_open_time = now
        #             if now < process + timedelta(seconds=55) and now > process + timedelta(seconds=5):

        #                 upper = output['Close'].iloc[-1]  + point1
        #                 lower = output['Close'].iloc[-1]  - point1


        #                 print(output['BaseClose'].iloc[-1])
        #                 print(output['BaseClose'].iloc[-2])
        #                 if output['BaseClose'].iloc[-1] != output['BaseClose'].iloc[-2]:
        #                     print("hesab1")
        #                     count = len(orderhistory)


        #                     if  (size2 < 0.04 and size1 < 0.04 and size3 < 0.04):
        #                         moj1 = 1
        #                         moj2 = 1
        #                         moj3 = 1
        #                         print("hesab2")
        #                     if ((size2 >= 0.04 or size1 >= 0.04 or size3 >= 0.04) and orderhistory[-1] == 0 ) :
        #                         print("hesab3")

        #                         if size1 > size2 and size1 > size3 :
        #                             moj1 = 1
        #                             moj2 = 0
        #                             moj3 = 0

        #                         elif size2 > size1 and size2 > size3 :
        #                             moj1 = 0
        #                             moj2 = 1
        #                             moj3 = 0

        #                         elif size3 > size1 and size3 > size2 :
        #                             moj1 = 0
        #                             moj2 = 0
        #                             moj3 = 1

        #                         ##############################################################
        #                         elif size1 == size2 and size1 > size3 :
        #                             moj1 = 1
        #                             moj2 = 0
        #                             moj3 = 0

        #                         elif size1 == size3 and size1 > size2 :
        #                             moj1 = 0
        #                             moj2 = 0
        #                             moj3 = 1

        #                         elif size2 == size3 and size2 > size1 :
        #                             moj1 = 0
        #                             moj2 = 1
        #                             moj3 = 0
        #                         else:
        #                             pass
        #                         ##############################################################


        #                     if size2 >= 0.04 and size1 >= 0.04 and size3 >= 0.04 and orderhistory[-1] == 0 :
        #                         print("hesab4")

        #                         if size2 == size1 and size3 == size1 and size2 == size3:
        #                             moj2 = 0
        #                             moj3 = 0
        #                             moj1 = 1
        #                         if size2 > size1 and size2 > size3 :
        #                             moj2 = 1
        #                             moj1 = 0
        #                             moj3 = 0
        #                         if size2 < size1 and size1 > size3 :
        #                             moj2 = 0
        #                             moj1 = 1
        #                             moj3 = 0
        #                         if size3 > size1 and size2 < size3 :
        #                             moj2 = 0
        #                             moj1 = 0
        #                             moj3 = 1




        #                     if moj1 :
        #                         print("hesab5")

        #                         if len(orderhistory) > count1 :
        #                             if orderhistory[count1] == 0 :
        #                                 if count1 != len(orderhistory):
        #                                     count1 = len(orderhistory)
        #                                 if mem1 <= 6 :
        #                                     mem1 = mem1 + 1
        #                                     size1  = zarib[mem1]
        #                             else:
        #                                 if count1 != len(orderhistory):
        #                                     count1 = len(orderhistory) 
        #                                 mem1 = 0
        #                                 size1  = zarib[mem1]
        #                         else:
        #                             pass
        #                     else:
        #                         pass




        #                     if moj2 :
        #                         print("hesab6")
        #                         if len(orderhistory) > count2 :
        #                             if orderhistory[count2] == 0 :
        #                                 if count2 != len(orderhistory) :
        #                                     count2 = len(orderhistory)
                                            
        #                                 if mem2 <= 6 :
        #                                     mem2 = mem2 + 1
        #                                     size2  = zarib[mem2]
        #                             else:
        #                                 if count2 != len(orderhistory):
        #                                     count2 = len(orderhistory)
        #                                 mem2 = 0
        #                                 size2  = zarib[mem2]
        #                         else:
        #                             pass
        #                     else:
        #                         pass




        #                     if moj3 :
        #                         print("hesab7")
        #                         if len(orderhistory) > count3 :
        #                             if orderhistory[count3] == 0 :
        #                                 if count3 != len(orderhistory) :
        #                                     count3 = len(orderhistory) 
                                            
        #                                 if mem3 <= 6 :
        #                                     mem3 = mem3 + 1
        #                                     size3  = zarib[mem3]
        #                             else:
        #                                 if count3 != len(orderhistory) :
        #                                     count3 = len(orderhistory)
        #                                 mem3 = 0
        #                                 size3  = zarib[mem3]
        #                     else:
        #                         pass



        #                 if output['BaseClose'].iloc[-1] > output['BaseClose'].iloc[-2] :#and output['ADX'] < 30:
        #                     print("buy1")
        #                     size = (size1*moj1)+(size2*moj2)+(size3*moj3)
        #                     if( size <= 1.28):
        #                         print("buy2",size)
        #                         self.dwx.open_order(symbol=symbol, order_type='buy',price=ask, lots=size,stop_loss=lower,take_profit=upper)
        #                     else:
        #                         print("buy3")
        #                         self.open_test_trades = False
        #                 if output['BaseClose'].iloc[-1] < output['BaseClose'].iloc[-2] :#and output['ADX'] < 30:
        #                     print("sell1")
        #                     size = (size1*moj1)+(size2*moj2)+(size3*moj3)
        #                     if( size <= 1.28):
        #                         print("sell2",size)
        #                         self.dwx.open_order(symbol=symbol, order_type='sell',price=bid, lots=size,stop_loss=upper,take_profit=lower)
        #                     else:
        #                         print("sell3")
        #                         self.open_test_trades = False

    def on_bar_data(self, symbol, time_frame, time, open_price, high, low, close_price, tick_volume):
        global output
        global h_candel

        global stop_key_candel
        global Get_Candle

        global volum_list
        global open_list
        global high_list
        global low_list
        global close_list
        global time_list

        global last_open_time__
        global point1
        global process

        global nc

        process = datetime.utcnow()

        last_open_time__ = datetime.utcnow()
        
        if Get_Candle == 1 :
            Get_Candle = 0
            stop_key_candel = time
            end = datetime.utcnow() + timedelta(hours=8,minutes=30)
            start = end - timedelta(hours=h_candel)
            self.dwx.get_historic_data('EURUSD_o', 'M1', start.timestamp(), end.timestamp())
        
        if Get_Candle == 2 :
            
            
            
            if (len(volum_list)>= (60)):
                volum_list.pop(0)
                open_list.pop(0)
                high_list.pop(0)
                low_list.pop(0)
                close_list.pop(0)
                time_list.pop(0)
                
                
            volum_list.append(tick_volume)
            open_list.append(open_price)
            high_list.append(high)
            low_list.append(low)
            close_list.append(close_price)
            time_list.append(str(time))
            
            last_open_time_ = datetime.utcnow()


            output = pd.DataFrame()
            
            
            output["Open"] = pd.Series(open_list)
            output["High"] = pd.Series(high_list)
            output["Low"] = pd.Series(low_list)
            output["Close"] = pd.Series(close_list)
            output["Volume"] = pd.Series(volum_list)
            output["Date"] = pd.Series(time_list)

            #output["ADX"] = ta.ADX(output["High"],output["Low"],output["Close"],32)

            output["BaseClose"] = baseline3(output["Open"],output["High"],output["Low"],output["Close"],point1)
            #output["BaseClose"] = baseline2(output["Close"],point1)
            output["Parakandegi"] = parakandegi_(parakandegi(output["BaseClose"]))
            
            nc = nc + 1
        print('on_bar_data:', symbol, time_frame, datetime.utcnow(), time, open_price, high, low, close_price)

    
    def on_historic_data(self, symbol, time_frame, data):

        global output
        global Get_Candle
        global stop_key_candel


        global volum_list
        global open_list
        global high_list
        global low_list
        global close_list
        global time_list

        global point1

        global process


        process = datetime.utcnow()

        open_ = []
        high_ = []
        low_ = []
        close_ = []
        volume_ = []
        time_ = []
        time__ = []
        
        time_=list(data.keys())


        for i in time_:
            open_.append(data[i]['open'])
            high_.append(data[i]['high'])
            low_.append(data[i]['low'])
            close_.append(data[i]['close'])
            volume_.append(data[i]['tick_volume'])
            time__.append(i)
            if i == str(stop_key_candel) :
                break
                
        volum_list=volume_
        open_list=open_
        high_list=high_
        low_list=low_
        close_list=close_
        time_list=time__

        output = pd.DataFrame()
        
        output["Open"] = pd.Series(open_)
        output["High"] = pd.Series(high_)
        output["Low"] = pd.Series(low_)
        output["Close"] = pd.Series(close_)
        output["Volume"] = pd.Series(volume_)
        output["Date"] = pd.Series(time__)

        #output["ADX"] =ta.ADX(output["High"],output["Low"],output["Close"],32)

        output["BaseClose"] = baseline3(output["Open"],output["High"],output["Low"],output["Close"],point1)
        #output["BaseClose"] = baseline2(output["Close"],point1)
        output["Parakandegi"] = parakandegi_(parakandegi(output["BaseClose"]))

        # you can also access the historic data via self.dwx.historic_data. 
        print('historic_data:', symbol, time_frame, f'{len(data)} bars')
        Get_Candle = 2

    def on_historic_trades(self):
        global orderhistory

        internal_list = []
        for i in self.dwx.historic_trades:
            if self.dwx.historic_trades[i]["pnl"] > 0 :
                internal_list.append(1)
            if self.dwx.historic_trades[i]["pnl"] < 0 :
                internal_list.append(0)


        orderhistory = []
        for i in range (len(internal_list)-1,-1,-1):
            orderhistory.append(internal_list[i])
        print(orderhistory)
        print(f'historic_trades: {len(self.dwx.historic_trades)}')
    

    def on_message(self, message):

        if message['type'] == 'ERROR':
            print(message['type'], '|', message['error_type'], '|', message['description'])
        elif message['type'] == 'INFO':
            print(message['type'], '|', message['message'])


    # triggers when an order is added or removed, not when only modified. 
    def on_order_event(self):
        global run_program
        date = (datetime.utcnow() - run_program) // timedelta(days=1)
        print(date)
        self.dwx.get_historic_trades(lookback_days=date+1)
        print(f'on_order_event. open_orders: {len(self.dwx.open_orders)} open orders')


MT4_files_dir = 'C:/Users/Administrator/AppData/Roaming/MetaQuotes/Terminal/2E7392F5A2A24C0774CFE5C2687A8155/MQL4/Files/'

processor = tick_processor(MT4_files_dir)

while processor.dwx.ACTIVE:
    app.run_server(debug=True,use_reloader=False)
    sleep(1)


