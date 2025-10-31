# utils/charts.py
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None

import pandas as pd

def create_cost_chart(material, size, cost):
    if not PLOTLY_AVAILABLE: return None
    df = pd.DataFrame({"Матеріал": [material], "Вічко": [size], "Собівартість": [cost]})
    return px.bar(df, x="Вічко", y="Собівартість", color="Матеріал")

def create_weight_chart(height, weight):
    if not PLOTLY_AVAILABLE: return None
    df = pd.DataFrame({"Висота": [height], "Вага": [weight]})
    return px.line(df, x="Висота", y="Вага", markers=True)
