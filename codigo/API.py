"""
Integração com dados públicos — Banco Central do Brasil (BACEN)
Case: Distribuidora de alimentos funcionais e suplementos

Objetivo:
    Enriquecer compras.csv com a taxa de câmbio oficial (PTAX - dólar venda,
    série SGS 1) para:
      1) Preencher os 593 registros de taxa_cambio_interna nulos
         (compras nacionais não têm câmbio, mas também há uma parcela de
         compras IMPORTADO sem o valor preenchido).
      2) Comparar a taxa interna praticada pela empresa com a PTAX do dia do
         evento de câmbio (data_evento_cambio), evidenciando spread cambial
         e o quanto da variação de custo de compra é explicada por câmbio
         vs. negociação com fornecedor.

Fonte: Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS)
       Série 1 = Taxa de câmbio - Livre - Dólar americano (venda) - diário
       Documentação: https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio---livre---dolar-americano-venda---diario

Observação: rode este script em um ambiente com acesso normal à internet
(seu notebook local, Colab, etc). A API do BACEN bloqueia user-agents de
scraping/robôs automatizados, o que impediu a execução direto no sandbox
usado para o restante da análise — mas é a chamada padrão documentada
pelo próprio BACEN e usada por bibliotecas como python-bcb.
"""

import pandas as pd
import requests

arq_compras = r"C:\Users\ghgarcia\.maquina_virtual\Case_dcondata\Case_AnalistaDados\dados\compras.csv"
# ---------------------------------------------------------------------------
# 1) Buscar a série de câmbio PTAX (venda) no período coberto pelos dados
# ---------------------------------------------------------------------------
URL_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"

def buscar_ptax(data_inicial: str, data_final: str) -> pd.DataFrame:
    """
    data_inicial / data_final no formato 'dd/mm/aaaa'.
    Retorna DataFrame com colunas: data (datetime), ptax_venda (float)
    """
    params = {
        "formato": "json",
        "dataInicial": data_inicial,
        "dataFinal": data_final,
    }
    resp = requests.get(URL_SGS, params=params, timeout=30)
    resp.raise_for_status()
    dados = resp.json()
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["ptax_venda"] = df["valor"].astype(float)
    return df[["data", "ptax_venda"]].sort_values("data").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2) Carregar compras.csv e preparar para o merge
# ---------------------------------------------------------------------------
compras = pd.read_csv(arq_compras, parse_dates=["data_evento_cambio", "data_pedido_compra"])

# cobre toda a janela do case com folga
ptax = buscar_ptax("01/01/2025", "31/07/2026")

# ---------------------------------------------------------------------------
# 3) Merge "as-of" — pega a PTAX do dia do evento de câmbio, ou o último dia
#    útil anterior (câmbio não é publicado em fins de semana/feriado)
#
#    merge_asof exige que a chave de junção não tenha nulos, então
#    separamos as compras COM data_evento_cambio preenchida (fazem o merge
#    real, pela data do evento) das que estão SEM (compras nacionais ou
#    lacunas — usamos a data_pedido_compra como aproximação).
# ---------------------------------------------------------------------------
ptax_sorted = ptax.sort_values("data")

com_evento = compras[compras["data_evento_cambio"].notna()].sort_values("data_evento_cambio").copy()
sem_evento = compras[compras["data_evento_cambio"].isna()].sort_values("data_pedido_compra").copy()

com_evento = pd.merge_asof(
    com_evento,
    ptax_sorted,
    left_on="data_evento_cambio",
    right_on="data",
    direction="backward",
)

sem_evento = pd.merge_asof(
    sem_evento,
    ptax_sorted,
    left_on="data_pedido_compra",
    right_on="data",
    direction="backward",
)
sem_evento["ptax_aproximada_por_data_pedido"] = True
com_evento["ptax_aproximada_por_data_pedido"] = False

enriquecido = pd.concat([com_evento, sem_evento], ignore_index=True)

# 4) Preenche taxa_cambio_interna nula com a PTAX (apenas para origem IMPORTADO)
mask_fill = enriquecido["taxa_cambio_interna"].isna() & (enriquecido["origem_fornecedor"] == "IMPORTADO")
enriquecido.loc[mask_fill, "taxa_cambio_interna_tratada"] = enriquecido.loc[mask_fill, "ptax_venda"]
enriquecido["taxa_cambio_interna_tratada"] = enriquecido["taxa_cambio_interna_tratada"].fillna(
    enriquecido["taxa_cambio_interna"]
)
enriquecido["taxa_preenchida_com_ptax"] = mask_fill

# 5) Spread cambial: quanto a empresa pagou de câmbio vs. a taxa oficial do dia
enriquecido["spread_cambial_pct"] = (
    (enriquecido["taxa_cambio_interna"] - enriquecido["ptax_venda"]) / enriquecido["ptax_venda"] * 100
)

# ---------------------------------------------------------------------------
# 6) Salvar resultado
# ---------------------------------------------------------------------------
enriquecido.to_csv("compras_enriquecido_ptax.csv", index=False)

print(f"Registros com taxa_cambio_interna preenchida via PTAX: {mask_fill.sum()}")
print(f"Spread cambial médio (empresa vs. PTAX oficial): "
      f"{enriquecido['spread_cambial_pct'].mean():.2f}%")
print("Arquivo salvo: compras_enriquecido_ptax.csv")