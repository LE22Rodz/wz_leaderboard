import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# ================= CONFIG PÁGINA =================
st.set_page_config(page_title="WZ Leaderboard", page_icon="🎮", layout="wide")

# ===== TEMA OSCURO + FUENTE TEKO + RESPONSIVE PARA CELULAR =====
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Teko:wght@400;600;700&display=swap" rel="stylesheet">

<style>
/* Fondo general */
.stApp {
    background-color: #181818;
    color: #F5F5F5;
}

/* Reduce padding lateral en pantallas pequeñas */
.main .block-container {
    padding-top: 1.2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Título principal (desktop) */
h1 {
    font-family: 'Teko', sans-serif !important;
    font-weight: 700 !important;
    font-size: 74px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #F5F5F5 !important;
    margin-bottom: 0.1rem !important;
    line-height: 0.95 !important;
}

/* Subtítulos */
h2, h3 {
    font-family: 'Teko', sans-serif !important;
}

/* Caption */
.block-container p {
    font-family: 'Teko', sans-serif !important;
}

/* --- RESPONSIVE (CELULAR) --- */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1.2rem;
        padding-right: 1.2rem;
        padding-top: 0.8rem;
    }

    h1 {
        font-size: 54px !important;
        line-height: 0.95 !important;
        letter-spacing: 0.03em !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
# En mobile Streamlit apila columnas automáticamente; en desktop se ven lado a lado.
col1, col2 = st.columns([3, 2])

with col1:
    st.title("MANQUERÍA: LOS BLOQUEAOS")
    st.caption("WZ Squad Leaderboard")

with col2:
    img = Image.open("logo.jpeg")
    # width grande en desktop; en mobile el CSS del título ya evita el desastre
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

# Orden fijo que tú quieres (izq->der)
orden_manual = ["Jesuso", "Kripy", "Gaby", "Koko"]
players_ordered = [p for p in orden_manual if p in players]

dia_scores = (
    fila_ultimo[players_ordered]
    .rename_axis("Jugador")
    .reset_index(name="Chivas")
)

# Fecha en español
meses = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]
fecha_texto = f"{ultimo_dia.day} de {meses[ultimo_dia.month - 1]}"

# ========= ESTILO WARZONE (colores) =========
WARZONE_BAR = "#4F6D7A"       # azul gris táctico
WARZONE_ACCENT = "#A1D6C4"    # verde HUD
MONTH_WINE = "#6B1F2B"        # vino
CHIVO_ORANGE = "#e67e22"      # naranja chiverómetro

# ================== MANCO DEL DÍA (vertical) ==================
max_dia = int(dia_scores["Chivas"].max())
padding_dia = max(1, int(max_dia * 0.10))
scale_dia = alt.Scale(domain=[0, max_dia + padding_dia], nice=True)

base_dia = alt.Chart(dia_scores)

bars_dia = (
    base_dia.mark_bar(color=WARZONE_BAR, size=70)
    .encode(
        x=alt.X("Jugador:N", sort=players_ordered, axis=None),
        y=alt.Y(
            "Chivas:Q",
            scale=scale_dia,
            axis=alt.Axis(
                title="Chivas del día",
                labelFont="Teko",
                labelFontSize=16,
                labelColor=WARZONE_ACCENT,
                titleFont="Teko",
                titleFontSize=22,
                titleColor=WARZONE_ACCENT,
                tickColor=WARZONE_ACCENT,
                domainColor=WARZONE_ACCENT,
                gridColor="#303030",
                tickMinStep=1,
            ),
        ),
    )
)

name_labels = (
    base_dia.mark_text(dy=-22, font="Teko", fontSize=20, fontWeight="bold", color=WARZONE_ACCENT)
    .encode(
        x=alt.X("Jugador:N", sort=players_ordered),
        y="Chivas:Q",
        text="Jugador:N",
    )
)

chivas_labels = (
    base_dia.mark_text(dy=-4, font="Teko", fontSize=18, fontWeight="bold", color=WARZONE_ACCENT)
    .encode(
        x=alt.X("Jugador:N", sort=players_ordered),
        y="Chivas:Q",
        text="Chivas:Q",
    )
)

chart_dia = (bars_dia + name_labels + chivas_labels).properties(
    height=300,
    background="transparent",
    title=alt.TitleParams(
        f"Manco del día 🏆 ({fecha_texto})",
        anchor="middle",
        font="Teko",
        fontSize=34,
        color=WARZONE_ACCENT,
    ),
).configure_view(strokeOpacity=0)

st.altair_chart(chart_dia, width="stretch")

# ================== LÍDER DEL MES ACTUAL ==================
mes_actual = ultimo_dia.month
anio_actual = ultimo_dia.year
nombre_mes = meses[mes_actual - 1].upper()

df_mes = df[(df["Fecha"].dt.year == anio_actual) & (df["Fecha"].dt.month == mes_actual)]
tot_mes = (
    df_mes[players]
    .sum()
    .rename_axis("Jugador")
    .reset_index(name="Chivas_mes")
)
tot_mes_plot = (
    tot_mes.set_index("Jugador")
    .reindex(orden_manual)
    .reset_index()
    .fillna(0)
)
tot_mes_plot["Chivas_mes"] = tot_mes_plot["Chivas_mes"].astype(int)

