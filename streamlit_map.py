import streamlit as st
import pandas as pd
import folium
from branca.colormap import linear

import plotly.express as px

from plotly.subplots import make_subplots

# st.set_page_config()
st.set_page_config(layout='wide', page_title="Painel dos Preços")
st.title("Painel dos Preços")

st.write("Escolha uma planilha:")

# Opções simplificadas
select_planilha = st.selectbox("Lista de Planilhas", ['bacalhau'])

# Carregamento condicional
if select_planilha == 'bacalhau':
    df = pd.read_csv('precos_carrefour_bacalhau_20250712_loc.csv')
else:
    df = pd.read_csv('precos_carrefour_bacalhau_20250712_loc.csv')


def limpar_coord(col):
    return (
        col.astype(str)
        .str.strip()              # remove espaços
        .str.replace(',', '.', regex=False)  # troca vírgula por ponto
        .apply(lambda x: x if x.replace('.', '', 1).replace('-', '', 1).isdigit() else None)
        .astype(float)
    )

df['lat'] = limpar_coord(df['lat'])
df['long'] = limpar_coord(df['long'])

df = df.dropna(subset=['lat', 'long'])


st.write("Data de coleta: ", df['data'].max())


col1, col2 = st.columns(2)

with col1:
    produto_1 = st.selectbox(
            "Escolha quantos produtos quiser", (list(df['produto'].unique())))#, [df['produto'][0]])#, [## colocar aqui os primeiros itens da lista]
    if not produto_1:
        st.error("Por favor, escolha pelo menos um produto.")
    else:
        df_1 = df[df['produto']==produto_1]

        # Criar um seletor para escolher se deseja exibir o preço ao lado do círculo
        exibir_preco = st.checkbox("Exibir preço ao lado do círculo")

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


with col2:
    produto_2 = st.selectbox(
            "Escolha produto seguinte:", (list(df['produto'].unique())))#, [df['produto'][0]])#, [## colocar aqui os primeiros itens da lista]
    if not produto_2:
        st.error("Por favor, escolha pelo menos um produto.")
    else:
        df_2 = df[df['produto']==produto_2]

         # Criar um seletor para escolher se deseja exibir o preço ao lado do círculo
        exibir_preco = st.checkbox("Exibir preço ao lado do círculo.")

        # Criar um mapa Folium centrado no Brasil
        mapa = folium.Map(location=[-15.793889, -47.882778], zoom_start=4)

        # Definir a escala de cores para os preços
        preco_minimo = df_2['preco'].min()
        preco_maximo = df_2['preco'].max()
        colormap = linear.YlOrRd_09.scale(preco_minimo, preco_maximo)

        # Adicionar círculos para representar os preços das lojas
        for _, row in df_2.iterrows():
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



        df_3 = df[df['produto'].isin([produto_1, produto_2])]
        # Mesclar os DataFrames com base no nome da loja
        #df = pd.merge(df_lojas[['lat', 'long', 'loja']], df_3, on='loja')

fig = px.scatter(df_3, x="cidade", y='preco', color='produto', title= "Registro Diário de Preços",  hover_data=df.columns.unique())
st.plotly_chart(fig, use_container_width = True,height=800)

fig2 = px.box(df_3, x="produto", y='preco', color='produto', title="Variação de Preços",  hover_data=df.columns.unique())
st.plotly_chart(fig2, use_container_width = True,height=400)

#down9 = to_excel(df)
#st.download_button(label="Clique aqui para baixar a Tabela de Preços!", file_name="tabela_precos_cities.xlsx", data = down9,  key=7)



# st.markdown(
#         """
#         Seleção por cidade

#         **👈 
#     """
#     )


# st.write("Selecione uma cidade: ")
# select_city = st.selectbox("Lista de Cidades", df['cidade/UF'].unique())
# if not select_city:
#     st.error("Por favor, escolha pelo menos uma cidade.")
# else:
#     precos_carrefour_city = df[df['cidade/UF'].isin([select_city])]
#     precos_carrefour_city = precos_carrefour_city.sort_values(by=['preco'], ascending=False).reset_index()
#     st.write("Tabela de Preços de: ",precos_carrefour_city[['produto', 'preco', 'desconto', 'loja']])

    
# #down10 = to_excel(precos_carrefour_city)
# #st.download_button(label="Clique aqui para baixar a Tabela de Preços!", file_name="tabela_precos.xlsx", data = down10,  key=15)


regioes = df['regiao'].unique()

# Iterar de 2 em 2 regiões
for i in range(0, len(regioes), 2):
    col1, col2 = st.columns(2)

    # Primeira coluna
    with col1:
        regiao = regioes[i]
        df_reg = df_3[df_3['regiao'] == regiao]
        fig = px.scatter(df_reg,
                         x='cidade',
                         y='preco',
                         color='produto',
                         title=f'Região {regiao}',
                         labels={'preco': 'Preço (R$)', 'cidade/UF': 'Cidade/UF'},
                         height=500)
        fig.update_layout(
            hovermode='closest',
            xaxis_title='Cidade/UF',
            yaxis_title='Preço (R$)',
            legend_title='Produto',
            margin=dict(l=20, r=20, b=80, t=80)
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # Segunda coluna, se existir
    if i + 1 < len(regioes):
        with col2:
            regiao = regioes[i + 1]
            df_reg = df_3[df_3['regiao'] == regiao]
            fig = px.scatter(df_reg,
                             x='cidade',
                             y='preco',
                             color='produto',
                             title=f'Região {regiao}',
                             labels={'preco': 'Preço (R$)', 'cidade/UF': 'Cidade/UF'},
                             height=500)
            fig.update_layout(
                hovermode='closest',
                xaxis_title='Cidade/UF',
                yaxis_title='Preço (R$)',
                legend_title='Produto',
                margin=dict(l=20, r=20, b=80, t=80)
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
