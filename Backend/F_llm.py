from transformers import pipeline
import re
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def summarize(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # 3 sentences
    return " ".join([str(sentence) for sentence in summary])



# ----------- heuristics -----------

def extract_actions(text: str):
    """
    Returns structured action items:
    [
      {"task": "...", "owner": "..."}
    ]
    """

    actions = []

    action_keywords = [
        " will ",
        " must ",
        " by ",
        " start", " starts",
        " prepare", " prepares",
        " draft", " drafts",
        " deliver", " delivers",
        " escalate",
        " action item",
    ]

    for line in text.split("\n"):
        sentence = line.strip()

        if not sentence:
            continue

        lower = sentence.lower()

        # ---------- Step 1: detect action ----------
        if not any(k in lower for k in action_keywords):
            continue

        original = sentence

        # ---------- Step 2: remove speaker label ----------
        if ":" in sentence:
            sentence = sentence.split(":", 1)[1].strip()

        # ---------- Step 3: extract owner ----------
        owner = ""

        # Pattern 1 → "Rahul will prepare..."
        m = re.match(r"^([A-Z][a-zA-Z]+)\s+(will|must|to|can|should|starts?|prepares?|drafts?|delivers?)", sentence)
        if m:
            owner = m.group(1)

        # Pattern 2 → "Meera, can you draft..."
        if not owner:
            m = re.match(r"^([A-Z][a-zA-Z]+),", sentence)
            if m:
                owner = m.group(1)

        # Pattern 3 → "Arjun’s team..."
        if not owner:
            m = re.match(r"^([A-Z][a-zA-Z]+)['’]s", sentence)
            if m:
                owner = m.group(1)

        if not owner:
            owner = "Unassigned"

        # ---------- Step 4: clean task ----------
        task = sentence

        # remove "Action item:"
        task = re.sub(r"(?i)action item[:\-]?", "", task)

        # remove owner name at start
        task = re.sub(rf"^{owner}\b[,:\s]*", "", task)

        task = task.strip()

        actions.append({
            "task": task,
            "owner": owner
        })

    return actions


def extract_decisions(text):
    keywords = ["decided", "approved", "confirmed", "deadline", "must"]

    return [
        l.strip()
        for l in text.split("\n")
        if any(k in l.lower() for k in keywords)
    ]


def extract_key_points(text):
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 40]
    return lines[:6]


# ----------- main -----------
def generate_insights(transcript, title="", meeting_type="discussion"):

    return {
        "summary": summarize(transcript),
        "key_points": extract_key_points(transcript),
        "decisions": extract_decisions(transcript),
        "action_items": extract_actions(transcript)
    }

