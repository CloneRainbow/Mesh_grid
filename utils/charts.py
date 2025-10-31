# utils/charts.py
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None

import pandas as pd

def create_cost_chart(material: str, cell: str, cost: float):
    if not PLOTLY_AVAILABLE:
        return None
    df = pd.DataFrame({"Матеріал": [material], "Вічко": [cell], "Собівартість": [cost]})
    fig = px.bar(df, x="Вічко", y="Собівартість", color="Матеріал", title="Собівартість")
    fig.update_traces(texttemplate='%{y:,.0f} грн', textposition='outside')
    return fig

def create_weight_chart(height: float, weight: float):
    if not PLOTLY_AVAILABLE:
        return None
    df = pd.DataFrame({"Висота (м)": [height], "Вага (кг)": [weight]})
    fig = px.line(df, x="Висота (м)", y="Вага (кг)", title="Вага vs Висота", markers=True)
    fig.update_traces(line_color="#00bfff", line_width=3)
    return fig
