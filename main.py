# app.py
# MBTI별 최적 공부법 추천 웹앱 (for Streamlit Cloud)
# 루루를 위해: 직관적 UI, 이모지 듬뿍, 재미 요소 포함!

import streamlit as st
from datetime import datetime
import random
import textwrap

st.set_page_config(
    page_title="MBTI 공부법 처방전",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="ex
