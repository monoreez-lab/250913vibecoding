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
    initial_sidebar_state="expanded",
)

# ---------- 스타일 & 애니메이션 ----------
CSS = """
<style>
/* 배경 그라데이션 */
.stApp {
  background: radial-gradient(1200px 800px at 10% 10%, #fff7e6 0%, #ffffff 40%) no-repeat,
              linear-gradient(135deg, #f9f7ff 0%, #ffffff 60%) no-repeat;
}
/* 카드 느낌 */
.block-container { padding-top: 2.2rem; }
.card {
  background: white;
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 16px;
  padding: 1.2rem 1.1rem;
  box-shadow: 0 6px 24px rgba(0,0,0,.06);
}
/* 반짝 애니메이션 */
@keyframes pop {
  0% { transform: scale(.98); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1.0); }
}
.pop { animation: pop .6s ease-out; }
/* 칩 */
.chip {
  display: inline-block;
  padding: .25rem .6rem;
  border-radius: 999px;
  background: #f3f4f6;
  margin-right: .35rem;
  margin-bottom: .35rem;
  font-size: .85rem;
}
.small { opacity: .8; font-size: .86rem; }
code { white-space: pre-wrap; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- 데이터 ----------
MBTI_DATA = {
    "INTJ": {
        "name": "INTJ · 전략가 🧭",
        "vibe": "구조화·장기 플랜·자기주도",
        "strengths": ["체계화", "장기전략", "집중력"],
        "pitfalls": ["과도한 완벽주의", "시작 지연(Procrastination)"],
        "strategies": [
            "📚 **토픽 트리**를 미리 설계 → 큰 주제 ▶ 중주제 ▶ 소주제로 쪼개기",
            "⏱ **타임박싱(25–50분)** + 끝시간 고정으로 완벽주의 제어",
            "🧩 ‘이해 맵(Concept Map)’으로 개념 간 연결 그리기",
            "🧪 **모의고사 → 오답저널**: 오류 유형 레이블링(개념/실수/시간관리)",
        ],
        "tools": ["Notion Database", "Anki Spaced Repetition", "Mermaid/Excalidraw", "Focus To-Do"],
        "buddies": "ENFP(아이디어 확장), ISTJ(디테일 검증)",
    },
    "INTP": {
        "name": "INTP · 사색가 🧪",
        "vibe": "원리파·추론·깊게 파기",
        "strengths": ["개념화", "문제해결", "유연한 사고"],
        "pitfalls": ["자료 수집만 하다 시작 늦춤", "마감 압박 취약"],
        "strategies": [
            "🎯 **질문 리스트(왜/어떻게/만약)**를 먼저 작성하고 학습 시작",
            "🧠 **파인만 기법**: 10살에게 설명하듯 요약 기록하기",
            "🔁 **Interleaving**: 서로 다른 과목/유형 번갈아 학습",
            "⛳ **마감 트리오**: 소마감(오늘)·중간(주말)·최종(시험 전)",
        ],
        "tools": ["Obsidian Zettelkasten", "Anki Cloze", "Jupyter(실험)", "Pomofocus"],
        "buddies": "ENTJ(추진력), ESFJ(루틴 안정화)",
    },
    "ENTJ": {
        "name": "ENTJ · 지휘관 🧨",
        "vibe": "목표지향·실적·속도",
        "strengths": ["추진력", "계획 실행", "의사결정"],
        "pitfalls": ["과부하 계획", "휴식 경시"],
        "strategies": [
            "🏁 **OKR**: Objective(1) + KR(3개 이하)로 주간 목표 설정",
            "📈 매일 **성과지표(문항수/학습시간/정확도)** 대시보드화",
            "👥 **가르치기 스터디(Teach-back)**로 리더십+이해도 상승",
            "🌿 **리커버리 블록**: 90분 집중 후 10–15분 회복 루틴",
        ],
        "tools": ["Google Sheets Dashboard", "Notion OKR", "Forest", "Past papers DB"],
        "buddies": "INTP(깊이), ISFJ(디테일·지속성)",
    },
    "ENTP": {
        "name": "ENTP · 발명가 💡",
        "vibe": "아이디어·토론·변화",
        "strengths": ["브레인스토밍", "문제 재정의", "즉흥성"],
        "pitfalls": ["금방 질림", "마무리 약함"],
        "strategies": [
            "🎲 **게임화**: 퀘스트·경험치·보상 시스템으로 과제 쪼개기",
            "🎤 **토론형 요약**: 3분 스피치·반박 포인트 만들기",
            "🧱 **마감형 스프린트(45분)** + 5분 데모(배운 것 발표)",
            "🔗 아이디어는 **칸반(Backlog→Doing→Done)**으로 흘려보내기",
        ],
        "tools": ["Trello/Asana", "Kahoot/Quizizz", "Voice Recorder 요약", "Anki"],
        "buddies": "INFJ(깊이·의미), ESTJ(실행·마감)",
    },
    "INFJ": {
        "name": "INFJ · 옹호자 🌙",
        "vibe": "의미·정리·몰입",
        "strengths": ["통찰", "메타인지", "서사적 정리"],
        "pitfalls": ["감정소진", "완벽주의 노트"],
        "strategies": [
            "🧭 **핵심 질문 3개** 정하고 모든 자료를 그 질문에 연결",
            "🧾 **한 페이지 요약(One-pager)**: 스토리·예시·오개념 정정",
            "🤝 **동료 튜터링**: 의미 부여 + 설명 능력 강화",
            "🌱 **루틴 앵커**: 고정 시간·고정 장소·고정 음악",
        ],
        "tools": ["Notion Template", "GoodNotes/OneNote", "Readwise", "Lofi playlist"],
        "buddies": "ENTP(관점 확장), ISTP(현실 검증)",
    },
    "INFP": {
        "name": "INFP · 중재자 🫧",
        "vibe": "가치·창의·몰입",
        "strengths": ["상상력", "글쓰기", "몰입"],
        "pitfalls": ["기분 따라 출렁임", "우선순위 혼란"],
        "strategies": [
            "💖 **가치 연결**: 오늘 공부가 내 장기 가치/학생에게 주는 영향 적기",
            "🍀 **3×3 플랜**: 오늘 3개, 이번주 3개, 이번달 3개",
            "🗣 **읽어-말해-쓰는** 3단 루프로 정서+기억 결합",
            "🎯 **미니 데드라인**: 30–40분 블록 + 스티커 보상",
        ],
        "tools": ["Notion Kanban", "Day One/Journal", "Speechify/TTS", "Anki"],
        "buddies": "ESTJ(현실·마감), ENFJ(동기 부여)",
    },
    "ENFJ": {
        "name": "ENFJ · 선도자 ✨",
        "vibe": "협업·피드백·코칭",
        "strengths": ["소통", "동기부여", "조직화"],
        "pitfalls": ["남 돌보느라 자기 공부 밀림"],
        "strategies": [
            "👥 **책임 파트너**: 매일 5분 상호 체크인(목표/진행/정서)",
            "🧾 **예습-수업-복습** 체크리스트로 흐름 고정",
            "📣 **피드백 루프**: 주 1회 모의강의 후 피드백 수집",
            "🧘 **경계 설정**: 돌봄 시간/학습 시간 캘린더로 분리",
        ],
        "tools": ["Google Calendar Block", "Notion Checklist", "Loom 모의강의", "Anki"],
        "buddies": "ISTP(현실성), INTJ(구조화)",
    },
    "ENFP": {
        "name": "ENFP · 활활러 ⚡",
        "vibe": "열정·연결·탐험",
        "strengths": ["발화력", "연결성", "창의"],
        "pitfalls": ["산만", "과다 약속"],
        "strategies": [
            "🏝 **테마 데이**(월:이론, 화:문제, 수:오답, …)로 다양성+일관성",
            "🧲 **집중 자석**: 10분 스타터 과제(제일 쉬운 것)로 시동",
            "🎥 **자기 설명 촬영(2분)** → 요약 카드 만들기",
            "🧱 **약속 제한 규칙**: 주당 큰 약속 2개까지만",
        ],
        "tools": ["Focusmate", "CapCut/Clips", "Quizizz", "TickTick"],
        "buddies": "ISTJ(안정), INTJ(전략)",
    },
    "ISTJ": {
        "name": "ISTJ · 관리자 📏",
        "vibe": "규율·정확·기록",
        "strengths": ["꾸준함", "정확성", "체계 문서화"],
        "pitfalls": ["변화 거부감", "과도한 디테일"],
        "strategies": [
            "📅 **루틴 캘린더링**: 매일 같은 시간·같은 장소·같은 순서",
            "✅ **체크리스트 기반 학습 흐름**(예습→학습→복습→테스트)",
            "🔄 **간격반복(SRS)**: 복습일 자동화",
            "🧭 주 1회 **전략 리뷰**로 전체 방향 점검",
        ],
        "tools": ["Google Calendar", "Notion Templates", "Anki", "Excel/Sheets 로그"],
        "buddies": "ENFP(유연성), ENTJ(목표 가속)",
    },
    "ISFJ": {
        "name": "ISFJ · 수호자 🫶",
        "vibe": "배려·성실·안정",
        "strengths": ["책임감", "기록", "세심함"],
        "pitfalls": ["자기 요구 후순위", "과부담"],
        "strategies": [
            "🌸 **따뜻한 시작**: 쉬운 과제로 성공감부터",
            "📦 **팩키지 공부**: 교재/노트/문제/오답 한 묶음으로 관리",
            "🧑‍🤝‍🧑 **짝 연습**: 설명·피드백으로 기억 강화",
            "🌿 **회복 루틴**: 스트레칭·티타임 예약",
        ],
        "tools": ["GoodNotes", "Notion Pack", "Focus To-Do", "Anki"],
        "buddies": "ENTP(발상), ENFJ(동기)",
    },
    "ISTP": {
        "name": "ISTP · 장인 🔧",
        "vibe": "실전·문제풀기·효율",
        "strengths": ["분석", "손에 익히기", "냉정함"],
        "pitfalls": ["이론 건너뛰기", "루틴 불안정"],
        "strategies": [
            "🧩 **문제→이론 역추적**: 틀린 문제에서 개념 북마크",
            "⏲ **스피드 드릴**: 제한시간 내 풀이 루틴화",
            "🧱 **최소 루틴(30분)**: 매일 같은 시각 최소블록 유지",
            "📒 **테크 로그**: 풀이 전략과 도구 설정 기록",
        ],
        "tools": ["Timer/Tabata", "Excel 풀이로그", "Past Papers", "Anki"],
        "buddies": "ENFJ(일관성), INFJ(깊이)",
    },
    "ISFP": {
        "name": "ISFP · 예술가 🎨",
        "vibe": "감각·감성·자율",
        "strengths": ["미적 감수성", "섬세함", "공감"],
        "pitfalls": ["동기 기복", "시간 추적 약함"],
        "strategies": [
            "🎧 **리추얼 플레이리스트** + 타임랩스 촬영으로 몰입 유도",
            "📷 **비주얼 노트**: 도식/색/아이콘으로 요약",
            "🧭 **가볍게 시작(10분)** → 몰입되면 연장",
            "⏱ **타임트래킹**으로 실제 공부시간 가시화",
        ],
        "tools": ["Notion Gallery", "GoodNotes/Procreate", "Toggl", "Anki"],
        "buddies": "ENTJ(목표), ESTJ(구조)",
    },
    "ESTJ": {
        "name": "ESTJ · 실행가 🏗️",
        "vibe": "규율·성과·리더십",
        "strengths": ["일정관리", "마감", "표준화"],
        "pitfalls": ["융통성 부족", "과도한 자기비판"],
        "strategies": [
            "📊 **WBS**로 범위 쪼개고 주간 간트차트 운영",
            "🧪 **주기적 모의고사**로 객관 지표 확보",
            "🧘 **완료-보상 프로토콜**(완료→짧은 산책/차)",
            "🧩 ‘예외일’ 대비 **버퍼 블록** 예약",
        ],
        "tools": ["Sheets Gantt", "Notion WBS", "Forest", "Past papers DB"],
        "buddies": "INFP(창의·균형), ENFP(동기)",
    },
    "ESFJ": {
        "name": "ESFJ · 사교가 🤝",
        "vibe": "협동·루틴·안정감",
        "strengths": ["협력", "꾸준함", "정리"],
        "pitfalls": ["외부 평판 의존", "자기 시간 부족"],
        "strategies": [
            "👥 **스터디 진행자 역할**로 책임감+몰입",
            "🧾 **체크리스트 락**: 끝낼 때까지 앱 잠금",
            "🧘 **1인 집중 타임**을 캘린더로 보호",
            "🧠 **퀴즈 리드**: 다른 사람 테스트 제작",
        ],
        "tools": ["Google Calendar", "StayFocusd/Focus", "Quizlet/Quizizz", "Anki"],
        "buddies": "INTP(깊이), ISTP(현실)",
    },
    "ESTP": {
        "name": "ESTP · 도전자 🏎️",
        "vibe": "액션·경쟁·현장감",
        "strengths": ["실전감각", "빠른 적응", "담대함"],
        "pitfalls": ["반복훈련 지루함", "장기 계획 약함"],
        "strategies": [
            "🏁 **타임어택 챌린지**: 기록 깨기식 훈련",
            "📣 **스몰 베팅**: 하루 목표 걸고 미션 성공시 보상",
            "🎯 **문제→바로 피드백**: 자동채점/즉시 오답",
            "🗺 **주간 미션보드**로 방향성 확보",
        ],
        "tools": ["Khan/Past papers", "Quiz apps", "Habitica", "Trello"],
        "buddies": "INFJ(깊이), ISFJ(안정)",
    },
    "ESFP": {
        "name": "ESFP · 엔터테이너 🎭",
        "vibe": "즐거움·즉흥·감각",
        "strengths": ["발표", "즉흥성", "관찰력"],
        "pitfalls": ["지속성 약함", "딴짓 유혹"]
