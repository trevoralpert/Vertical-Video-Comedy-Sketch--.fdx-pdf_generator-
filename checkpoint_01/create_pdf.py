from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import textwrap

def create_screenplay_pdf(script_text: str, filename: str) -> str:
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Final Draft-style margins
    left_margin = 72       # 1 inch
    right_margin = 72      # 1 inch
    top_margin = 72
    bottom_margin = 72
    line_height = 14

    char_width = c.stringWidth("M", "Courier", 12)  # Width of a monospaced character

    y = height - top_margin
    c.setFont("Courier", 12)
    lines = script_text.splitlines()
    previous_type = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            y -= line_height
            previous_type = None
            continue

        # Determine paragraph type
        if stripped.startswith("INT.") or stripped.startswith("EXT."):
            ptype = "Scene Heading"
        elif stripped.startswith("(") and stripped.endswith(")"):
            ptype = "Parenthetical"
        elif stripped.upper() == stripped and len(stripped.split()) <= 4:
            ptype = "Character"
        elif previous_type in ("Character", "Parenthetical"):
            ptype = "Dialogue"
        else:
            ptype = "Action"

        # Insert extra spacing between blocks
        if previous_type == "Dialogue" and ptype == "Action":
            y -= line_height

        if y < bottom_margin:
            c.showPage()
            c.setFont("Courier", 12)
            y = height - top_margin

        # Rendering based on type
        if ptype == "Scene Heading":
            max_chars = int((width - left_margin - right_margin) // char_width)
            wrapped = textwrap.wrap(stripped, width=max_chars)
            for wline in wrapped:
                c.drawString(left_margin, y, wline)
                y -= line_height

        elif ptype == "Action":
            # Give ~2 more chars room than before (previously width = 90 chars, now ~92)
            max_chars = int((width - left_margin - right_margin + 10) // char_width)
            wrapped = textwrap.wrap(stripped, width=max_chars)
            for wline in wrapped:
                c.drawString(left_margin, y, wline)
                y -= line_height

        elif ptype == "Character":
            c.drawCentredString(width / 2, y, stripped)
            y -= line_height

        elif ptype == "Parenthetical":
            indent = left_margin + 160  # shifted ~1 tab further right
            max_chars = int((width - indent - right_margin) // char_width)
            wrapped = textwrap.wrap(stripped, width=max_chars)
            for wline in wrapped:
                c.drawString(indent, y, wline)
                y -= line_height

        elif ptype == "Dialogue":
            indent = left_margin + 100
            max_chars = int((width - indent - right_margin) // char_width)
            wrapped = textwrap.wrap(stripped, width=max_chars)
            for wline in wrapped:
                c.drawString(indent, y, wline)
                y -= line_height

        previous_type = ptype

    c.save()
    return pdf_path