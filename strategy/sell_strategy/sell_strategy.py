import numpy as np
import pandas as pd

class SellStrategy:
    """
    A trading strategy class that determines whether a given stock
    will hit a specified profit or loss target within a auto_sell_period-day window or ends with an auto-sell based on the closing price after auto_sell_period days.
    """
    def __init__(self, data, profit_threshold=1.05, loss_threshold=0.95, auto_sell_period=20):
        self.data = data
        self.profit_threshold = profit_threshold
        self.loss_threshold = loss_threshold
        self.auto_sell_period = auto_sell_period

    def apply_strategy(self):
        self.data.sort_index(inplace=True)  # 데이터가 시간 순서대로 정렬되었는지 확인

        # Initialize columns for tracking
        self.data['Target'] = np.nan  # 최종 수익률을 저장할 새로운 열

        for i in range(len(self.data) - self.auto_sell_period):  # 마지막 auto_sell_period은 자동 청산 확인 불가
            window_data = self.data.iloc[i:i+21]  # 현재 포함 auto_sell_period 데이터 선택
            target_profit_price = self.data.iloc[i]['Close'] * self.profit_threshold
            target_loss_price = self.data.iloc[i]['Close'] * self.loss_threshold

            profit_hit_day = None
            loss_hit_day = None

            # Check for profit or loss targets hit within the next auto_sell_period days
            for j, row in window_data.iterrows():
                if row['High'] >= target_profit_price and profit_hit_day is None:
                    profit_hit_day = j
                if row['Low'] <= target_loss_price and loss_hit_day is None:
                    loss_hit_day = j

            # Determine the outcome based on the trading strategy
            if profit_hit_day is not None and loss_hit_day is not None:
                if profit_hit_day == loss_hit_day:  # 동일한 날에 발생한 경우
                    final_return = (window_data.loc[profit_hit_day, 'Close'] / self.data.iloc[i]['Close'] - 1) * 100
                else:  # 먼저 발생한 조건 기준으로 청산
                    earlier_day = min(profit_hit_day, loss_hit_day)
                    final_return = (window_data.loc[earlier_day, 'Close'] / self.data.iloc[i]['Close'] - 1) * 100
            elif profit_hit_day is not None:
                final_return = (window_data.loc[profit_hit_day, 'Close'] / self.data.iloc[i]['Close'] - 1) * 100
            elif loss_hit_day is not None:
                final_return = (window_data.loc[loss_hit_day, 'Close'] / self.data.iloc[i]['Close'] - 1) * 100
            else:  # 자동 청산일
                auto_sell_return = (window_data.iloc[-1]['Close'] / self.data.iloc[i]['Close'] - 1) * 100
                final_return = auto_sell_return

            self.data.at[self.data.index[i], 'Target'] = final_return
        
        self.data.dropna(subset=['Target'], inplace=True)

if __name__ == "__main__":
    file_path = "data/csv/005930.csv"
    market_data = pd.read_csv(file_path, dtype={'Code': str})
    market_data['Date'] = pd.to_datetime(market_data['Date'])
    market_data.set_index('Date', inplace=True)

    strategy = SellStrategy(data=market_data, profit_threshold=1.15, loss_threshold=0.95, auto_sell_period=20)
    strategy.apply_strategy()
    print(strategy.data.head())
    print(strategy.data.tail())
