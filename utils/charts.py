import plotly.express as px
import pandas as pd

def create_cost_chart(material, size, cost):
    df = pd.DataFrame({"Матеріал": [material], "Вічко": [size], "Собівартість (грн)": [cost]})
    return px.bar(df, x="Вічко", y="Собівартість (грн)", color="Матеріал", title="Собівартість")

def create_weight_chart(height, weight):
    df = pd.DataFrame({"Висота (м)": [height], "Вага (кг)": [weight]})
    return px.line(df, x="Висота (м)", y="Вага (кг)", title="Вага vs Висота", markers=True)
