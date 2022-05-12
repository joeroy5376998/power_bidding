
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

    return df_cons, df_gene, df_bid, last_day

def Model():
    LR = 0.001
    # model
    model = Sequential()
    model.add(LSTM(128, activation = "relu", return_sequences = True, input_shape = (24, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(128, activation = "relu", return_sequences = True))
    model.add(TimeDistributed(Dense(1)))
    # optimizer
    opt = keras.optimizers.Adam(learning_rate=LR)
    model.compile(optimizer = opt, loss = 'mse')
    # model.summary()

    return model

def predict(gene, cons):
    # data preprocess
    scalar = MinMaxScaler(feature_range=(0,1))
    generation = gene['generation'][-24:]
    consumption = cons['consumption'][-24:]
    # reshape for MinMaxScaler
    generation = generation.to_numpy()
    consumption = consumption.to_numpy()
    generation = np.reshape(generation,(generation.shape[0],1))
    consumption = np.reshape(consumption,(generation.shape[0],1))
    # normalization
    generation = scalar.fit_transform(generation)
    consumption = scalar.fit_transform(consumption)
    # reshape for lstm
    generation = np.reshape(generation,(1,generation.shape[0],1))
    consumption = np.reshape(consumption,(1,consumption.shape[0],1))

    
    # predict generation
    generation_model = Model()
    generation_model.load_weights('generation_model.h5')
    predict_gene = generation_model.predict(generation)
    predict_gene = predict_gene.reshape(predict_gene.shape[1],predict_gene.shape[0])
    predict_gene = scalar.inverse_transform(predict_gene)

    # predict consumption
    consumption_model = Model()
    consumption_model.load_weights('consumption_model.h5')
    predict_cons = consumption_model.predict(consumption)
    predict_cons = predict_cons.reshape(predict_cons.shape[1],predict_cons.shape[0])
    predict_cons = scalar.inverse_transform(predict_cons)

    predict_diff = predict_gene - predict_cons
    
    # plt.plot(predict_diff)
    # plt.show()

    return predict_diff


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
    if not ((bid['time']==day).any()):
        price = 3
    else:
        pre_action = bid.loc[day]['action']
        pre_result = bid.loc[day]['status']
        pre_price = bid.loc[day]['trade_price']
        if status=='sell':
            if pre_action=='sell':
                if pre_result=='未成交':
                    price = pre_price - 0.5
                else:
                    price = pre_price + 0.5
            else:
                price = 4
        else: # buy
            if pre_action=='buy':
                if pre_result=='未成交':
                    price = pre_price + 0.5
                else:
                    price = pre_price - 0.5
            else:
                price = 4
                
    # 防止價格過低或過高
    lowest = 2
    highest = 6
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
    import tensorflow as tf
    tf.random.set_seed(1)
    # other
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    from pathlib import Path
    from sklearn.preprocessing import MinMaxScaler

    args = config()

    consumption, generation, bidresult, last_day = read_data(args.consumption,\
        args.generation, args.bidresult)
    
    # 預測未來一天的 consumptioin 及 generation data，並計算每小時多餘產電量
    diff = predict(generation, consumption)

    data = action(diff, bidresult, last_day) # bid action array
    output(args.output, data)