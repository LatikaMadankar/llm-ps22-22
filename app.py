import os
import re
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Flashcard Generator",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# LOAD API KEY
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Gemini API key not found. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)


# =========================================================
# HELPER FUNCTION
# =========================================================

def clean_text(text):
    """
    Removes HTML tags, Markdown code formatting, and extra spaces
    from Gemini-generated text.
    """
    text = str(text)

    # Remove markdown code blocks & html tag remnants if present
    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "")
    
    # Remove HTML tags completely
    text = re.sub(r"<[^>]*>", "", text)

    # Remove common markdown formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN BACKGROUND ---------- */

    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(91, 92, 255, 0.15), transparent 28%),
            radial-gradient(circle at 85% 80%, rgba(155, 89, 255, 0.12), transparent 28%),
            linear-gradient(135deg, #080b1a, #101936, #171044);
        color: #f5f7ff;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 4.5rem;
        padding-bottom: 3rem;
    }


    /* ---------- TITLE ---------- */

    .main-title {
        text-align: center;
        font-size: 44px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 30px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #aeb8d4;
        font-size: 17px;
        margin-bottom: 35px;
    }


    /* ---------- LABELS ---------- */

    .section-label {
        color: #b9c2ff;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }


    /* ---------- TEXT AREA ---------- */

    textarea {
        background-color: #111832 !important;
        color: #f5f7ff !important;
        border: 1px solid #303b68 !important;
        border-radius: 14px !important;
    }


    /* ---------- BUTTONS ---------- */

    .stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 12px;
        border: 1px solid #4653a5;
        background: linear-gradient(135deg, #5965ff, #8b5cf6);
        color: white;
        font-size: 16px;
        font-weight: 700;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #8d98ff;
        transform: translateY(-1px);
    }


    /* ---------- UNIFIED FLASHCARD CONTAINER ---------- */

    .flashcard-box {
        background: linear-gradient(145deg, #202957, #151b3c);
        border: 1px solid #394475;
        border-radius: 24px;
        padding: 35px;
        margin-top: 25px;
        margin-bottom: 18px;
        text-align: center;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
    }

    .card-number {
        color: #9ba8ff;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 15px;
    }

    .question-text {
        color: #ffffff;
        font-size: 24px;
        font-weight: 700;
        line-height: 1.5;
    }


    /* ---------- ANSWER ---------- */

    .answer-box {
        background: #111936;
        border: 1px solid #394475;
        border-radius: 18px;
        padding: 25px;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    .answer-label {
        color: #aab5ff;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }

    .answer-text {
        color: #e8ecff;
        font-size: 17px;
        line-height: 1.65;
    }


    /* ---------- PROGRESS ---------- */

    .progress-text {
        text-align: center;
        color: #aeb8d4;
        font-size: 14px;
        margin-top: 5px;
    }


    /* ---------- DIVIDER ---------- */

    .custom-divider {
        height: 1px;
        background: #29345c;
        margin: 30px 0;
    }


    /* ---------- DOWNLOAD ---------- */

    .stDownloadButton > button {
        width: 100%;
        border-radius: 12px;
        min-height: 46px;
        background: #151d3c;
        border: 1px solid #3d4a7d;
        color: #e9edff;
        font-weight: 600;
    }

    .stDownloadButton > button:hover {
        border-color: #6876c8;
    }


    /* ---------- SELECTBOX ---------- */

    div[data-baseweb="select"] > div {
        background-color: #111832;
        border-color: #303b68;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "flashcards" not in st.session_state:
    st.session_state.flashcards = None

if "current_card" not in st.session_state:
    st.session_state.current_card = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📚 Flashcard Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Turn your study notes into smart question-answer flashcards for quick revision.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# INPUT SECTION
# =========================================================

st.markdown(
    '<div class="section-label">📝 Study Notes</div>',
    unsafe_allow_html=True
)

notes = st.text_area(
    "Study Notes",
    height=230,
    placeholder=(
        "Paste your study notes here...\n\n"
        "Example:\n"
        "BERT is a transformer-based language model..."
    ),
    label_visibility="collapsed"
)


col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(
        '<div class="section-label">🎯 Number of Flashcards</div>',
        unsafe_allow_html=True
    )

    num_cards = st.selectbox(
        "Number of Flashcards",
        options=[3, 5, 7, 10],
        index=1,
        label_visibility="collapsed"
    )

with col2:
    st.markdown(
        '<div class="section-label">✨ Action</div>',
        unsafe_allow_html=True
    )

    generate_button = st.button(
        "✨ Generate Flashcards"
    )


# =========================================================
# GENERATE FLASHCARDS
# =========================================================

if generate_button:

    if not notes.strip():
        st.warning("⚠️ Please enter some study notes first.")

    else:

        prompt = f"""
You are an educational flashcard generator.

Convert the following study notes into exactly {num_cards}
question-answer flashcards.

IMPORTANT RULES:

1. Create exactly {num_cards} flashcards.
2. Questions must test important concepts from the notes.
3. Questions should be clear and useful for students.
4. Answers should be concise but informative.
5. Use ONLY information available in the study notes.
6. Do not add outside knowledge.
7. Do not create duplicate questions.
8. Return ONLY valid JSON as a list of dictionaries with keys "question" and "answer".
9. Do NOT use HTML tags or Markdown formatting inside the question or answer strings.

Return EXACTLY this JSON structure:
[
    {{
        "question": "Question here",
        "answer": "Answer here"
    }}
]

Study Notes:
{notes}
"""

        try:

            with st.spinner("✨ Creating your flashcards..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "thinking_config": {
                            "thinking_level": "low"
                        }
                    }
                )

                raw_output = response.text.strip()
                raw_output = re.sub(r"```[a-zA-Z]*", "", raw_output).replace("```", "").strip()

                flashcards = json.loads(raw_output)

                if not isinstance(flashcards, list):
                    raise ValueError("Gemini did not return a list of flashcards.")

                cleaned_flashcards = []

                for card in flashcards:
                    if not isinstance(card, dict):
                        continue

                    question = clean_text(card.get("question", ""))
                    answer = clean_text(card.get("answer", ""))

                    if question and answer:
                        cleaned_flashcards.append(
                            {
                                "question": question,
                                "answer": answer
                            }
                        )

                if not cleaned_flashcards:
                    raise ValueError("No valid flashcards were generated.")

                cleaned_flashcards = cleaned_flashcards[:num_cards]
                df = pd.DataFrame(cleaned_flashcards)

                st.session_state.flashcards = df
                st.session_state.current_card = 0
                st.session_state.show_answer = False

            st.success(f"✅ {len(cleaned_flashcards)} flashcards generated successfully!")

        except json.JSONDecodeError:
            st.error("❌ Gemini returned an invalid JSON response. Please try generating again.")

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")


# =========================================================
# DISPLAY FLASHCARDS
# =========================================================

if st.session_state.flashcards is not None:

    df = st.session_state.flashcards
    total_cards = len(df)

    if st.session_state.current_card >= total_cards:
        st.session_state.current_card = total_cards - 1

    current = st.session_state.current_card

    question = clean_text(df.iloc[current]["question"])
    answer = clean_text(df.iloc[current]["answer"])

    # -----------------------------------------------------
    # PROGRESS
    # -----------------------------------------------------

    progress_value = (current + 1) / total_cards
    st.progress(progress_value)

    st.markdown(
        f'<div class="progress-text">Flashcard {current + 1} of {total_cards}</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # QUESTION CARD (Unified clean block)
    # -----------------------------------------------------

    safe_question = (
        question
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    st.markdown(
        f"""
        <div class="flashcard-box">
            <div class="card-number">FLASHCARD {current + 1}</div>
            <div class="question-text">{safe_question}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # ANSWER
    # -----------------------------------------------------

    if st.session_state.show_answer:
        safe_answer = (
            answer
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        st.markdown(
            f"""
            <div class="answer-box">
                <div class="answer-label">✦ ANSWER</div>
                <div class="answer-text">{safe_answer}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.button("👀 Reveal Answer", key=f"reveal_{current}"):
            st.session_state.show_answer = True
            st.rerun()

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        if st.button("← Previous", disabled=(current == 0), key="previous_card"):
            st.session_state.current_card -= 1
            st.session_state.show_answer = False
            st.rerun()

    with nav2:
        if st.button("🔄 Hide Answer", disabled=(not st.session_state.show_answer), key="hide_answer"):
            st.session_state.show_answer = False
            st.rerun()

    with nav3:
        if st.button("Next →", disabled=(current == total_cards - 1), key="next_card"):
            st.session_state.current_card += 1
            st.session_state.show_answer = False
            st.rerun()

    # -----------------------------------------------------
    # DOWNLOAD CSV
    # -----------------------------------------------------

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📥 Export Flashcards</div>', unsafe_allow_html=True)

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Flashcards as CSV",
        data=csv_data,
        file_name="flashcards.csv",
        mime="text/csv"
    )