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
if "journal_box_key" not in st.session_state:
    st.session_state.journal_box_key = 0
if "archive" not in st.session_state:
    st.session_state.archive = []
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []

# ---- Mood and Philosopher Selectors ----
mood_options = (
    "Restless", "Overwhelmed", "Disconnected", "Anxious", "Stuck", "Numb",
    "Curious", "Tender", "Grateful", "Hopeful", "Motivated", "Clear", "Sad"
)

mood = st.selectbox(
    "Choose your current state of mind (optional):",
    options=[""] + list(mood_options)
)

philosopher_options = {
    "None": "No specific voice",
    "Socrates": "Greek philosopher known for the Socratic method and questioning assumptions",
    "Laozi": "Ancient Chinese sage and founder of Taoism, master of paradox and flow",
    "Buddha": "Indian prince turned spiritual teacher who taught the path to enlightenment",
    "Jesus": "Jewish teacher and moral reformer whose parables challenged societal norms",
    "Rumi": "Persian Sufi poet and mystic exploring divine love and longing",
    "Confucius": "Chinese philosopher focused on virtue, duty, and moral harmony",
    "Marcus Aurelius": "Stoic Roman emperor who wrote deeply about self-discipline and fate",
    "Teresa of Ávila": "Christian mystic whose writings explore the soul’s union with God",
    "Nietzsche": "Existential philosopher who questioned morality and celebrated self-overcoming",
    "Solomon": "Biblical king known for his wisdom literature on meaning, time, and toil"
}

philosopher = st.selectbox(
    "Select a philosophical voice to inspire your question:",
    options=list(philosopher_options.keys()),
    format_func=lambda key: f"{key} — {philosopher_options[key]}"
)

# ---- Prompt Builder ----
def build_prompt(mood, philosopher):
    base_prompt = (
        "Write a single, thoughtful question meant to help someone reflect deeply on their life, choices, and values. "
        "The question should be poetic but not flowery, direct but not blunt, and layered with meaning. "
        "It should avoid excessive metaphor or romantic language. Instead, use clean, resonant phrasing that carries depth and emotional clarity. "
        f"The tone and logic of the question should reflect the voice of {philosopher_options[philosopher]}."
    )

    voice_map = {
        "Socrates": "Channel the spirit of Socrates — ask a question that uncovers hidden assumptions, provokes dialogue, and guides the reader toward self-examination.",
        "Laozi": "Use the voice of Laozi — soft, paradoxical, rooted in nature and non-action, pointing to harmony through simplicity and surrender.",
        "Buddha": "Speak with the quiet clarity of the Buddha — a question that points toward detachment, mindfulness, compassion, and the impermanence of all things.",
        "Jesus": "Let the tone reflect the parables and moral paradoxes of Jesus — challenging, upside-down wisdom that elevates love, humility, and soul over status.",
        "Rumi": "Speak in the poetic, passionate, soul-thirsting voice of Rumi — a question that dances with longing, union, love, and divine mystery.",
        "Confucius": "Adopt the clear moral logic of Confucius — wise, relational, virtuous, practical; pointing the reader toward integrity in the ordinary.",
        "Marcus Aurelius": "Channel Marcus Aurelius — calm, reflective, stoic; ask a question that orients the reader toward acceptance, inner strength, and right action.",
        "Teresa of Ávila": "Ask with the mystical intimacy of Teresa of Ávila — a question that calls the soul inward toward surrender, ecstasy, and divine companionship.",
        "Nietzsche": "Speak with Nietzsche’s boldness — challenge the reader to confront chaos, self-deception, and power, and to carve meaning with raw authenticity.",
        "Solomon": "Let the voice be that of Solomon from the wisdom books — paradoxical, regal, full of proverbs and contemplative observations on time, toil, and meaning."
    }

    if philosopher in voice_map:
        base_prompt += " " + voice_map[philosopher]

    if mood:
        base_prompt += (
            f" The person reading it is currently feeling {mood.lower()}, "
            "so the question should acknowledge or gently respond to that emotional state."
        )

    base_prompt += (
        " The goal is to ask something that breaks through surface thinking and lingers in the reader’s mind — something they’d want to sit with."
    )

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
    prompt = build_prompt(mood, philosopher)
    question = get_question(prompt)
    st.session_state.current_question = question
    st.session_state.archive.insert(0, {"question": question, "timestamp": datetime.datetime.now().isoformat()})

# ---- Display Current Question ----
if st.session_state.current_question:
    st.markdown(f"### {st.session_state.current_question}")
    if philosopher != "None":
        st.markdown(f"_Inspired by: **{philosopher}**_")
    st.button("Save to Archive", on_click=lambda: None)  # Already saved on generation
    st.download_button("📋 Copy Question", st.session_state.current_question, file_name="reflection.txt")

# ---- Journal Entry Section ----
st.markdown("---")
st.subheader("📝 Journal Your Thoughts")
journal_input = st.text_area("Write your thoughts for today:", key=f"journal_input_{st.session_state.journal_box_key}")
if st.button("Save Journal Entry"):
    timestamp = datetime.datetime.now().isoformat()
    st.session_state.journal_entries.insert(0, {
        "entry": journal_input,
        "timestamp": timestamp,
        "question": st.session_state.current_question,
        "mood": mood
    })
    st.success("Journal entry saved.")
    st.session_state.journal_box_key += 1

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
