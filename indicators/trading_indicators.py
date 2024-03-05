import pandas as pd
import numpy as np

class TradingIndicators:
    def __init__(self, file_path, **kwargs):
        self.data = pd.read_csv(file_path, dtype={'Code': str})
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        # self.data.set_index('Date', inplace=True)
        self.kwargs = kwargs

    def calculate_RSI(self, window=14):
        window = self.kwargs.get('rsi_window', window)
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def calculate_MACD(self, fast_period=12, slow_period=26, signal_period=9):
        fast_period = self.kwargs.get('macd_fast_period', fast_period)
        slow_period = self.kwargs.get('macd_slow_period', slow_period)
        signal_period = self.kwargs.get('macd_signal_period', signal_period)
        exp1 = self.data['Close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=slow_period, adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['MACD_Signal'] = self.data['MACD'].ewm(span=signal_period, adjust=False).mean()

    def calculate_moving_averages(self, periods=[20, 50, 100, 200]):
        periods = self.kwargs.get('ma_periods', periods)
        for period in periods:
            self.data[f'SMA_{period}'] = self.data['Close'].rolling(window=period).mean()
            self.data[f'EMA_{period}'] = self.data['Close'].ewm(span=period, adjust=False).mean()

    def calculate_trading_volume(self):
        self.data['Trading_Volume'] = self.data['Close'] * self.data['Volume']

    def calculate_vwap(self):
        cum_volume_price = (self.data['Volume'] * (self.data['High'] + self.data['Low'] + self.data['Close']) / 3).cumsum()
        cum_volume = self.data['Volume'].cumsum()
        self.data['VWAP'] = cum_volume_price / cum_volume

    def calculate_moving_average_trading_volume(self, window=20):
        window = self.kwargs.get('matv_window', window)
        self.data[f'MA_Trading_Volume_{window}'] = self.data['Trading_Volume'].rolling(window=window).mean()

    def calculate_volume_roc(self, window=20):
        window = self.kwargs.get('vroc_window', window)
        self.data[f'Volume_ROC_{window}'] = self.data['Trading_Volume'].pct_change(periods=window) * 100

    def calculate_accumulated_trading_volume(self):
        self.data['Accumulated_Trading_Volume'] = self.data['Trading_Volume'].cumsum()

    def calculate_all(self):
        self.calculate_RSI()
        self.calculate_MACD()
        self.calculate_moving_averages()
        self.calculate_trading_volume()
        self.calculate_vwap()
        self.calculate_moving_average_trading_volume()
        self.calculate_volume_roc()
        self.calculate_accumulated_trading_volume()

    def display_indicators(self):
        print(self.data.tail())

if __name__ == "__main__":
    file_path = "data/csv/005930.csv"
    market_data = TradingIndicators(
        file_path,
        # rsi_window=14,
        # macd_fast_period=12,
        # macd_slow_period=26,
        # macd_signal_period=9,
        # ma_periods=[20, 50, 100, 200],
        # matv_window=20,
        # vroc_window=20
    )
    market_data.calculate_all()
    market_data.display_indicators()