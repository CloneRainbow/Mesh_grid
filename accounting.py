from finance import get_cash_flow_df
import pandas as pd

def calculate_profit_loss():
    df = get_cash_flow_df()
    if df.empty:
        return pd.DataFrame()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    summary = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    summary["income"] = summary.get("income", 0)
    summary["expense"] = summary.get("expense", 0)
    summary["profit"] = summary["income"] - summary["expense"]
    return summary.reset_index()[["month", "income", "expense", "profit"]]
