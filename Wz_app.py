import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# ================= CONFIG PÁGINA =================
st.set_page_config(page_title="WZ Leaderboard", page_icon="🎮")

# ===== TEMA OSCURO + FUENTE TEKO PARA ESTILO WARZONE =====
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Teko:wght@400;600;700&display=swap" rel="stylesheet">

<style>
/* Fondo general */
.stApp {
    background-color: #181818;
    color: #F5F5F5;
}

/* Título principal estilo Warzone */
h1 {
    font-family: 'Teko', sans-serif !important;
    font-weight: 700 !important;
    font-size: 74px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #F5F5F5 !important;
    margin-bottom: 0.1rem !important;
}

/* Subtítulos (por si usamos st.subheader) */
h2 {
    font-family: 'Teko', sans-serif !important;
    font-weight: 600 !important;
    font-size: 40px !important;
    margin-bottom: 0.3rem !important;
}

/* Caption bajo el título */
.block-container p {
    font-family: 'Teko', sans-serif !important;
}

/* Quitar padding superior extra si estorba */
.main .block-container {
    padding-top: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
col1, col2 = st.columns([3, 2])

with col1:
    # Título sencillo en una sola línea como al principio
    st.title("MANQUERÍA: LOS BLOQUEAOS")
    st.caption("WZ Squad Leaderboard")

with col2:
    img = Image.open("logo.jpeg")
    st.write("")  # pequeño espacio
    # Controla el tamaño visual de la imagen con width
    st.image(img, width=420)

# ============== URL DEL GOOGLE SHEET (CSV) ==========
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1eIV375K_xsQ3KuuY5VjPv7ca3mvsV8gZXBN3wF1JgAg/export?format=csv&gid=0"
)

# ============== CARGA DE DATOS ======================
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_CSV_URL)
    df.columns = [c.strip() for c in df.columns]
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    player_cols = df.columns[1:]
    for col in player_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df, list(player_cols)

df, players = load_data()

if df.empty:
    st.warning("No hay datos todavía en el Sheet.")
    st.stop()

# ================== ÚLTIMO DÍA JUGADO ==================
ultimo_dia = df["Fecha"].max()
fila_ultimo = df[df["Fecha"] == ultimo_dia].iloc[0]

dia_scores = (
    fila_ultimo[players]
    .rename_axis("Jugador")
    .reset_index(name="Chivas")
    .sort_values("Chivas", ascending=False)
)

# Fecha en español
meses = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]
dia = ultimo_dia.day
mes = meses[ultimo_dia.month - 1]
fecha_texto = f"{dia} de {mes}"

# ========= MANCO DEL DÍA: PODIO CON BARRAS (WARZONE THEME) =========

max_dia = int(dia_scores["Chivas"].max())
padding_dia = max(1, int(max_dia * 0.10))
scale_dia = alt.Scale(domain=[0, max_dia + padding_dia], nice=True)

# Paleta tipo Warzone
WARZONE_BAR = "#4F6D7A"      # azul gris táctico
WARZONE_ACCENT = "#A1D6C4"   # verde-azulado HUD

base_dia = alt.Chart(dia_scores)

# Barras gruesas, eje Y con chivas, eje X sin labels
bars_dia = (
    base_dia.mark_bar(color=WARZONE_BAR, size=80)
    .encode(
        x=alt.X(
            "Jugador:N",
            sort="-y",
            axis=None,                 # sin ticks ni labels en X
        ),
        y=alt.Y(
            "Chivas:Q",
            scale=scale_dia,
            axis=alt.Axis(
                title="Chivas del día",
                labelFont="Teko",
                labelFontSize=18,
                labelColor=WARZONE_ACCENT,
                titleFont="Teko",
                titleFontSize=24,
                titleColor=WARZONE_ACCENT,
                tickColor=WARZONE_ACCENT,
                domainColor=WARZONE_ACCENT,
                tickMinStep=1,
            ),
        ),
    )
)

# NOMBRE del jugador encima de la barra
name_labels = (
    base_dia.mark_text(
        dy=-26,
        font="Teko",
        fontSize=22,
        fontWeight="bold",
        color=WARZONE_ACCENT,
    )
    .encode(
        x=alt.X("Jugador:N", sort="-y"),
        y="Chivas:Q",
        text="Jugador:N",
    )
)

# NÚMERO de chivas justo debajo del nombre
chivas_labels = (
    base_dia.mark_text(
        dy=-6,
        font="Teko",
        fontSize=20,
        fontWeight="bold",
        color=WARZONE_ACCENT,
    )
    .encode(
        x=alt.X("Jugador:N", sort="-y"),
        y="Chivas:Q",
        text="Chivas:Q",
    )
)

chart_dia = (bars_dia + name_labels + chivas_labels).properties(
    height=320,
    background="transparent",
    title=alt.TitleParams(
        f"Manco del día 🏆 ({fecha_texto})",
        anchor="middle",
        font="Teko",
        fontSize=34,
        color=WARZONE_ACCENT,
    ),
)

st.altair_chart(chart_dia, use_container_width=True)

# ================== TOTALES (CHIVERÓMETRO) =================
totales = (
    df[players]
    .sum()
    .rename_axis("Jugador")
    .reset_index(name="Chivas_totales")
)

orden_manual = ["Jesuso", "Kripy", "Gaby", "Koko"]

totales_plot = (
    totales.set_index("Jugador")
    .reindex(orden_manual)
    .reset_index()
)

max_chivas = int(totales_plot["Chivas_totales"].max())
padding = max(1, int(max_chivas * 0.10))
x_scale = alt.Scale(domain=[0, max_chivas + padding], nice=True)

base = alt.Chart(totales_plot)

# Barras naranjas
bars = (
    base.mark_bar(color="#e67e22")
    .encode(
        x=alt.X(
            "Chivas_totales:Q",
            title="Chivas",
            scale=x_scale,
            axis=alt.Axis(
                tickMinStep=1,
                labelFont="Teko",
                labelFontSize=18,
                labelColor="#FFFFFF",
                titleFont="Teko",
                titleFontSize=22,
                titleColor="#FFFFFF",
                tickColor="#FFFFFF",
                domainColor="#FFFFFF",
            ),
        ),
        y=alt.Y(
            "Jugador:N",
            sort=orden_manual,
            axis=alt.Axis(
                title=None,
                labelFont="Teko",
                labelFontSize=22,
                labelColor="#FFFFFF",
                tickColor="#FFFFFF",
                domainColor="#FFFFFF",
            ),
        ),
    )
)

labels = (
    base.mark_text(
        align="left",
        baseline="middle",
        dx=6,
        font="Teko",
        fontSize=22,
        fontWeight="bold",
        color="#FFFFFF",
    )
    .encode(
        x="Chivas_totales:Q",
        y=alt.Y("Jugador:N", sort=orden_manual),
        text="Chivas_totales:Q",
    )
)

chart = (bars + labels).properties(
    height=270,
    background="transparent",
    title=alt.TitleParams(
        "CHIVERÓMETRO 📉",
        anchor="middle",
        font="Teko",
        fontSize=34,
        color="#FFFFFF",
    ),
)

st.altair_chart(chart, use_container_width=True)