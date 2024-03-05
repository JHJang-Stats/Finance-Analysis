import pandas as pd
import FinanceDataReader as fdr
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class KoreaStockFetcher:
    def __init__(self, start_year='2017'):
        self.start_year = start_year
        self.stock_data = {}
    
    def fetch_stock_data(self, code):
        stock_data = fdr.DataReader(code, self.start_year)
        stock_data['Code'] = code
        return stock_data
    
    def fetch_all(self, code_list):
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.fetch_stock_data, code): code for code in code_list}
            for future in tqdm(as_completed(futures), total=len(futures)):
                code = futures[future]
                try:
                    data = future.result()
                    self.stock_data[code] = data
                except Exception as e:
                    print(f"Failed to fetch data for {code}: {e}")
        return self.stock_data