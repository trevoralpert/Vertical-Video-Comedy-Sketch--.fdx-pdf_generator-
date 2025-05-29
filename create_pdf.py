from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import textwrap
from fdx_utils import parse_screenplay_blocks

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
    blocks = parse_screenplay_blocks(script_text)

    for ptype, text in blocks:
        if y < bottom_margin:
            c.showPage()
            c.setFont("Courier", 12)
            y = height - top_margin

        if ptype == "Scene Heading":
            max_chars = int((width - left_margin - right_margin) // char_width)
            wrapped = textwrap.wrap(text, width=max_chars)
            for wline in wrapped:
                c.drawString(left_margin, y, wline)
                y -= line_height
            y -= line_height  # Extra space after scene heading

        elif ptype == "Action":
            max_chars = int((width - left_margin - right_margin + 10) // char_width)
            wrapped = textwrap.wrap(text, width=max_chars)
            for wline in wrapped:
                c.drawString(left_margin, y, wline)
                y -= line_height
            y -= line_height  # Extra space after action

        elif ptype == "Character":
            c.drawCentredString(width / 2, y, text)
            y -= line_height
            # No extra space after character

        elif ptype == "Parenthetical":
            indent = left_margin + 160  # shifted ~1 tab further right
            max_chars = int((width - indent - right_margin) // char_width)
            wrapped = textwrap.wrap(text, width=max_chars)
            for wline in wrapped:
                c.drawString(indent, y, wline)
                y -= line_height
            # No extra space after parenthetical

        elif ptype == "Dialogue":
            indent = left_margin + 100
            max_chars = int((width - indent - right_margin) // char_width)
            wrapped = textwrap.wrap(text, width=max_chars)
            for wline in wrapped:
                c.drawString(indent, y, wline)
                y -= line_height
            y -= line_height  # Extra space after dialogue

        elif ptype == "General":
            y -= line_height  # blank line

        elif ptype == "End of Act":
            c.drawCentredString(width / 2, y, text)
            y -= line_height

    c.save()
    return pdf_path