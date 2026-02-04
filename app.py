import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(layout="wide")
st.title("📊 AI Meeting Insight Generator")

title = st.text_input("Meeting Title")

meeting_type = st.selectbox(
    "Meeting Type",
    ["standup", "planning", "review", "discussion"]
)

# Option 1: Paste transcript
transcript = st.text_area("Paste transcript", height=300)

# Option 2: Upload audio file
audio_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])


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


if st.button("Generate Insights"):
    # Always call /process
    if audio_file is not None:
        # Send audio file
        files = {"audio": audio_file}
        data = {"title": title, "meeting_type": meeting_type}
        res = requests.post(API + "/process", data=data, files=files)
    else:
        # Send transcript text
        data = {"transcript": transcript, "title": title, "meeting_type": meeting_type}
        res = requests.post(API + "/process", data=data)

    st.write("Status:", res.status_code)

    if res.status_code == 200:
        result = res.json()
        display(result["insights"])

        with open(result["pdf_path"], "rb") as f:
            st.download_button("Download PDF", f, "meeting_report.pdf")
    else:
        st.error(res.text)
