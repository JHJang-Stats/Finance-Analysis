from concurrent.futures import ProcessPoolExecutor
import pandas as pd
from sklearn.model_selection import train_test_split

import sys
sys.path.append(".")

from strategy.sell_strategy import SellStrategy
from indicators import TradingIndicators

class NonSequentialDatasetConstructor:
    def __init__(self, file_paths, profit_threshold=1.05, loss_threshold=0.95, auto_sell_period=20, **kwargs):
        self.file_paths = file_paths
        self.profit_threshold = profit_threshold
        self.loss_threshold = loss_threshold
        self.auto_sell_period = auto_sell_period
        self.kwargs = kwargs
        self.dataset = pd.DataFrame()

    def construct_dataset_for_file(self, file_path):
        indicators = TradingIndicators(file_path, **self.kwargs)
        indicators.calculate_all()

        strategy = SellStrategy(indicators.data, self.profit_threshold, self.loss_threshold, self.auto_sell_period)
        strategy.apply_strategy()

        return indicators.data

    def construct_dataset(self):
        with ProcessPoolExecutor() as executor:
            results = executor.map(self.construct_dataset_for_file, self.file_paths)
        
        for result in results:
            self.dataset = pd.concat([self.dataset, result], ignore_index=True)

    def split_dataset(self, train_period='3Y', test_period='1Y', val_ratio=0.2):
        # 데이터를 날짜 기준으로 정렬
        self.dataset.sort_values('Date', inplace=True)

        # 사용자가 정의한 기간에 따라 데이터 분할
        cutoff_date_train_test = self.dataset['Date'].max() - pd.DateOffset(years=int(train_period[:-1]))
        cutoff_date_test = self.dataset['Date'].max() - pd.DateOffset(years=int(test_period[:-1]))

        train_test_data = self.dataset[self.dataset['Date'] < cutoff_date_train_test]
        test_data = self.dataset[(self.dataset['Date'] >= cutoff_date_train_test) & (self.dataset['Date'] < cutoff_date_test)]

        # 훈련 및 검증 데이터셋 분할
        train_data, val_data = train_test_split(train_test_data, test_size=val_ratio, random_state=42)

        train_data.set_index('Date', inplace=True)
        val_data.set_index('Date', inplace=True)
        test_data.set_index('Date', inplace=True)

        return train_data, val_data, test_data

    def get_dataset(self):
        if self.dataset.empty:
            self.construct_dataset()
        return self.dataset

if __name__ == "__main__":
    file_paths = ["data/csv/005930.csv", "data/csv/000020.csv"]
    dataset_constructor = NonSequentialDatasetConstructor(
        file_paths=file_paths,
        profit_threshold=1.15,
        loss_threshold=0.95,
        auto_sell_period=20,
        # Add any other kwargs for TradingIndicators if needed
    )
    dataset_constructor.get_dataset()
    train_data, val_data, test_data = dataset_constructor.split_dataset(train_period='3Y', test_period='1Y', val_ratio=0.2)
    print("Train Dataset:")
    print(train_data.tail())
    print("\nValidation Dataset:")
    print(val_data.tail())
    print("\nTest Dataset:")
    print(test_data.tail())
    print("\nDataset Columns:")
    print(train_data.columns)
