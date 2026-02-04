from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(data, filename):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    def title(t):
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(t, styles["Heading1"]))

    def bullets(items):
        bullet_items = [
            ListItem(Paragraph(str(x), styles["BodyText"])) for x in items
        ]
        elements.append(ListFlowable(bullet_items))

    title("Meeting Summary")
    elements.append(Paragraph(data["summary"], styles["BodyText"]))

    title("Key Points")
    bullets(data["key_points"])

    title("Decisions")
    bullets(data["decisions"])

    title("Action Items")
    bullets(data["action_items"])   # ✅ FIX

    doc.build(elements)
