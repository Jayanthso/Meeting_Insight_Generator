# =========================================================
# Professional PDF Export
# =========================================================

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(data, filename, title="Meeting Report"):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    elements = []

    # -----------------------------------------------------
    # helpers
    # -----------------------------------------------------
    def heading(text):
        elements.append(Spacer(1, 18))
        elements.append(Paragraph(text, styles["Heading1"]))

    def bullets(items):
        if not items:
            elements.append(Paragraph("None", styles["BodyText"]))
            return

        lst = []
        for x in items:
            lst.append(ListItem(Paragraph(str(x), styles["BodyText"])))

        elements.append(ListFlowable(lst, bulletType="bullet"))

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 20))

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------
    heading("Summary")
    elements.append(Paragraph(data["summary"], styles["BodyText"]))

    # -----------------------------------------------------
    # Key Points
    # -----------------------------------------------------
    heading("Key Points")
    bullets(data["key_points"])

    # -----------------------------------------------------
    # Decisions
    # -----------------------------------------------------
    heading("Decisions")
    bullets(data["decisions"])

    # -----------------------------------------------------
    # Action Items
    # -----------------------------------------------------
    heading("Action Items")

    actions = []

    for a in data["action_items"]:
        line = a["task"]

        if a.get("owner"):
            line += f" — {a['owner']}"

        if a.get("deadline"):
            line += f" ({a['deadline']})"

        actions.append(line)

    bullets(actions)

    doc.build(elements)
