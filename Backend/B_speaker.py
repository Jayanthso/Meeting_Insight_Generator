import re

def extract_speaker_actions(transcript):

    actions = []

    pattern = r"(\w+):\s(.+)"

    triggers = [
        "i will", "i'll", "i can", "let me",
        "i plan to", "i shall", "i am going to"
    ]

    for speaker, text in re.findall(pattern, transcript):
        lower = text.lower()

        if any(t in lower for t in triggers):
            actions.append({
                "task": text.strip(),
                "owner": speaker
            })

    return actions
