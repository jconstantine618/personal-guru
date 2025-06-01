import streamlit as st
from openai import OpenAI
import datetime
import os

# ---- Configuration ----
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---- App Title ----
st.set_page_config(page_title="The Still Point", page_icon="🌀", layout="centered")
st.title("🌀 The Still Point")
st.caption("One question. One shift.")

# ---- Session State for Archive and Journal ----
if "archive" not in st.session_state:
    st.session_state.archive = []
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []

# ---- Mood Selector ----
mood = st.selectbox(
    "Choose your current state (optional):",
    ("", "Restless", "Overwhelmed", "Disconnected", "Grateful", "Clear")
)

# ---- Prompt Builder ----
def build_prompt(mood):
    base_prompt = (
        "Generate a single, reflective question that draws on deep philosophical and spiritual insight. "
        "Draw from the tone and wisdom found in ancient contemplative texts — the kind that offer paradox, poetic depth, and moral clarity. "
        "Let your question echo the spirit of writings that explore suffering, justice, love, awe, and the mystery of existence. "
        "The question should reframe how one thinks about life, love, purpose, or happiness amid complexity and responsibility. "
        "It should feel timeless, quiet, and expansive — without referencing any specific traditions or teachers. "
        "Assume the person reading it is thoughtful, driven, and often lives in their head. Your goal is to disrupt that gently."
    )
    if mood:
        base_prompt += f" The person is currently feeling {mood.lower()}."
    return base_prompt

# ---- Generate Question ----
def get_question(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a quiet and timeless muse. Speak only in thought-provoking questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=80
    )
    return response.choices[0].message.content.strip()

# ---- Ask Me a Question Button ----
if st.button("Ask Me a Question"):
    prompt = build_prompt(mood)
    question = get_question(prompt)
    st.session_state.current_question = question
    st.session_state.archive.insert(0, {"question": question, "timestamp": datetime.datetime.now().isoformat()})

# ---- Display Current Question ----
if st.session_state.current_question:
    st.markdown(f"### ❓ {st.session_state.current_question}")
    st.button("Save to Archive", on_click=lambda: None)  # Already saved on generation
    st.download_button("📋 Copy Question", st.session_state.current_question, file_name="reflection.txt")

    share_text = f"Here's a reflective question I came across:\n\n{st.session_state.current_question}"
    st.text_area("Shareable Text:", share_text)

# ---- Journal Entry Section ----
st.markdown("---")
st.subheader("📝 Journal Your Thoughts")
journal_input = st.text_area("Write your thoughts for today:")
if st.button("Save Journal Entry"):
    timestamp = datetime.datetime.now().isoformat()
    st.session_state.journal_entries.insert(0, {
        "entry": journal_input,
        "timestamp": timestamp,
        "question": st.session_state.current_question,
        "mood": mood
    })
    st.success("Journal entry saved.")

# ---- Sidebar Journal Viewer ----
st.sidebar.title("📔 Your Journals")
for i, journal in enumerate(st.session_state.journal_entries):
    date_str = journal['timestamp'].split('T')[0]
    label = f"{date_str} ({journal['mood']})" if journal['mood'] else date_str
    with st.sidebar.expander(label):
        st.markdown(f"**Question:** {journal['question']}")
        st.markdown(f"**Entry:**\n{journal['entry']}")

# ---- Archive Section ----
st.markdown("---")
st.subheader("📚 Your Archive")
for entry in st.session_state.archive:
    st.markdown(f"- _{entry['timestamp'].split('T')[0]}_: {entry['question']}")
