# utils/reports_finance.py — ПОВНИЙ, ПРАЦЮЄ
import pandas as pd
from io import BytesIO

def export_pl_to_excel(pl_df: pd.DataFrame) -> BytesIO:
    """
    Експортує P&L звіт у Excel файл (BytesIO)
    Працює без reportlab, лише pandas + openpyxl
    """
    # Якщо DataFrame порожній — створюємо заглушку
    if pl_df.empty:
        pl_df = pd.DataFrame({
            "month": ["Немає даних"],
            "income": [0.0],
            "expense": [0.0],
            "profit": [0.0]
        })

    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pl_df.to_excel(writer, sheet_name="P&L Звіт", index=False)

        # Отримуємо аркуш
        workbook = writer.book
        worksheet = writer.sheets["P&L Звіт"]

        # Автоматична ширина стовпців
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Формат чисел: ₴#,##0.00
        from openpyxl.styles import numbers
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=2, max_col=4):
            for cell in row:
                cell.number_format = '#,##0.00'

    output.seek(0)
    return output
