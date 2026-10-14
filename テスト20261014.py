"""海の魚クイズ（Streamlit版）

実行方法:
    pip install streamlit
    streamlit run テスト20261014.py
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


QUESTIONS = [
    {
        "question": "サメの中でも最も大きい種類はどれ？",
        "choices": ["ホホジロザメ", "ジンベエザメ", "シュモクザメ", "オオメジロザメ"],
        "answer": "ジンベエザメ",
    },
    {
        "question": "クラゲのように見えるが、実はサンゴの仲間であるのはどれ？",
        "choices": ["カツオ", "イソギンチャク", "サメ", "タコ"],
        "answer": "イソギンチャク",
    },
    {
        "question": "海の魚の中で、体の色が青くて速く泳ぐ代表的な魚はどれ？",
        "choices": ["マグロ", "フグ", "カレイ", "タツノオトシゴ"],
        "answer": "マグロ",
    },
    {
        "question": "海底で砂に埋もれて暮らし、目が大きく頭が平たい魚はどれ？",
        "choices": ["カレイ", "ウナギ", "サバ", "ハマチ"],
        "answer": "カレイ",
    },
    {
        "question": "海の中で「海の宝石」と呼ばれることがある、色とりどりの魚はどれ？",
        "choices": ["チョウチョウウオ", "サケ", "ブリ", "ニシン"],
        "answer": "チョウチョウウオ",
    },
]

# 背景画像（このスクリプトと同じフォルダに置く、縦長に切り取った磯釣りの写真）
BG_IMAGE = Path(__file__).parent / "isozuri_bg.jpg"

# 磯釣りの写真を背景に、クイズ部分は半透明のすりガラス風カード。
# ボタンはスマホでタップしやすい横幅いっぱい・大きめ。
# アクセント色は写真の釣り糸の蛍光イエロー。
PAGE_CSS = """
<style>
.stApp {
    background: #0b1a26;
    isolation: isolate;
}

/* 背景写真（iPhoneでも固定表示されるよう ::before で敷く） */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    background:
        linear-gradient(180deg,
            rgba(6, 16, 26, 0.55) 0%,
            rgba(6, 16, 26, 0.15) 35%,
            rgba(6, 16, 26, 0.25) 65%,
            rgba(6, 16, 26, 0.75) 100%),
        __BG__ center / cover no-repeat;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* クイズ部分：半透明のすりガラス風カード */
[data-testid="stMainBlockContainer"], .block-container {
    max-width: 34rem;
    margin-top: 2.5rem;
    padding: 1.75rem 1.25rem 2rem;
    background: rgba(8, 22, 34, 0.48);
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 1.5rem;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
}

.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
[data-testid="stMetricLabel"] p {
    color: #f4f8fb;
}

.stApp h1 {
    font-weight: 800;
    letter-spacing: 0.06em;
    text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
}

.stApp h1::after {
    content: "";
    display: block;
    width: 3rem;
    height: 3px;
    margin-top: 0.5rem;
    border-radius: 2px;
    background: #e4ff3a;
    box-shadow: 0 0 10px rgba(228, 255, 58, 0.7);
}

[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: rgba(244, 248, 251, 0.75);
}

[data-testid="stMetricValue"] {
    color: #e4ff3a;
    text-shadow: 0 0 14px rgba(228, 255, 58, 0.45);
}

[data-testid="stAlert"] p {
    color: #ffffff;
}

/* 選択肢ボタン */
div.stButton > button {
    width: 100%;
    min-height: 3.5rem;
    font-size: 1.15rem;
    font-weight: 600;
    border-radius: 0.9rem;
    color: #f4f8fb;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.28);
    transition: all 0.15s ease;
}

div.stButton > button:hover,
div.stButton > button:active {
    color: #e4ff3a;
    background: rgba(255, 255, 255, 0.14);
    border-color: #e4ff3a;
}

div.stButton > button:disabled {
    color: rgba(244, 248, 251, 0.5);
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.12);
}

/* 「次の問題へ」などのメインボタン */
div.stButton > button[kind="primary"] {
    color: #0b1a26;
    background: #e4ff3a;
    border-color: #e4ff3a;
    box-shadow: 0 0 18px rgba(228, 255, 58, 0.45);
}

div.stButton > button[kind="primary"]:hover {
    color: #0b1a26;
    background: #f0ff7a;
}
</style>
"""


@st.cache_data
def load_page_css() -> str:
    """背景画像を埋め込んだCSSを作る。画像がなければ単色背景にする。"""
    if BG_IMAGE.exists():
        encoded = base64.b64encode(BG_IMAGE.read_bytes()).decode()
        background = f'url("data:image/jpeg;base64,{encoded}")'
    else:
        background = "#0b1a26"
    return PAGE_CSS.replace("__BG__", background)


def init_state() -> None:
    """セッション状態を初期化する。"""
    st.session_state.setdefault("index", 0)
    st.session_state.setdefault("score", 0)
    st.session_state.setdefault("selected", None)


def select_choice(choice: str) -> None:
    """選択肢がタップされたときの処理。"""
    if st.session_state.selected is not None:
        return
    st.session_state.selected = choice
    if choice == QUESTIONS[st.session_state.index]["answer"]:
        st.session_state.score += 1


def next_question() -> None:
    """次の問題へ進む。"""
    st.session_state.index += 1
    st.session_state.selected = None


def restart() -> None:
    """最初からやり直す。"""
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.selected = None


def show_question() -> None:
    """現在の問題を表示する。"""
    index = st.session_state.index
    item = QUESTIONS[index]
    selected = st.session_state.selected

    st.progress(index / len(QUESTIONS), text=f"{index + 1} / {len(QUESTIONS)} 問目")
    st.subheader(f"Q{index + 1}. {item['question']}")

    for choice_index, choice in enumerate(item["choices"]):
        st.button(
            choice,
            key=f"q{index}_c{choice_index}",
            on_click=select_choice,
            args=(choice,),
            disabled=selected is not None,
        )

    if selected is None:
        return

    if selected == item["answer"]:
        st.success("正解！")
    else:
        st.error(f"不正解です。正解は「{item['answer']}」です。")

    is_last = index == len(QUESTIONS) - 1
    st.button(
        "結果を見る" if is_last else "次の問題へ ▶",
        key=f"next_{index}",
        type="primary",
        on_click=next_question,
    )


def show_result() -> None:
    """最終結果を表示する。"""
    score = st.session_state.score
    total = len(QUESTIONS)

    st.subheader("終了！")
    st.metric("あなたの得点", f"{score} / {total} 点")

    if score == total:
        st.balloons()
        st.success("すごい！海の魚マスターですね！")
    elif score >= 3:
        st.info("いい感じ！かなり知っていますね。")
    else:
        st.warning("次はもっと海の魚を勉強してみましょう！")

    st.button("もう一度挑戦する", type="primary", on_click=restart)


def main() -> None:
    """プログラムの入口。"""
    st.set_page_config(page_title="海の魚クイズ", page_icon="🐟", layout="centered")
    st.markdown(load_page_css(), unsafe_allow_html=True)
    init_state()

    st.title("🐟 海の魚クイズ")
    st.caption(f"{len(QUESTIONS)}問あります。頑張ってね！")

    if st.session_state.index < len(QUESTIONS):
        show_question()
    else:
        show_result()


if __name__ == "__main__":
    main()
