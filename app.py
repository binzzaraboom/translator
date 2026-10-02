import streamlit as st

from translator import (
    InvalidResponseError,
    MissingApiKeyError,
    TranslationAPIError,
    get_config,
    translate,
)

MAX_CHARS = 5000
WARN_CHARS = 4500

# 국기 이모지는 Windows에서 글자(US, JP)로 보이므로 언어 코드 배지를 사용한다.
LANGUAGES = {
    "en": {"badge": "EN", "label": "English"},
    "ja": {"badge": "JA", "label": "日本語"},
    "vi": {"badge": "VI", "label": "Tiếng Việt"},
}

ERROR_MESSAGES = {
    MissingApiKeyError: "API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.",
    TranslationAPIError: "번역 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    InvalidResponseError: "번역 결과를 처리하지 못했습니다. 다시 시도해주세요.",
}

CSS = """
<style>
.block-container { max-width: 1200px; padding-top: 2.5rem; }
.subtitle { margin: -0.75rem 0 1.5rem; opacity: 0.7; }
.char-count { text-align: right; font-size: 0.85rem; opacity: 0.65; margin-top: -0.5rem; }
.char-count.warn { color: #E8890C; opacity: 1; }
.char-count.over { color: #E5484D; opacity: 1; font-weight: 600; }
.lang-head { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; font-size: 1.05rem; margin-bottom: 0.5rem; }
.lang-badge { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; padding: 0.1rem 0.45rem;
              border-radius: 0.4rem; background: rgba(127, 127, 127, 0.15); }
.empty-result { text-align: center; padding: 2rem 1rem; opacity: 0.6; }
.footer { text-align: center; font-size: 0.8rem; opacity: 0.5; margin-top: 3rem; }
</style>
"""

st.set_page_config(page_title="다국어 번역기", page_icon="🌐", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None

config = get_config()
has_api_key = bool(config["api_key"])

# 사이드바: 대상 언어 선택 (F-10), 사용 방법, 모델 정보
with st.sidebar:
    st.header("번역할 언어", anchor=False)
    selected = [
        code for code, lang in LANGUAGES.items() if st.checkbox(lang["label"], value=True, key=f"lang_{code}")
    ]
    st.divider()
    st.subheader("사용 방법", anchor=False)
    st.markdown(
        "1. 번역할 언어를 선택합니다.\n"
        "2. 번역할 글을 입력합니다.\n"
        "3. **번역하기**를 누릅니다.\n"
        "4. 결과 칸 오른쪽 위의 복사 버튼으로 복사합니다."
    )
    st.divider()
    st.caption(f"모델: {config['model']}")

# 헤더
st.title("🌐 다국어 번역기", anchor=False)
st.markdown('<p class="subtitle">영어 · 일본어 · 베트남어로 한 번에 번역합니다</p>', unsafe_allow_html=True)

if not has_api_key:
    st.error(ERROR_MESSAGES[MissingApiKeyError])

# 입력 영역
text = st.text_area(
    "번역할 글",
    placeholder="번역할 글을 입력하세요...",
    height=200,
    label_visibility="collapsed",
)
count_class = "over" if len(text) > MAX_CHARS else "warn" if len(text) >= WARN_CHARS else ""
st.markdown(
    f'<div class="char-count {count_class}">글자 수: {len(text):,} / {MAX_CHARS:,}</div>',
    unsafe_allow_html=True,
)

if st.button("번역하기", type="primary", width="stretch", disabled=not has_api_key):
    if not text.strip():
        st.warning("번역할 글을 입력해주세요.")
    elif len(text) > MAX_CHARS:
        st.warning(f"최대 {MAX_CHARS:,}자까지 입력할 수 있습니다.")
    elif not selected:
        st.warning("번역할 언어를 하나 이상 선택해주세요.")
    else:
        try:
            with st.spinner("번역 중입니다..."):
                st.session_state.result = translate(text, selected)
        except tuple(ERROR_MESSAGES) as e:
            st.error(ERROR_MESSAGES[type(e)])

# 결과 영역
st.subheader("번역 결과", anchor=False)
result = st.session_state.result
shown = [code for code in selected if result and code in result]

if shown:
    # 좁은 화면(모바일)에서는 Streamlit이 컬럼을 자동으로 세로로 쌓는다.
    for col, code in zip(st.columns(len(shown)), shown):
        with col, st.container(border=True):
            lang = LANGUAGES[code]
            st.markdown(
                f'<div class="lang-head"><span class="lang-badge">{lang["badge"]}</span>{lang["label"]}</div>',
                unsafe_allow_html=True,
            )
            st.code(result[code], language=None, wrap_lines=True)
else:
    with st.container(border=True):
        st.markdown(
            '<div class="empty-result">글을 입력하고 <b>번역하기</b>를 누르면 여기에 번역 결과가 표시됩니다.</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div class="footer">Powered by OpenAI {config["model"]} · Built with Streamlit</div>',
    unsafe_allow_html=True,
)
