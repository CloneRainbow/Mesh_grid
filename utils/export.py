import pandas as pd

def export_to_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    return path

def export_to_excel(df: pd.DataFrame, path: str):
    df.to_excel(path, index=False)
    return path
