import pandas as pd

import sys
sys.path.append(".")

class MarketFilter:
    def __init__(self, min_trading_volume=0, min_market_cap=0, max_market_cap=1e+20, market_cap_path="data/market_cap.csv"):
        self.min_trading_volume = min_trading_volume
        self.min_market_cap = min_market_cap
        self.max_market_cap = max_market_cap
        self.market_cap = pd.read_csv(market_cap_path, dtype={'Code': str})

    def filter(self, dataset):
        filtered_by_volume = dataset[dataset['Trading_Volume'] >= self.min_trading_volume]
        merged_data = filtered_by_volume.merge(self.market_cap, on='Code', how='left')
        filtered_by_market_cap = merged_data[(merged_data['MarketCap'] >= self.min_market_cap) & (merged_data['MarketCap'] <= self.max_market_cap)]
        
        return filtered_by_market_cap


if __name__ == "__main__":
    from dataset_constructor import NonSequentialDatasetConstructor

    import os
    import random
    def get_random_csv_files(directory, num_files=100, random_state=42):
        random.seed(random_state)
        all_csv_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
        selected_files = random.sample(all_csv_files, min(num_files, len(all_csv_files)))
        return selected_files

    file_paths = get_random_csv_files("data/csv")

    # file_paths = ["data/csv/005930.csv", "data/csv/000020.csv", "data/csv/001360.csv", "data/csv/900250.csv"]
    dataset_constructor = NonSequentialDatasetConstructor(file_paths)
    dataset_constructor.get_dataset()

    train_data, val_data, test_data = dataset_constructor.split_dataset(train_period='3Y', test_period='1Y', val_ratio=0.2)

    print(f"Before filtering - len(train_data) : {len(train_data)}, len(val_data) : {len(val_data)}, len(test_data) : {len(test_data)}")

    trading_volume_filter = MarketFilter(min_trading_volume=1e9, min_market_cap=1e10, max_market_cap=1e12)
    train_data = trading_volume_filter.filter(train_data)
    val_data = trading_volume_filter.filter(val_data)
    test_data = trading_volume_filter.filter(test_data)

    print(f"After filtering - len(train_data) : {len(train_data)}, len(val_data) : {len(val_data)}, len(test_data) : {len(test_data)}")