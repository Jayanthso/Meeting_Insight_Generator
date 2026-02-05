import re


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
