import streamlit as st
from jogo import PrognosticoGame

st.set_page_config(page_title="Jogo de Prognóstico", layout="centered")

st.title("🎴 Jogo de Prognóstico")
st.write("Simulação automática do jogo")

nomes_input = st.text_input(
    "Jogadores (separados por vírgula)",
    "Ana, Bruno, Carlos, Diana"
)

if st.button("▶️ Iniciar Jogo"):
    nomes = [n.strip() for n in nomes_input.split(",") if n.strip()]

    if len(nomes) < 2:
        st.error("Informe pelo menos 2 jogadores.")
    else:
        jogo = PrognosticoGame(nomes)
        jogo.jogar()

        st.subheader("🏆 Resultado Final")
        for j in jogo.jogadores:
            st.write(
                f"**{j.nome}** — "
                f"Pontos: {j.pontos} | "
                f"Vazas: {j.vazas} | "
                f"Prognóstico: {j.prognostico}"
            )
