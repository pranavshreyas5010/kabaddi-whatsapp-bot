import pandas as pd

EXCEL_PATH = "SKDB.xlsx"

def load_sheets():
    xl = pd.ExcelFile(EXCEL_PATH)
    return {
        name: xl.parse(name).to_dict(orient="records")
        for name in ["S_RBR"]
    }
