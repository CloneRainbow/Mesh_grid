# utils/charts.py
import plotly.express as px
import pandas as pd

def create_cost_chart(material: str, size: str, cost: float):
    df = pd.DataFrame({
        "Матеріал": [material],
        "Вічко": [size],
        "Собівартість (грн)": [cost]
    })
    fig = px.bar(
        df,
        x="Вічко",
        y="Собівартість (грн)",
        color="Матеріал",
        title="Собівартість за матеріалом",
        text="Собівартість (грн)"
    )
    fig.update_traces(texttemplate='%{text:.0f} грн')
    return fig

def create_weight_chart(height: float, weight: float):
    df = pd.DataFrame({
        "Висота (м)": [height],
        "Вага (кг)": [weight]
    })
    fig = px.line(
        df,
        x="Висота (м)",
        y="Вага (кг)",
        title="Загальна вага залежно від висоти",
        markers=True
    )
    fig.update_traces(line_color="#00bfff", line_width=3)
    return fig
