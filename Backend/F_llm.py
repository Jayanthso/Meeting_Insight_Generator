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
def extract_actions(text):
    patterns = [
        r"\bwill\b.*",
        r"\bprepare\b.*",
        r"\bstart\b.*",
        r"\bdraft\b.*",
        r"\bdeliver\b.*",
        r"\bdeadline\b.*",
        r"\baction\b.*",
        r"\bfollowup\b.*",
    ]

    actions = []
    for line in text.split("\n"):
        for p in patterns:
            if re.search(p, line.lower()):
                actions.append(line.strip())
                break

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
