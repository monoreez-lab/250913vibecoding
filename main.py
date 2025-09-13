import streamlit as st
import pandas as pd
import altair as alt
import os

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="MBTI Top10 by Country", layout="wide")
st.title("MBTI 유형별 비율이 가장 높은 국가 TOP10")
st.write("CSV 데이터를 기본적으로 같은 폴더에서 불러오며, 없을 경우 업로드한 파일을 사용합니다.")

# -----------------------------
# File Handling: 기본 CSV 로드 + 업로더
# -----------------------------
def try_load_default(path="countriesMBTI_16types.csv"):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return None

uploaded = st.file_uploader("CSV 파일 업로드 (예: countriesMBTI_16types.csv)", type=["csv"]) 

def get_dataframe():
    default_df = try_load_default()
    if default_df is not None:
        st.info("기본 CSV 파일을 불러왔습니다.")
        return default_df
    elif uploaded is not None:
        st.info("업로드된 CSV 파일을 사용합니다.")
        return pd.read_csv(uploaded)
    else:
        st.warning("CSV 파일을 불러올 수 없습니다. 같은 폴더에 'countriesMBTI_16types.csv'를 두거나 업로드 해주세요.")
        st.stop()

# Altair 행 제한 해제
alt.data_transformers.disable_max_rows()

# -----------------------------
# Helper: 데이터 로딩 & 검증
# -----------------------------
MBTI_ORDER = [
    "INFJ", "ISFJ", "INTP", "ISFP", "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP", "ESTP", "ISTJ", "ENFJ", "ESFJ",
]

def load_and_validate(df) -> (pd.DataFrame, list):
    # Country 존재 확인
    if "Country" not in df.columns:
        st.error("CSV에 'Country' 컬럼이 없습니다. 첫 번째 열에 국가명이 들어간 'Country' 컬럼을 포함해 주세요.")
        st.stop()

    mbti_cols = [c for c in MBTI_ORDER if c in df.columns]
    if len(mbti_cols) == 0:
        st.error("MBTI 컬럼이 없습니다. (예: INFJ, ENFP 등)")
        st.stop()

    for c in mbti_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    bad_cols = [c for c in mbti_cols if df[c].notna().sum() == 0]
    if bad_cols:
        st.error(f"수치형으로 변환할 수 없는 컬럼이 있습니다: {', '.join(bad_cols)}")
        st.stop()

    for c in mbti_cols:
        series = df[c].dropna()
        if (series > 1).mean() > 0.5:
            df[c] = df[c] / 100.0

    return df, mbti_cols

# -----------------------------
# Main Logic
# -----------------------------
df = get_dataframe()
df, mbti_cols = load_and_validate(df)

st.subheader("데이터 미리보기")
st.dataframe(df.head(10))

# Long format 변환
long_df = df.melt(id_vars="Country", value_vars=mbti_cols, var_name="MBTI", value_name="Proportion")

# 상위 10개 추출 (MBTI별)
top10 = (
    long_df.sort_values(["MBTI", "Proportion"], ascending=[True, False])
           .groupby("MBTI", as_index=False)
           .head(10)
           .copy()
)

# 순위
top10["Rank"] = top10.groupby("MBTI")["Proportion"].rank(method="first", ascending=False).astype(int)

# 선택 위젯
st.subheader("MBTI 유형 선택")
selected_mbti = st.selectbox("유형", mbti_cols, index=0)

sel_df = top10[top10["MBTI"] == selected_mbti].sort_values("Proportion", ascending=False)

# 다운로드 버튼
csv_buf = sel_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"{selected_mbti} TOP10 데이터 다운로드 (CSV)",
    data=csv_buf,
    file_name=f"{selected_mbti}_top10.csv",
    mime="text/csv",
)

# Altair Bar Chart
st.subheader("그래프: 선택된 MBTI 유형의 국가 TOP10")
chart = (
    alt.Chart(sel_df)
    .mark_bar()
    .encode(
        x=alt.X("Proportion:Q", title="비율", axis=alt.Axis(format="%")),
        y=alt.Y("Country:N", sort="-x", title="국가"),
        tooltip=["Country:N", alt.Tooltip("Proportion:Q", format=".2%"), "Rank:O"],
        color=alt.value("#4C78A8"),
    )
    .properties(height=400)
)
text = chart.mark_text(align="left", dx=3).encode(
    text=alt.Text("Proportion:Q", format=".1%")
)
st.altair_chart(chart + text, use_container_width=True)

# 전체 개요
st.subheader("전체 개요: 모든 MBTI 유형의 TOP10 (필터 가능)")
selection = alt.selection_point(fields=["MBTI"], bind=alt.binding_select(options=mbti_cols, name="MBTI 유형 "))
overview = (
    alt.Chart(top10)
    .transform_filter(selection)
    .mark_bar()
    .encode(
        y=alt.Y("Country:N", sort="-x", title="국가"),
        x=alt.X("Proportion:Q", title="비율", axis=alt.Axis(format="%")),
        row=alt.Row("MBTI:N", sort=mbti_cols),
        tooltip=["MBTI:N", "Country:N", alt.Tooltip("Proportion:Q", format=".2%"), "Rank:O"],
    )
    .properties(height=150)
    .resolve_scale(x="independent")
)
st.altair_chart(overview, use_container_width=True)

st.subheader("요약")
st.write("기본 CSV 파일이 같은 폴더에 있으면 자동으로 로드되며, 없을 경우 업로드한 CSV 파일을 사용합니다.")
