# power_bidding
Design an agent for bidding power to minimize your electricity bill

## Data
1. generation.csv：前七天的產電資料(每小時為單位)
2. consumption.csv：前七天的用電資料(每小時為單位)
3. bidresult.csv：前一天的競標結果(每小時為單位)
4. output.csv：未來一天的競標動作(每小時為單位)
5. model.h5：預測未來一天產用電資料差的 model weights

## LSTM model
經過實驗發現，預測產用電量差異的準確度優於單純預測產電或是用電資料。因此利用前七天的產電、用電資料差來預測未來一天的產電、用電資料差。
模型採用 mlp model，架構如下：

![image](https://github.com/joeroy5376998/power_bidding/blob/main/image/model_structure.PNG)

訓練結果：

![image](https://github.com/joeroy5376998/power_bidding/blob/main/image/predict.png)

## 競標策略
因為模型的輸出為預測未來24小時的產電、用電量差異，因此設定每一小時做一次交易。
若沒有 bidresult.csv 可以參考，則分別設定買價及賣價：
sell = 1.5
buy = 2.5
若有 bidresult.csv，則可以根據前一天的交易結果來微調價格：
1. 若交易動作為 sell：
    a. 若前一天同一時段交易動作也是 sell，且"有成交"或是"部分成交"，價格 + 0.1
    b. 若前一天同一時段交易動作也是 sell，且"未成交"，價格 - 0.1
    c. 若前一天同一時段交易動作為 buy，價格設為 1.5
2. 若交易動作為 buy：
    a. 若前一天同一時段交易動作也是 buy，且"有成交"或是"部分成交"，價格 - 0.1
    b. 若前一天同一時段交易動作也是 buy，且"未成交"，價格 + 0.1
    c. 若前一天同一時段交易動作為 sell，價格設為 2.5
