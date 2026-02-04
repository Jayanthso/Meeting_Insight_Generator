import streamlit as st
import os
from Backend.A_STT import transcribe_audio
from Backend.F_llm import generate_insights
from Backend.D_pdf_export import generate_pdf

# --- Streamlit page setup ---
st.set_page_config(layout="wide")
st.title("📊 AI Meeting Insight Generator")

# --- Inputs ---
title = st.text_input("Meeting Title")
meeting_type = st.selectbox("Meeting Type", ["standup", "planning", "review", "discussion"])

# Option 1: Paste transcript
transcript = st.text_area("Paste transcript", height=300)

# Option 2: Upload audio file
audio_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])


# --- Helper to display insights ---
def display(insights):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Summary")
        st.write(insights.get("summary", ""))

        st.subheader("Key Points")
        for k in insights.get("key_points", []):
            st.write("•", k)

    with col2:
        st.subheader("Decisions")
        for d in insights.get("decisions", []):
            st.write("•", d)

        st.subheader("Action Items")
        for a in insights.get("action_items", []):
            if isinstance(a, dict):
                st.write(f"• {a.get('task','')} — {a.get('owner','')}")
            else:
                st.write(f"• {a}")


# --- Main button ---
if st.button("Generate Insights"):
    try:
        # If audio uploaded, transcribe it
        if audio_file is not None:
            suffix = os.path.splitext(audio_file.name)[-1] or ".mp3"
            audio_path = f"temp_upload{suffix}"
            with open(audio_path, "wb") as f:
                f.write(audio_file.read())

            with st.spinner("Transcribing audio… please wait"):
                transcript = transcribe_audio(audio_path)

            os.remove(audio_path)

        if not transcript:
            st.error("No transcript or audio provided")
        else:
            with st.spinner("Generating insights…"):
                insights = generate_insights(transcript)

            with st.spinner("Exporting PDF…"):
                pdf_path = "report.pdf"
                generate_pdf(insights, pdf_path)

            # Show results
            display(insights)

            # Download button
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, "meeting_report.pdf")

    except Exception as e:
        st.error(f"Error: {e}")
