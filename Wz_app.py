import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
from zoneinfo import ZoneInfo
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="WZ Leaderboard", page_icon="🎮")

# ================= CSS =================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Teko:wght@400;600;700&display=swap" rel="stylesheet">
<style>
.stApp { background-color:#181818; color:#F5F5F5; }

h1{
  font-family:'Teko',sans-serif !important;
  font-weight:700 !important;
  font-size:74px !important;
  letter-spacing:0.05em !important;
  text-transform:uppercase !important;
  color:#F5F5F5 !important;
  margin-bottom:0.1rem !important;
}
h2{
  font-family:'Teko',sans-serif !important;
  font-weight:600 !important;
  font-size:40px !important;
  margin-bottom:0.3rem !important;
}
.block-container p{ font-family:'Teko',sans-serif !important; }
.main .block-container{ padding-top:1.2rem; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
col1, col2 = st.columns([3, 2])

with col1:
    st.title("MANQUERÍA: LOS BLOQUEAOS")
    st.caption("WZ Squad Leaderboard")

with col2:
    img = Image.open("logo.jpeg")
    st.image(img, width=420)

# ================= GOOGLE SHEET =================
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1eIV375K_xsQ3KuuY5VjPv7ca3mvsV8gZXBN3wF1JgAg/export?format=csv&gid=0"
)

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

# ================= CONSTANTES / ESTILO =================
meses = [
    "enero","febrero","marzo","abril","mayo","junio",
    "julio","agosto","septiembre","octubre","noviembre","diciembre"
]

orden_manual = ["Jesuso", "Kripy", "Gaby", "Koko"]

WARZONE_BAR = "#4F6D7A"       # azul gris táctico
WARZONE_ACCENT = "#A1D6C4"    # verde-azulado HUD
WINE_BAR = "#6D1F2A"          # vino (mes)
ORANGE_BAR = "#e67e22"        # naranja (chiverómetro)

GRID_COLOR = "#2B2B2B"
WHITE = "#FFFFFF"

def warzone_transparent_config(chart: alt.Chart) -> alt.Chart:
    # Quita “rectángulo” del view y cualquier fondo de Vega/Vega-Lite
    return (
        chart
        .configure(background="transparent")
        .configure_view(strokeOpacity=0)
        .configure_axis(gridColor=GRID_COLOR)
    )

# ================= MANCO DEL DÍA =================
ultimo_dia = df["Fecha"].max()
fila_ultimo = df[df["Fecha"] == ultimo_dia].iloc[0]

dia_scores = (
    fila_ultimo[players]
    .rename_axis("Jugador")
    .reset_index(name="Chivas")
    .set_index("Jugador")
    .reindex(orden_manual)
    .fillna(0)
    .reset_index()
)

fecha_texto = f"{ultimo_dia.day} de {meses[ultimo_dia.month - 1]}"

max_dia = int(dia_scores["Chivas"].max())
padding_dia = max(1, int(max_dia * 0.10))
scale_dia = alt.Scale(domain=[0, max_dia + padding_dia], nice=True)

base_dia = alt.Chart(dia_scores)

bars_dia = base_dia.mark_bar(color=WARZONE_BAR, size=80).encode(
    x=alt.X("Jugador:N", sort=orden_manual, axis=None),
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
            gridColor=GRID_COLOR,
        ),
    ),
)

labels_nombre = base_dia.mark_text(
    dy=-26, font="Teko", fontSize=22,
    fontWeight="bold", color=WARZONE_ACCENT
).encode(
    x=alt.X("Jugador:N", sort=orden_manual),
    y="Chivas:Q",
    text="Jugador:N"
)

labels_num = base_dia.mark_text(
    dy=-6, font="Teko", fontSize=20,
    fontWeight="bold", color=WARZONE_ACCENT
).encode(
    x=alt.X("Jugador:N", sort=orden_manual),
    y="Chivas:Q",
    text="Chivas:Q"
)