max_mes = int(tot_mes_plot["Chivas_mes"].max())
padding_mes = max(1, int(max_mes * 0.10)) if max_mes > 0 else 1
x_scale_mes = alt.Scale(domain=[0, max_mes + padding_mes], nice=True)

# ticks pares (0,2,4,...) para esta gráfica
max_tick_mes = (max_mes + padding_mes)
tick_vals_mes = list(range(0, max_tick_mes + 2, 2))  # pares

lider_val = int(tot_mes_plot["Chivas_mes"].max())
leaders = tot_mes_plot[tot_mes_plot["Chivas_mes"] == lider_val]["Jugador"].tolist()
leaders_text = ", ".join(leaders) if leaders else "—"

st.subheader(f"LÍDER DEL MES ({nombre_mes} {anio_actual})")
st.markdown(
    f"""
    <div style="background:#222; border:1px solid #333; padding:18px; border-radius:14px;
                font-family:'Teko', sans-serif; font-size:28px; color:#F5F5F5;">
        🤡 <span style="color:{WARZONE_ACCENT};">{leaders_text}</span> — {lider_val}
    </div>
    """,
    unsafe_allow_html=True,
)

base_mes = alt.Chart(tot_mes_plot)

bars_mes = (
    base_mes.mark_bar(color=MONTH_WINE)
    .encode(
        x=alt.X(
            "Chivas_mes:Q",
            title="Chivas_mes",
            scale=x_scale_mes,
            axis=alt.Axis(
                values=tick_vals_mes,
                labelFont="Teko",
                labelFontSize=16,
                labelColor="#FFFFFF",
                titleFont="Teko",
                titleFontSize=20,
                titleColor="#FFFFFF",
                tickColor="#FFFFFF",
                domainColor="#FFFFFF",
                gridColor="#303030",
            ),
        ),
        y=alt.Y(
            "Jugador:N",
            sort=orden_manual,
            axis=alt.Axis(
                title="Jugador",
                labelFont="Teko",
                labelFontSize=18,
                labelColor="#FFFFFF",
                titleFont="Teko",
                titleFontSize=20,
                titleColor="#FFFFFF",
                tickColor="#FFFFFF",
                domainColor="#FFFFFF",
            ),
        ),
    )
)

labels_mes = (
    base_mes.mark_text(
        align="left", baseline="middle", dx=6,
        font="Teko", fontSize=18, fontWeight="bold", color=WARZONE_ACCENT
    )
    .encode(
        x="Chivas_mes:Q",
        y=alt.Y("Jugador:N", sort=orden_manual),
        text="Chivas_mes:Q",
    )
)

chart_mes = (bars_mes + labels_mes).properties(
    height=180,
    background="transparent",
    title=alt.TitleParams(
        "TOTALES DEL MES",
        anchor="middle",
        font="Teko",
        fontSize=30,
        color="#FFFFFF",
    ),
).configure_view(strokeOpacity=0)

st.altair_chart(chart_mes, width="stretch")

# ================== CHIVERÓMETRO (totales históricos) ==================
totales = (
    df[players]
    .sum()
    .rename_axis("Jugador")
    .reset_index(name="Chivas_totales")
)
totales_plot = (
    totales.set_index("Jugador")
    .reindex(orden_manual)
    .reset_index()
    .fillna(0)
)
totales_plot["Chivas_totales"] = totales_plot["Chivas_totales"].astype(int)

max_chivas = int(totales_plot["Chivas_totales"].max())
padding = max(1, int(max_chivas * 0.10)) if max_chivas > 0 else 1
x_scale = alt.Scale(domain=[0, max_chivas + padding], nice=True)

# ticks 5 en 5 para el chiverómetro
max_tick = (max_chivas + padding)
tick_step = 5
tick_vals = list(range(0, max_tick + tick_step, tick_step))

base = alt.Chart(totales_plot)

bars = (
    base.mark_bar(color=CHIVO_ORANGE)
    .encode(
        x=alt.X(
            "Chivas_totales:Q",
            title="Chivas_totales",
            scale=x_scale,
            axis=alt.Axis(
                values=tick_vals,
                labelFont="Teko",
                labelFontSize=16,
                labelColor="#FFFFFF",
                titleFont="Teko",
                titleFontSize=20,
                titleColor="#FFFFFF",
                tickColor="#FFFFFF",
                domainColor="#FFFFFF",
                gridColor="#303030",
            ),
        ),
        y=alt.Y(
            "Jugador:N",
            sort=orden_manual,
            axis=alt.Axis(
                title="Jugador",
                labelFont="Teko",
                labelFontSize=18,
                labelColor="#FFFFFF",
                titleFont="Teko",
                titleFontSize=20,
                titleColor="#FFFFFF",
                tickColor="#FFFFFF",
                domainColor="#FFFFFF",
            ),
        ),
    )
)

labels = (
    base.mark_text(
        align="left", baseline="middle", dx=6,
        font="Teko", fontSize=18, fontWeight="bold", color="#FFFFFF"
    )
    .encode(
        x="Chivas_totales:Q",
        y=alt.Y("Jugador:N", sort=orden_manual),
        text="Chivas_totales:Q",
    )
)

chart = (bars + labels).properties(
    height=220,
    background="transparent",
    title=alt.TitleParams(
        "CHIVERÓMETRO",
        anchor="middle",
        font="Teko",
        fontSize=34,
        color="#FFFFFF",
    ),
).configure_view(strokeOpacity=0)

st.altair_chart(chart, width="stretch")