import re

TASK_PATTERNS = [
    r"(assign .* to \w+)",
    r"(follow up .*?)",
    r"(prepare .*?)",
    r"(update .*?)",
    r"(fix .*?)",
    r"(deploy .*?)",
    r"(complete .*?)",
    r"(review .*?)",
]

def regex_action_items(text):

    items = []

    for p in TASK_PATTERNS:
        for m in re.findall(p, text, flags=re.IGNORECASE):
            items.append({
                "task": m,
                "owner": "Unassigned"
            })

    return items
