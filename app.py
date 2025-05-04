
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go

st.set_page_config(page_title="Analisador Técnico B3", layout="wide")
st.title("📈 Analisador Técnico - B3 em Tempo Quase Real")

# Escolha do ativo e intervalo
ativo = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA)", value="PETR4.SA")
intervalo = st.selectbox("Intervalo de tempo", ["1m", "5m", "15m", "30m", "1h", "1d"], index=2)
periodo = st.selectbox("Período", ["1d", "5d", "7d", "1mo", "3mo"], index=1)

# Baixar os dados
df = yf.download(ativo, interval=intervalo, period=periodo)

if df.empty:
    st.error("Não foi possível obter os dados. Verifique o ticker ou o intervalo.")
    st.stop()

# Indicadores técnicos
df['MME9'] = ta.trend.ema_indicator(df['Close'], window=9).ema_indicator()
df['MME21'] = ta.trend.ema_indicator(df['Close'], window=21).ema_indicator()
df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
df['Sinal'] = ''

# Geração dos sinais
for i in range(1, len(df)):
    if df['MME9'][i] > df['MME21'][i] and df['MME9'][i-1] <= df['MME21'][i-1] and df['RSI'][i] < 70:
        df.at[df.index[i], 'Sinal'] = 'COMPRA'
    elif df['MME9'][i] < df['MME21'][i] and df['MME9'][i-1] >= df['MME21'][i-1]:
        df.at[df.index[i], 'Sinal'] = 'VENDA'

# Últimos dados
st.subheader("📋 Últimos Sinais")
st.dataframe(df[['Close', 'MME9', 'MME21', 'RSI', 'Sinal']].dropna().tail(10))

# Gráfico
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Preço', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df.index, y=df['MME9'], name='MME 9', line=dict(color='green')))
fig.add_trace(go.Scatter(x=df.index, y=df['MME21'], name='MME 21', line=dict(color='red')))

sinais_compra = df[df['Sinal'] == 'COMPRA']
sinais_venda = df[df['Sinal'] == 'VENDA']
fig.add_trace(go.Scatter(x=sinais_compra.index, y=sinais_compra['Close'], mode='markers', name='Compra', marker=dict(color='lime', size=10, symbol='triangle-up')))
fig.add_trace(go.Scatter(x=sinais_venda.index, y=sinais_venda['Close'], mode='markers', name='Venda', marker=dict(color='orange', size=10, symbol='triangle-down')))

fig.update_layout(title=f"{ativo} - Estratégia Técnica", xaxis_title="Data", yaxis_title="Preço (R$)", height=600)
st.plotly_chart(fig, use_container_width=True)

# Exportar Excel
st.download_button("📥 Baixar histórico de sinais (Excel)", data=df.to_csv().encode('utf-8'), file_name=f'{ativo}_sinais.csv', mime='text/csv')
