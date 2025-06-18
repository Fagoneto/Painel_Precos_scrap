import streamlit as st
import pandas as pd
import folium
from branca.colormap import linear

import plotly.express as px

from plotly.subplots import make_subplots

st.set_page_config(layout='wide', page_title="Painel dos Preços")
st.title("Painel dos Preços")

# df = st.selectbox("Lista de Planilhas", ['precos_carrefour_kani_20250516_tratado.xlsx', 'precos_carrefour_empanado_20250516_tratado.xlsx'])

st.write("Escolha uma planilha:")

# Opções simplificadas
select_planilha = st.selectbox("Lista de Planilhas", ['cerveja', 'cachaca'])

# Carregamento condicional
if select_planilha == 'cerveja':
    df = pd.read_csv('precos_carrefour_cerveja_20250617.csv')
else:
    df = pd.read_csv('precos_carrefour_cachaca_20250617.csv')

# if not df:
#     st.error("Por favor, escolha pelo menos uma planilha.")
# else:
#     df = pd.read_excel('precos_carrefour_kani_20250516_tratado.xlsx)



produto_1 = st.selectbox(
        "Escolha quantos produtos quiser", (list(df['produto'].unique())))#, [df['produto'][0]])#, [## colocar aqui os primeiros itens da lista]
if not produto_1:
    st.error("Por favor, escolha pelo menos um produto.")
else:
    df_1 = df[df['produto']==produto_1]

    # Criar um mapa Folium centrado no Brasil
    mapa = folium.Map(location=[-15.793889, -47.882778], zoom_start=4)

    # Definir a escala de cores para os preços
    preco_minimo = df_1['preco'].min()
    preco_maximo = df_1['preco'].max()
    colormap = linear.YlOrRd_09.scale(preco_minimo, preco_maximo)

    # Adicionar círculos para representar os preços das lojas
    for _, row in df_1.iterrows():
        circle = folium.CircleMarker(location=[row['lat'], row['long']], radius=10, color='black', fill=True, 
                                    fill_opacity=0.7, fill_color=colormap(row['preco']))
        
        # Adicionar popup com o nome da loja e preço ao clicar no círculo
        popup_html = f"<b>{row['loja']}</b><br>Preço: <b>R${row['preco']:.2f}</b>"
        popup = folium.Popup(popup_html, parse_html=False)
        circle.add_child(popup)
        
        # # Se o seletor estiver marcado, exibir o preço ao lado do círculo
        # if exibir_preco:
        #     preco_popup = f"<b>R${row['preco']:.2f}</b>"
        #     folium.Marker(location=[row['lat'] - 0.01, row['long']],  # Ajuste na posição vertical
        #                 icon=folium.DivIcon(html=f"<div style='font-size: 12pt;'>{preco_popup}</div>")).add_to(mapa)  # Ajuste no tamanho da fonte
        
        circle.add_to(mapa)

    # Adicionar a legenda da escala de cores
    colormap.caption = 'Preço'
    colormap.add_to(mapa)

    # Exibir o mapa no Streamlit
    mapa.save("mapa.html")
    st.components.v1.html(open("mapa.html", "r").read(), height=600)



st.markdown(" Escolha uma cidade e uma loja para ver os preços dos produtos disponíveis:")

# Seleção por cidade
select_cidade = st.selectbox("Lista de Cidades", df.cidade.unique().tolist())
df_cidade = df[df['cidade'] == select_cidade]

# Seleção por loja
select_loja = st.selectbox("Lista de Lojas", df_cidade.loja.unique().tolist())
df_loja = df_cidade[df_cidade['loja'] == select_loja]

# Ordenar por preço crescente (opcional)
df_loja_sorted = df_loja[['produto', 'preco']].sort_values(by='preco', ascending=False)

# Exibir em formato de tabela interativa
st.dataframe(df_loja_sorted, use_container_width=True)
