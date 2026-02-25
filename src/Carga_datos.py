import os
import pandas as pd

def cargar_datos():
    df = pd.read_excel(r'C:\Users\MSI\Desktop\PI5-ClaudiaRivero\MLops-dtpt01\Base_de_datos.xlsx')
    return df

