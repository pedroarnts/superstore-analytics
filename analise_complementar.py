"""
Análise complementar: correlações e tendência por ano.

Execute depois do main.py, que gera dados/tratado/Superstore_Tratado.csv:
    python analise_complementar.py
"""

from pathlib import Path

import pandas as pd

PASTA = Path(__file__).parent
ARQUIVO_TRATADO = PASTA / "dados" / "tratado" / "Superstore_Tratado.csv"

df = pd.read_csv(ARQUIVO_TRATADO, parse_dates=["Order Date", "Ship Date"])

# --- 1. CORRELAÇÕES ---
# Pearson mede relação em linha reta; Spearman mede se uma variável sobe/desce
# junto com a outra, mesmo que não seja em linha reta.
colunas = ["Discount", "Profit", "Sales", "Quantity"]

print("--- CORRELAÇÃO DE PEARSON ---")
print(df[colunas].corr(method="pearson").round(3).to_string())

print("\n--- CORRELAÇÃO DE SPEARMAN ---")
print(df[colunas].corr(method="spearman").round(3).to_string())

# --- 2. TENDÊNCIA POR ANO ---
por_ano = df.groupby(df["Order Date"].dt.year).agg(
    Vendas=("Sales", "sum"),
    Lucro=("Profit", "sum"),
    Pedidos=("Order ID", "nunique"),
)
por_ano["Margem (%)"] = por_ano["Lucro"] / por_ano["Vendas"] * 100
por_ano.index.name = "Ano"

print("\n--- VENDAS, LUCRO E MARGEM POR ANO ---")
print(por_ano.round(2).to_string())
