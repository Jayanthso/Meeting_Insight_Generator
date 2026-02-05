import re

def extract_actions(text):
    action_verbs = [
        "will",
        "start", "starts", "starting",
        "prepare", "prepares",
        "draft", "drafts",
        "deliver", "delivers",
        "send", "sends",
        "complete", "completes",
        "escalate", "esclate",
        "follow up", "follow-up",
        "must",
        "need to",
        "action"
    ]

    actions = []

    for line in text.split("\n"):
        clean = line.strip()

        if not clean:
            continue

        lower = clean.lower()

        if any(v in lower for v in action_verbs):
            actions.append(clean)

    return actions
