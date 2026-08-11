# Case DconData — Distribuidora de Alimentos Funcionais e Suplementos

Consultor de Análise de Dados
**Autor:** Gabriel Garcia

## Por onde começar

1. **[`Case_Distribuidora_Diagnostico.pptx`](/Conclusão/Case_Distribuidora_Diagnostico.pptx))** — material executivo. Comece por aqui: sumário executivo, diagnóstico, segmentação e recomendações priorizadas.
2. **[`Case_Distribuidora_Analise.ipynb`](./codigo/Case_Distribuidora_Analise.ipynb)** — material analítico. Todo o raciocínio e cálculo documentado célula a célula (renderiza direto aqui no GitHub).
3. **[`Registro_Premissas_Limitacoes.docx`](./Conclusão/Registro_Premissas_Limitacoes.docx)** — premissas, limitações, ferramentas escolhidas, uso de IA e plano de trabalho.
4. **[`integracao_bacen_cambio.py`](./codigo/API.py)** — código de acesso à fonte pública (API do Banco Central, série PTAX).

## Resumo do diagnóstico

O crescimento recente está sendo parcialmente comprado com desconto, frete
subsidiado e custo de aquisição crescente — e a operação, com capacidade
fixa, já não sustenta o ritmo atual. A recomendação não é crescer menos: é
redirecionar canal, cliente e produto antes de acelerar mais.

## Estrutura do repositório

```
.
├── Case_Distribuidora_Diagnostico.pptx     # material executivo
├── Case_Distribuidora_Analise.ipynb        # material analítico (Python/pandas)
├── Registro_Premissas_Limitacoes.docx      # premissas, limitações, plano de trabalho
├── integracao_bacen_cambio.py              # integração com fonte pública (BACEN)
├── dados/                                  # bases originais fornecidas no case
│   ├── clientes.csv
│   ├── compras.csv
│   ├── devolucoes.csv
│   ├── estoque.csv
│   ├── itens_pedidos.csv
│   ├── marketing.csv
│   ├── operacao.csv
│   ├── pedidos.csv
│   ├── produtos.csv
│   └── capacidade.csv
└── README.md
```

## Stack utilizada

Python (pandas, matplotlib), Jupyter Notebook, PowerPoint, API do Banco
Central do Brasil (SGS/PTAX).
