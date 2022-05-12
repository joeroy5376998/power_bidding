# power_bidding
Design an agent for bidding power to minimize your electricity bill

## Data
1. generation.csv：前七天的產電資料(每小時為單位)
2. consumption.csv：前七天的用電資料(每小時為單位)
3. bidresult.csv：前一天的競標結果(每小時為單位)
4. output.csv：未來一天的競標動作(每小時為單位)
5. generation_model.h5：預測未來一天產電資料的 LSTM model weights
6. consumption_model.h5：預測未來一天用電資料的 LSTM model weights

## 系統流程圖
![image](https://github.com/joeroy5376998/power_bidding/blob/main/image/flow_chart.png)

## LSTM model
以前一天的產電、用電資料來預測未來一天的產電、用電資料。
模型架構：
<img src="https://github.com/joeroy5376998/power_bidding/blob/main/image/model_structure.PNG" width="100" height="100"><br/>

訓練結果：
1. 產電資料預測

<img src="https://github.com/joeroy5376998/power_bidding/blob/main/image/generation.png" width="50" height="50"><br/>

2. 用電資料預測

<img src="https://github.com/joeroy5376998/power_bidding/blob/main/image/consumption.png" width="50" height="50"><br/>

3. 剩餘可用電量預測(產電減用電)

<img src="https://github.com/joeroy5376998/power_bidding/blob/main/image/diff.png" width="50" height="50"><br/>

## 競標策略
