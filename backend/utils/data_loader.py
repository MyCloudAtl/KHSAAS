import pandas as pd

def load_products(csv_path):
    """
    Load product data from a CSV file.
    :param csv_path: Path to the CSV file
    :return: DataFrame containing product information
    """
    return pd.read_csv(csv_path)