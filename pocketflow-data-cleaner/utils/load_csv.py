"""
Load CSV files into pandas DataFrames
"""
import pandas as pd


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        pandas DataFrame
    """
    df = pd.read_csv(filepath)
    return df


if __name__ == "__main__":
    # Test loading
    import os
    test_file = "data/test.csv"
    
    if os.path.exists(test_file):
        df = load_csv(test_file)
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        print(df.head())
    else:
        print(f"Test file {test_file} not found")

