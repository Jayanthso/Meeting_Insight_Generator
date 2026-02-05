# =========================================================
# Streamlit Frontend — Production UI
# =========================================================

import streamlit as st
import os

from Backend.A_STT import transcribe_audio
from Backend.F_llm import generate_insights
from Backend.D_pdf_export import generate_pdf


# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Meeting Insight Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Meeting Insight Generator")
st.caption("Turn meetings into summaries, decisions, and action items instantly")


# =========================================================
# Sidebar controls
# =========================================================
with st.sidebar:
    st.header("⚙️ Settings")

    title = st.text_input("Meeting Title", "Weekly Sync")
    meeting_type = st.selectbox(
        "Meeting Type",
        ["discussion", "standup", "planning", "review"]
    )

    st.divider()

    st.info(
        "Tips:\n"
        "- Paste transcript for fastest results\n"
        "- WAV audio works best\n"
        "- Longer meetings may take 5–10s"
    )


# =========================================================
# Input Section
# =========================================================
tab1, tab2 = st.tabs(["📝 Transcript", "🎙 Audio Upload"])

transcript = ""
audio_file = None

with tab1:
    transcript = st.text_area(
        "Paste transcript",
        height=300,
        placeholder="Paste meeting notes or transcript here..."
    )

with tab2:
    audio_file = st.file_uploader(
        "Upload WAV file",
        type=["wav"]
    )


# =========================================================
# Display helpers
# =========================================================
def metric_cards(insights):
    c1, c2, c3 = st.columns(3)

    c1.metric("Key Points", len(insights["key_points"]))
    c2.metric("Decisions", len(insights["decisions"]))
    c3.metric("Action Items", len(insights["action_items"]))


def display_section(title, items):
    st.subheader(title)

    if not items:
        st.caption("No items detected")
        return

    for x in items:
        st.write("•", x)


def display_actions(actions):
    st.subheader("📌 Action Items")

    if not actions:
        st.caption("No actions detected")
        return

    for a in actions:
        owner = a.get("owner", "")
        deadline = a.get("deadline", "")

        line = f"• {a['task']}"
        if owner:
            line += f" — 👤 {owner}"
        if deadline:
            line += f" — ⏰ {deadline}"

        st.write(line)


def display(insights):
    metric_cards(insights)

    st.divider()

    st.subheader("🧾 Summary")
    st.write(insights["summary"])

    col1, col2 = st.columns(2)

    with col1:
        display_section("📍 Key Points", insights["key_points"])

    with col2:
        display_section("✅ Decisions", insights["decisions"])

    st.divider()
    display_actions(insights["action_items"])


# =========================================================
# Generate button
# =========================================================
if st.button("🚀 Generate Insights", use_container_width=True):

    try:
        # -------- audio -> transcript --------
        if audio_file is not None:
            suffix = os.path.splitext(audio_file.name)[-1]
            tmp = f"temp{suffix}"

            with open(tmp, "wb") as f:
                f.write(audio_file.read())

            with st.spinner("🎙 Transcribing audio..."):
                transcript = transcribe_audio(tmp)

            os.remove(tmp)

        if not transcript:
            st.error("Please provide transcript or audio")
            st.stop()

        # -------- NLP --------
        with st.spinner("🧠 Analyzing meeting..."):
            insights = generate_insights(transcript, title, meeting_type)

        # -------- PDF --------
        with st.spinner("📄 Generating PDF report..."):
            pdf_path = "meeting_report.pdf"
            generate_pdf(insights, pdf_path, title)

        # -------- display --------
        display(insights)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇ Download PDF Report",
                f,
                "meeting_report.pdf",
                use_container_width=True
            )

    except Exception as e:
        st.error(str(e))
