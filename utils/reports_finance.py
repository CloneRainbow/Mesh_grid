from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import pandas as pd

def generate_pl_pdf(pl_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("P&L Звіт", styles["Title"]))
    data = [["Місяць", "Дохід", "Витрати", "Прибуток"]]
    for _, r in pl_df.iterrows():
        data.append([r["month"], f"₴{r['income']:,.0f}", f"₴{r['expense']:,.0f}", f"₴{r['profit']:,.0f}"])
    table = Table(data)
    table.setStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black)])
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer
