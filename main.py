# You should not modify this part.
from numpy import NaN


def config():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--consumption", default="./sample_data/consumption.csv", help="input the consumption data path")
    parser.add_argument("--generation", default="./sample_data/generation.csv", help="input the generation data path")
    parser.add_argument("--bidresult", default="./sample_data/bidresult.csv", help="input the bids result path")
    parser.add_argument("--output", default="output.csv", help="output the bids path")

    return parser.parse_args()


def output(path, data):
    df = pd.DataFrame(data, columns=["time", "action", "target_price", "target_volume"])
    df.to_csv(path, index=False)

    return

def read_data(cons, gene, bid):
    df_cons = pd.read_csv(cons)
    df_gene = pd.read_csv(gene)
    diff = df_gene['generation'] - df_cons['consumption']
    df_diff = pd.DataFrame(diff)
    
    # check bidreult exist 
    bid_file = Path(bid)
    if bid_file.is_file():
        # print('bidresult file exist')
        df_bid = pd.read_csv(bid)
    else:
        # print('bidresult file do not exist')
        col = ['time','acion','target_price','target_volume',\
        'trade_price','trade_volume','status']
        df_bid = pd.DataFrame(columns=col)
        df_bid.to_csv(bid_file, index=False)
        
    date = pd.to_datetime(df_cons['time'], format='%Y-%m-%d %H:%M:%S')
    last_day = date.iloc[-1]

    return df_diff, df_bid, last_day

def Model():
    input_dim = 24*7
    output_dim = 24
    LR = 0.001
    # model
    # model
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(256, activation='relu',input_shape=(1,input_dim)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(output_dim, activation='sigmoid')
        ])
    # optimizer
    opt = keras.optimizers.Adam(learning_rate=LR)
    model.compile(optimizer = opt, loss = 'mse')
    # model.summary()

    return model

def predict(diff):
    # data preprocess
    scalar = MinMaxScaler(feature_range=(0,1))
    # reshape for MinMaxScaler
    diff = diff.to_numpy()
    diff = np.reshape(diff,(diff.shape[0],1))
    # normalization
    diff = scalar.fit_transform(diff)
    # reshape for model input
    diff = np.reshape(diff,(-1,1,diff.shape[0]))

    
    # predict
    model = Model()
    model.load_weights('model.h5')
    predict = model.predict(diff)
    predict = predict.reshape(24,1)
    predict = scalar.inverse_transform(predict)
    #plt.plot(predict)
    #plt.show()

    return predict


def action(diff, bid, last_day):
    df = pd.DataFrame(columns=['time','action','target_price','target_volume'])
    
    # date list
    date = []
    for i in range(24):
        date.append(last_day + pd.to_timedelta(i+1, unit='H'))
    df['time'] = date

    # bid strategy
    for i in range(24):
        day = df['time'].iloc[i]
        if diff[i] > 0:
            df.at[i, 'action'] = 'sell'
            df.at[i, 'target_volume'] = diff[i][0]
            df.at[i, 'target_price'] = targetPrice(day,bid,'sell')
        elif diff[i] < 0:
            df.at[i, 'action'] = 'buy'
            df.at[i, 'target_volume'] = -diff[i][0]
            df.at[i, 'target_price'] = targetPrice(day,bid,'buy')
        else:
            pass

    for i in range(24):
        if df['action'].iloc[i]==NaN:
            df.drop(i)
    # print(df) # print bidresult dataframe

    return df

def targetPrice(day, bid, status):
    # 定價
    basic_sell_price = 1.5
    basic_buy_price = 2.5

    day = day.strftime('%Y-%m-%d %H:%M:%S')

    if not ((bid['time']==day).any()):
        if status=='sell':
            price = basic_sell_price
        else:
            price = basic_buy_price
    else:
        pre = bid.loc[bid['time']==day]
        pre_action = pre['action'].mode()[0]
        pre_result = pre['status'].mode()[0]
        pre_price = pre['trade_price'].mode()[0]
        
        if status=='sell':
            if pre_action=='sell':
                if pre_result=='未成交':
                    price = pre_price - 0.1
                else:
                    price = pre_price + 0.1
            else:
                price = basic_sell_price
        else: # buy
            if pre_action=='buy':
                if pre_result=='未成交':
                    price = pre_price + 0.1
                else:
                    price = pre_price - 0.1
            else:
                price = basic_buy_price
                
    # 防止價格過低或過高
    lowest = 1.0
    highest = 3.5
    if price < lowest:
        price = lowest
    if price > highest:
        price = highest

    return price


if __name__ == "__main__":
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, TimeDistributed
    from tensorflow.keras.layers import LSTM
    from tensorflow import keras
    # make result reprodicible
    from numpy.random import seed
    seed(1)
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1" # 關掉 GPU
    import tensorflow as tf
    tf.random.set_seed(1)
    # other
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from pathlib import Path
    from sklearn.preprocessing import MinMaxScaler

    args = config()

    diff, bidresult, last_day = read_data(args.consumption,\
        args.generation, args.bidresult)
    
    # 預測未來一天的 consumptioin 及 generation data，並計算每小時多餘產電量
    diff = predict(diff)

    data = action(diff, bidresult, last_day) # bid action array
    output(args.output, data)