chart_dia = (bars_dia + labels_nombre + labels_num).properties(
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

chart_dia = warzone_transparent_config(chart_dia)
st.altair_chart(chart_dia, width="stretch")

# ================= LÍDER DEL MES =================
tz = ZoneInfo("America/Puerto_Rico")
now = datetime.now(tz)

df_month = df[
    (df["Fecha"].dt.year == now.year) &
    (df["Fecha"].dt.month == now.month)
]

st.markdown("<hr style='border:1px solid #2b2b2b;'>", unsafe_allow_html=True)

st.subheader(f"LÍDER DEL MES ({meses[now.month-1].upper()} {now.year})")

if not df_month.empty:
    totales_mes = (
        df_month[players]
        .sum()
        .rename_axis("Jugador")
        .reset_index(name="Chivas_mes")
        .set_index("Jugador")
        .reindex(orden_manual)
        .fillna(0)
        .reset_index()
    )

    # líder del mes
    lider_row = totales_mes.sort_values("Chivas_mes", ascending=False).iloc[0]
    lider = lider_row["Jugador"]
    lider_val = int(lider_row["Chivas_mes"])

    st.markdown(
        f"""
        <div style="background:#202020;border:1px solid #2f2f2f;
        padding:14px 16px;border-radius:12px;margin-bottom:12px;">
        <span style="font-family:'Teko';font-size:30px;color:{WARZONE_ACCENT};">🤡 {lider}</span>
        <span style="font-family:'Teko';font-size:26px;color:#F5F5F5;"> — {lider_val}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ticks pares
    max_mes = int(totales_mes["Chivas_mes"].max())
    pad_mes = max(1, int(max_mes * 0.20))  # un poco más de aire
    x_max = max(2, int((max_mes + pad_mes + 1)//2*2))
    ticks_pares = list(range(0, x_max + 1, 2))

    base_mes = alt.Chart(totales_mes)

    bars_mes = base_mes.mark_bar(color=WINE_BAR).encode(
        x=alt.X(
            "Chivas_mes:Q",
            title="Chivas_mes",
            scale=alt.Scale(domain=[0, x_max]),
            axis=alt.Axis(
                values=ticks_pares,
                tickMinStep=2,
                labelFont="Teko",
                labelFontSize=16,
                labelColor=WHITE,
                titleFont="Teko",
                titleFontSize=20,
                titleColor=WHITE,
                tickColor=WHITE,
                domainColor=WHITE,
                gridColor=GRID_COLOR,
            ),
        ),
        y=alt.Y(
            "Jugador:N",
            sort=orden_manual,
            axis=alt.Axis(
                title="Jugador",
                labelFont="Teko",
                labelFontSize=18,
                labelColor=WHITE,
                titleFont="Teko",
                titleFontSize=20,
                titleColor=WHITE,
                tickColor=WHITE,
                domainColor=WHITE,
            ),
        ),
    )

    labels_mes = base_mes.mark_text(
        align="left",
        baseline="middle",
        dx=8,
        font="Teko",
        fontSize=20,
        fontWeight="bold",
        color=WARZONE_ACCENT,
    ).encode(
        x="Chivas_mes:Q",
        y=alt.Y("Jugador:N", sort=orden_manual),
        text="Chivas_mes:Q",
    )

    chart_mes = (bars_mes + labels_mes).properties(
        height=240,  # MÁS GRANDE para que no se vea aplastado
        background="transparent",
        title=alt.TitleParams(
            "TOTALES DEL MES",
            anchor="middle",
            font="Teko",
            fontSize=30,
            color=WHITE,
        ),
    )

    chart_mes = warzone_transparent_config(chart_mes)
    st.altair_chart(chart_mes, width="stretch")
else:
    st.info("No hay datos todavía para este mes.")

# ================= CHIVERÓMETRO =================
totales = (
    df[players]
    .sum()
    .rename_axis("Jugador")
    .reset_index(name="Chivas_totales")
    .set_index("Jugador")
    .reindex(orden_manual)
    .fillna(0)
    .reset_index()
)

max_total = int(totales["Chivas_totales"].max())
pad_total = max(2, int(max_total * 0.10))
x_max_total = max(5, int((max_total + pad_total + 4)//5*5))
ticks_5 = list(range(0, x_max_total + 1, 5))

base_total = alt.Chart(totales)

bars_total = base_total.mark_bar(color=ORANGE_BAR).encode(
    x=alt.X(
        "Chivas_totales:Q",
        title="Chivas_totales",
        scale=alt.Scale(domain=[0, x_max_total]),
        axis=alt.Axis(
            values=ticks_5,
            tickMinStep=5,
            labelFont="Teko",
            labelFontSize=16,
            labelColor=WHITE,
            titleFont="Teko",
            titleFontSize=20,
            titleColor=WHITE,
            tickColor=WHITE,
            domainColor=WHITE,
            gridColor=GRID_COLOR,
        ),
    ),
    y=alt.Y(
        "Jugador:N",
        sort=orden_manual,
        axis=alt.Axis(
            title="Jugador",
            labelFont="Teko",
            labelFontSize=18,
            labelColor=WHITE,
            titleFont="Teko",
            titleFontSize=20,
            titleColor=WHITE,
            tickColor=WHITE,
            domainColor=WHITE,
        ),
    ),
)

labels_total = base_total.mark_text(
    align="left",
    baseline="middle",
    dx=8,
    font="Teko",
    fontSize=20,
    fontWeight="bold",
    color=WHITE,
).encode(
    x="Chivas_totales:Q",
    y=alt.Y("Jugador:N", sort=orden_manual),
    text="Chivas_totales:Q",
)

chart_total = (bars_total + labels_total).properties(
    height=280,  # MÁS GRANDE para que no se vea pequeño
    background="transparent",
    title=alt.TitleParams(
        "CHIVERÓMETRO",
        anchor="middle",
        font="Teko",
        fontSize=34,
        color=WHITE,
    ),
)

chart_total = warzone_transparent_config(chart_total)
st.altair_chart(chart_total, width="stretch")