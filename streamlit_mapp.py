import streamlit as st
import pandas as pd
import folium
from branca.colormap import linear

import plotly.express as px

from plotly.subplots import make_subplots

st.set_page_config(layout='wide', page_title="Painel dos Preços")
st.title("Painel dos Preços")
st.write("Data de coleta: ", df['data'].max())
select_planilha = st.selectbox("Lista de Planilhas", ['precos_carrefour_kani_20250516_tratado.xlsx', 'precos_carrefour_empanado_20250516_tratado.xlsx'])
if not select_planilha:
    st.error("Por favor, escolha pelo menos uma planilha.")
else:
    df = pd.read_excel(select_planilha)
             
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
        
        # Se o seletor estiver marcado, exibir o preço ao lado do círculo
        if exibir_preco:
            preco_popup = f"<b>R${row['preco']:.2f}</b>"
            folium.Marker(location=[row['lat'] - 0.01, row['long']],  # Ajuste na posição vertical
                        icon=folium.DivIcon(html=f"<div style='font-size: 12pt;'>{preco_popup}</div>")).add_to(mapa)  # Ajuste no tamanho da fonte
        
        circle.add_to(mapa)

    # Adicionar a legenda da escala de cores
    colormap.caption = 'Preço'
    colormap.add_to(mapa)

    # Exibir o mapa no Streamlit
    mapa.save("mapa.html")
    st.components.v1.html(open("mapa.html", "r").read(), height=600)


