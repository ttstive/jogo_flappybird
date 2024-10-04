import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")  # Configurando a largura total da página

st.title("Análise de Performance da Rede Neural")

# Adicionando seções interativas
feedback = st.selectbox("Gostaram do nosso jogo?", options=["Sim", "Demais", "Sim, queria aprender como fizeram"])

st.subheader("Flappy Bird com AI")

# Carregando dados
dados = pd.read_csv("dados_genomas.csv")
dados2 = pd.read_csv("dados_genomas2.csv")
dados3 = pd.read_csv("dados_genomas3.csv")
dados1 = pd.read_csv("dados_genomas1.csv")
dados5 = pd.read_csv("dados_genomas4.csv")
dados6 = pd.read_csv("dados_genomas5.csv")

# Adicionando uma coluna para identificar o tamanho da população
dados['Pop_Size'] = '3'
dados2['Pop_Size'] = '20'
dados3['Pop_Size'] = '50'
dados1['Pop_Size'] = '10'
dados5['Pop_Size'] = '30'
dados6['Pop_Size'] = '40'

# Combinando todos os dados em DataFrames únicos
dados_combined = pd.concat([dados, dados2, dados3])
dados_combined2 = pd.concat([dados1, dados5, dados6])

# Definindo a melhor geração com base no Fitness
melhor_geracao = dados_combined[dados_combined['Fitness'] == dados_combined['Fitness'].max()]['Geracao'].values[0]
melhor_geracao2 = dados_combined2[dados_combined2['Fitness'] == dados_combined2['Fitness'].max()]['Geracao'].values[0]

# Criando gráficos de dispersão
fig = px.scatter(dados_combined, x='Geracao', y='Fitness', color='Pop_Size',
                 title="Dispersão de Fitness por Tamanho da População",
                 hover_data=['Pop_Size'],
                 labels={'Geracao': 'Gerações', 'Fitness': 'Fitness'},
                 color_discrete_map={'3': 'blue', '20': 'green', '50': 'red'})

fig.add_trace(go.Scatter(x=[melhor_geracao], y=[dados_combined['Fitness'].max()],
                         mode='markers', marker=dict(color='gold', size=15),
                         name='Melhor Geração'))

fig.update_layout(
    xaxis_title="Gerações",
    yaxis_title="Fitness",
    width=1200,
    height=800
)

fig2 = px.scatter(dados_combined2, x='Geracao', y='Fitness', color='Pop_Size',
                  title="Dispersão de Fitness por Tamanho da População",
                  hover_data=['Pop_Size'],
                  labels={'Geracao': 'Gerações', 'Fitness': 'Fitness'},
                  color_discrete_map={'10': 'cyan', '30': 'purple', '40': 'orange'})

fig2.add_trace(go.Scatter(x=[melhor_geracao2], y=[dados_combined2['Fitness'].max()],
                          mode='markers', marker=dict(color='gold', size=15),
                          name='Melhor Geração'))

fig2.update_layout(
    xaxis_title="Gerações",
    yaxis_title="Fitness",
    width=1200,
    height=800
)

# Dividindo os gráficos lado a lado
col1, col2 = st.columns(2)

with col1:
    st.subheader("Dispersão de Fitness por Tamanho da População - Teste 1")
    st.plotly_chart(fig)
    st.write("Podemos ver claramente a diferença de Aprendizagem entre as gerações nos dois testes")

with col2:
    st.subheader("Dispersão de Fitness por Tamanho da População - Teste 2")
    st.plotly_chart(fig2)
    st.write("Com um simples grafico de dispersão segmentada, podemos identificar a melhot geração em cada teste, e elas não são simétricas")

# Adicionando o indicador
melhor_fitness1 = dados_combined['Fitness'].max()
melhor_fitness2 = dados_combined2['Fitness'].max()
diferenca_fitness = melhor_fitness1 - melhor_fitness2

st.header("Comparação de Melhores Gerações")
st.metric(label="Diferença no Melhor Fitness", value=diferenca_fitness)

# Adicionando uma seção para feedback
st.subheader("Feedback")
st.write("Queremos saber o que vocês acharam! Deixem seus comentários abaixo:")
feedback_text = st.text_area("Deixe seu feedback aqui")
submit_button = st.button("Enviar")

if submit_button:
    st.write("Obrigado pelo seu feedback!")
