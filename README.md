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
