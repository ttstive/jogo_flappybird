import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configurando a largura total da página
st.set_page_config(layout="wide")

st.title("Análise de Performance da Rede Neural")

# Adicionando seções interativas
feedback = st.selectbox("Gostaram do nosso jogo?", options=["Sim", "Demais", "Sim, queria aprender como fizeram"])

st.subheader("Flappy Bird com AI")

# Função para carregar dados com cache
@st.cache_data
def carregar_dados():
    dados = pd.read_csv("dados_genomas.csv")
    dados2 = pd.read_csv("dados_genomas2.csv")
    dados3 = pd.read_csv("dados_genomas3.csv")
    dados1 = pd.read_csv("dados_genomas1.csv")
    dados5 = pd.read_csv("dados_genomas4.csv")
    dados6 = pd.read_csv("dados_genomas5.csv")
    dados7 = pd.read_csv("dados_genomas6.csv")
    dados8 = pd.read_csv("dados_genomas7.csv")
    dados9 = pd.read_csv("dados_genomas8.csv")
    return dados, dados2, dados3, dados1, dados5, dados6, dados7, dados8, dados9

# Carregando os dados
dados, dados2, dados3, dados1, dados5, dados6, dados7, dados8, dados9 = carregar_dados()

# Adicionando uma coluna para identificar o tamanho da população
dados['Pop_Size'] = '3'
dados2['Pop_Size'] = '20'
dados3['Pop_Size'] = '50'
dados1['Pop_Size'] = '10'
dados5['Pop_Size'] = '30'
dados6['Pop_Size'] = '40'
dados7['Pop_Size'] = '3'
dados8['Pop_Size'] = '20'
dados9['Pop_Size'] = '50'

# Concatenando DataFrames de maneira otimizada
dados_combined = pd.concat([dados, dados2, dados3], ignore_index=True)
dados_combined2 = pd.concat([dados1, dados5, dados6], ignore_index=True)
dados_combined3 = pd.concat([dados7, dados8, dados9], ignore_index=True)

# Definindo a melhor geração com base no Fitness
melhor_geracao = dados_combined[dados_combined['Fitness'] == dados_combined['Fitness'].max()]['Geracao'].values[0]
melhor_geracao2 = dados_combined2[dados_combined2['Fitness'] == dados_combined2['Fitness'].max()]['Geracao'].values[0]
melhor_geracao3 = dados_combined3[dados_combined3['Fitness'] == dados_combined3['Fitness'].max()]['Geracao'].values[0]

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

fig3 = px.scatter(dados_combined3, x='Geracao', y='Fitness', color='Pop_Size',
                  title="Dispersão de Fitness por Tamanho da População",
                  hover_data=['Pop_Size'],
                  labels={'Geracao': 'Gerações', 'Fitness': 'Fitness'},
                  color_discrete_map={'17': 'cyan', '25': 'purple', '60': 'orange'})

fig3.add_trace(go.Scatter(x=[melhor_geracao3], y=[dados_combined3['Fitness'].max()],
                          mode='markers', marker=dict(color='gold', size=15),
                          name='Melhor Geração'))

fig3.update_layout(
    xaxis_title="Gerações",
    yaxis_title="Fitness",
    width=1200,
    height=800
)

# Dividindo os gráficos lado a lado
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Dispersão de Fitness por Tamanho da População - Teste 1")
    st.plotly_chart(fig)
    st.write("Podemos ver claramente a diferença de Aprendizagem entre as gerações nos dois testes")

with col2:
    st.subheader("Dispersão de Fitness por Tamanho da População - Teste 2")
    st.plotly_chart(fig2)
    st.write("Com um simples gráfico de dispersão segmentada, podemos identificar a melhor geração em cada teste.")

with col3:
    st.subheader("Dispersão de Fitness por Tamanho da População - Teste 3")
    st.plotly_chart(fig3)
    st.write("###")

# Adicionando o indicador
melhor_fitness1 = dados_combined['Fitness'].max()
melhor_fitness2 = dados_combined2['Fitness'].max()
melhor_fitness3 = dados_combined3['Fitness'].max()
diferenca_fitness = melhor_fitness1 + melhor_fitness2 + melhor_fitness3 / 3 * 100


# Função para carregar feedbacks do CSV
@st.cache_data
def carregar_feedbacks():
    if os.path.exists("feedbacks.csv"):
        return pd.read_csv("feedbacks.csv")
    else:
        return pd.DataFrame(columns=["feedback"])

# Função para salvar feedbacks no CSV
def salvar_feedback(feedback):
    feedbacks = carregar_feedbacks()
    novo_feedback = pd.DataFrame({"feedback": [feedback]})
    feedbacks = pd.concat([feedbacks, novo_feedback], ignore_index=True)
    feedbacks.to_csv("feedbacks.csv", index=False)

# Seção de feedback
st.subheader("Feedback")
st.write("Queremos saber o que vocês acharam! Deixem seus comentários abaixo:")
feedback_text = st.text_area("Deixe seu feedback aqui")
submit_button = st.button("Enviar")

if submit_button:
    if feedback_text.strip():
        salvar_feedback(feedback_text)
        st.write("Obrigado pelo seu feedback!")
    else:
        st.write("Por favor, insira um feedback válido.")

# Mostrar feedbacks anteriores
feedbacks = carregar_feedbacks()
if not feedbacks.empty:
    st.subheader("Feedbacks anteriores")
    st.write(feedbacks)
