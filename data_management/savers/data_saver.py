import os
import pandas as pd
from typing import Dict

class DataSaver:
    """
    A class to save stock data to HDF5 or CSV files.

    Attributes:
        filepath (str): The base directory path where the files will be saved.
    """
    def __init__(self, filepath: str) -> None:
        """
        Initializes the DataSaver with a base directory path.

        Parameters:
            filepath (str): The base directory path for saving files.
        """
        self.filepath = filepath

    def save_to_hdf5(self, stock_data: Dict[str, pd.DataFrame]) -> None:
        """
        Saves the given stock data to an HDF5 file.

        Each item in the stock_data dictionary is saved as a separate table
        within the HDF5 file, identified by the stock code.

        Parameters:
            stock_data (Dict[str, pd.DataFrame]): A dictionary where each key is a
                                                  stock code and each value is a DataFrame
                                                  containing the stock's data.
        """
        with pd.HDFStore(self.filepath, mode='w') as store:
            for code, df in stock_data.items():
                store.put(code, df, format='table', data_columns=True)
        print(f"All data saved to {self.filepath}")

    def save_to_csv(self, stock_data: Dict[str, pd.DataFrame]) -> None:
        """
        Saves the given stock data to CSV files in the specified directory.

        Each stock's data is saved to a separate CSV file, named after the stock code.
        The DataFrame's index is reset before saving to ensure the index is included as a column.

        Parameters:
            stock_data (Dict[str, pd.DataFrame]): A dictionary where each key is a
                                                  stock code and each value is a DataFrame
                                                  containing the stock's data.
        """
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        
        for code, df in stock_data.items():
            file_path = os.path.join(self.filepath, f"{code}.csv")
            df.reset_index().to_csv(file_path, index=False)
        print(f"All data saved to CSV in {self.filepath}")
