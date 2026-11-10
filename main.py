from pathlib import Path

import pandas as pd

PASTA = Path(__file__).parent
ARQUIVO_BRUTO = PASTA / "dados" / "bruto" / "Sample - Superstore.csv"
ARQUIVO_TRATADO = PASTA / "dados" / "tratado" / "Superstore_Tratado.csv"

# --- 1. CARGA ---
df = pd.read_csv(ARQUIVO_BRUTO, encoding="latin1")
print(f"Linhas lidas: {len(df)}")

# --- 2. QUALIDADE DOS DADOS ---
print("\n--- QUALIDADE ---")
print(f"Linhas duplicadas: {df.duplicated().sum()}")
print(f"Valores nulos (total): {df.isna().sum().sum()}")
print(f"Row ID é único: {df['Row ID'].is_unique}")
print(f"Pedidos distintos (Order ID): {df['Order ID'].nunique()}")

df = df.drop_duplicates()

# --- 3. TIPOS E NOVAS COLUNAS ---
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])
df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

df["Profit Margin"] = df["Profit"] / df["Sales"]

# Faixas de desconto
df["Faixa_Desconto"] = pd.cut(
    df["Discount"],
    bins=[-0.001, 0.0, 0.20, 0.40, 1.0],
    labels=["Sem desconto", "Até 20%", "21% a 40%", "Acima de 40%"],
)

# --- 4. RESUMO FINANCEIRO ---
faturamento_total = df["Sales"].sum()
lucro_total = df["Profit"].sum()
margem_consolidada = lucro_total / faturamento_total * 100

print("\n--- RESUMO FINANCEIRO ---")
print(f"Faturamento total: US$ {faturamento_total:,.2f}")
print(f"Lucro total:       US$ {lucro_total:,.2f}")
print(f"Margem consolidada (lucro / faturamento): {margem_consolidada:.2f}%")

# --- 5. CATEGORIA ---
print("\n--- POR CATEGORIA ---")
por_categoria = df.groupby("Category").agg(
    Vendas=("Sales", "sum"), Lucro=("Profit", "sum")
)
por_categoria["Margem (%)"] = por_categoria["Lucro"] / por_categoria["Vendas"] * 100
por_categoria["% das vendas"] = por_categoria["Vendas"] / faturamento_total * 100
print(por_categoria.round(2).sort_values("Lucro", ascending=False).to_string())

# --- 6. SUBCATEGORIA (todas as 17) ---
print("\n--- POR SUBCATEGORIA ---")
por_sub = df.groupby(["Category", "Sub-Category"]).agg(
    Vendas=("Sales", "sum"), Lucro=("Profit", "sum")
)
por_sub["Margem (%)"] = por_sub["Lucro"] / por_sub["Vendas"] * 100
print(por_sub.round(2).sort_values("Lucro").to_string())

# --- 7. DESCONTO ---
print("\n--- POR NÍVEL DE DESCONTO ---")
por_nivel = df.groupby("Discount").agg(
    Itens=("Row ID", "count"), Lucro_Medio=("Profit", "mean"), Lucro_Total=("Profit", "sum")
)
print(por_nivel.round(2).to_string())

print("\n--- POR FAIXA DE DESCONTO ---")
por_faixa = df.groupby("Faixa_Desconto", observed=False).agg(
    Itens=("Row ID", "count"),
    Pedidos=("Order ID", "nunique"),
    Lucro_Medio=("Profit", "mean"),
    Lucro_Total=("Profit", "sum"),
    Vendas=("Sales", "sum"),
)
por_faixa["Margem (%)"] = por_faixa["Lucro_Total"] / por_faixa["Vendas"] * 100
print(por_faixa.round(2).to_string())

# --- 8. DESCONTO x CATEGORIA:
print("\n--- LUCRO MÉDIO: FAIXA x CATEGORIA ---")
print(
    df.pivot_table(
        index="Faixa_Desconto", columns="Category", values="Profit",
        aggfunc="mean", observed=False,
    ).round(2).to_string()
)
print("\n--- ITENS POR FAIXA x CATEGORIA ---")
print(
    df.pivot_table(
        index="Faixa_Desconto", columns="Category", values="Row ID",
        aggfunc="count", observed=False,
    ).to_string()
)

# --- 9. SALVAR
ARQUIVO_TRATADO.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(ARQUIVO_TRATADO, index=False)
print(f"\nArquivo tratado salvo em: {ARQUIVO_TRATADO}")
