"""
Save pandas DataFrames to CSV files
"""
import pandas as pd


def save_csv(df: pd.DataFrame, filepath: str) -> None:
    """
    Save a pandas DataFrame to a CSV file.
    
    Args:
        df: pandas DataFrame to save
        filepath: Destination file path
    """
    df.to_csv(filepath, index=False)
    print(f"✅ Saved CSV to {filepath}")


if __name__ == "__main__":
    # Test saving
    import pandas as pd
    
    test_df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [25, 30]
    })
    
    save_csv(test_df, "data/test_output.csv")

