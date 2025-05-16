import tempfile
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from lxml import etree as ET
import tempfile

def create_fdx(script_text: str, filename: str) -> str:
    from fdx_utils import parse_screenplay_blocks

    tree = ET.parse("Don't threaten me.fdx")  # use your real template
    root = tree.getroot()
    content = root.find("Content")

    for child in list(content):
        content.remove(child)

    blocks = parse_screenplay_blocks(script_text)

    for ptype, text in blocks:
        p = ET.SubElement(content, "Paragraph", Type=ptype)
        if ptype == "Dialogue":
            for style, chunk in apply_inline_styles(text):
                t = ET.SubElement(p, "Text")
                if style:
                    t.set("Style", style)
                t.text = chunk
        else:
            t = ET.SubElement(p, "Text")
            t.text = text

    fdx_path = tempfile.NamedTemporaryFile(delete=False, suffix=".fdx").name
    tree.write(fdx_path, encoding="utf-8", xml_declaration=True)
    return fdx_path


def extract_screenplay_text_from_fdx(filepath: str) -> str:
    tree = ET.parse(filepath)
    root = tree.getroot()
    content = root.find("Content")
    if content is None:
        return ""

    lines = []
    for paragraph in content.findall("Paragraph"):
        ptype = paragraph.attrib.get("Type", "Action")
        text = paragraph.text or ""
        if ptype == "Scene Heading":
            lines.append(text)
        elif ptype == "Character":
            lines.append(text.upper())
        elif ptype == "Parenthetical":
            lines.append(f"({text})")
        elif ptype == "Dialogue":
            lines.append(text)
        elif ptype == "Action":
            lines.append(text)
        elif ptype == "General":
            lines.append("")
    return "\n".join(lines)

def extract_formatted_screenplay_from_fdx(filepath: str) -> str:
    tree = ET.parse(filepath)
    root = tree.getroot()
    content = root.find("Content")
    if content is None:
        return ""

    lines = []
    for paragraph in content.findall("Paragraph"):
        ptype = paragraph.attrib.get("Type", "Action")
        text = (paragraph.text or "").strip()

        if ptype == "Scene Heading":
            lines.append(text)  # flush left
        elif ptype == "Character":
            lines.append(f"{text.center(60)}")  # centered
        elif ptype == "Parenthetical":
            lines.append(f"{text.center(45)}")  # slightly indented center
        elif ptype == "Dialogue":
            lines.append(f"{text.rjust(20)}")  # fake margin left
        elif ptype == "Action":
            lines.append(text)  # flush left
        elif ptype == "General":
            lines.append("")

    return "\n\n".join(lines)

def parse_screenplay_blocks(script_text: str) -> list[tuple[str, str]]:
    """
    Smarter screenplay parser that handles multiline dialogue and parentheticals.
    """
    lines = script_text.splitlines()
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            blocks.append(("General", ""))
            i += 1
            continue

        if line.startswith("INT.") or line.startswith("EXT."):
            blocks.append(("Scene Heading", line))
            i += 1
            continue

        if line.upper() == line and len(line.split()) <= 4:
            # It's a character name
            blocks.append(("Character", line))
            i += 1

            # Check for optional parenthetical
            if i < len(lines) and lines[i].strip().startswith("(") and lines[i].strip().endswith(")"):
                blocks.append(("Parenthetical", lines[i].strip()))
                i += 1

            # Accumulate dialogue lines until next paragraph
            dialogue_lines = []
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line.upper() == next_line and len(next_line.split()) <= 4:
                    break
                dialogue_lines.append(next_line)
                i += 1

            if dialogue_lines:
                blocks.append(("Dialogue", " ".join(dialogue_lines)))
            continue

        elif line.startswith("(") and line.endswith(")"):
            blocks.append(("Parenthetical", line))
        else:
            blocks.append(("Action", line))

        i += 1

    return blocks



def apply_inline_styles(text: str) -> list[tuple[str, str]]:
    """Parses *italic* text and returns list of (style, text) chunks."""
    import re
    parts = []
    tokens = re.split(r"(\*.*?\*)", text)
    for token in tokens:
        if token.startswith("*") and token.endswith("*"):
            parts.append(("Italic", token[1:-1]))
        else:
            parts.append(("", token))
    return parts


def create_pdf(script_text: str, filename: str) -> str:
    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    blocks = parse_screenplay_blocks(script_text)
    y = height - inch  # Start 1 inch from the top

    def draw_wrapped(text, x_start, y_pos, max_width, font="Courier", size=12, leading=14):
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, font, size) <= max_width:
                line = test_line
            else:
                c.drawString(x_start, y_pos, line)
                y_pos -= leading
                line = word
        if line:
            c.drawString(x_start, y_pos, line)
            y_pos -= leading
        return y_pos

    for ptype, text in blocks:
        if y < inch:  # New page margin
            c.showPage()
            y = height - inch

        if ptype == "Scene Heading":
            c.setFont("Courier", 12)
            y = draw_wrapped(text.upper(), inch, y, width - 2 * inch)
        elif ptype == "Action":
            c.setFont("Courier", 12)
            y = draw_wrapped(text, inch, y, width - 2 * inch)
        elif ptype == "Character":
            c.setFont("Courier", 12)
            c.drawCentredString(width / 2, y, text.upper())
            y -= 14
        elif ptype == "Parenthetical":
            c.setFont("Courier", 12)
            cleaned = text.strip("()")  # Remove outer parentheses if present
            y = draw_wrapped(f"({cleaned})", width / 2.5, y, width / 2.5)
        elif ptype == "Dialogue":
            c.setFont("Courier", 12)
            # Tighter margins than action
            y = draw_wrapped(text, inch + 1.0 * inch, y, width - 3.5 * inch)
        elif ptype == "General":
            y -= 14  # blank line

    c.save()
    return pdf_path