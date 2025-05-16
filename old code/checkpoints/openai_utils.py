import os
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import uuid
import tempfile
import zipfile
from pinecone_utils import embed_and_store_script
from fdx_utils import extract_screenplay_text_from_fdx

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_script(prompt: str, temperature: float = 0.8, model: str = "gpt-4"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()

def generate_creative_title(script: str) -> str:
    """
    Uses GPT to create a creative, short sketch title.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a witty sketch comedy writer. Title sketches like viral TikToks or YouTube Shorts."},
            {"role": "user", "content": f"Give me a funny, short title for the following sketch script:\n\n{script}\n\nKeep it under 5 words."}
        ],
        temperature=0.9
    )
    return response.choices[0].message.content.strip().replace('"', '')


def generate_random_topic(temperature: float = 0.9) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a comedy sketch writer. Generate a funny, original topic for a short sketch that would work well on TikTok or Instagram Reels."},
            {"role": "user", "content": "Give me just one random sketch topic idea in one sentence."}
        ],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()



#def create_pdf(sketch_text: str, filename: str) -> str:
#    pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#    c = canvas.Canvas(pdf_path, pagesize=letter)
#    width, height = letter
#    x, y = 40, height - 40

#    for line in sketch_text.splitlines():
#        if y < 50:
#            c.showPage()
#            y = height - 40
#        c.drawString(x, y, line[:110])  # truncate long lines
#        y -= 15

    c.save()
    return pdf_path

def zip_fdx(fdx_path, out_name="sketch_export.zip"):
    zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(fdx_path, arcname=out_name)
    return zip_path

def embed_multiple_fdx(files: list[str]):
    for filepath in files:
        sketch_text = extract_screenplay_text_from_fdx(filepath)
        name = filepath.split("/")[-1].replace(".fdx", "").replace(" ", "_")
        embed_and_store_script(sketch_text, metadata={"source": "reference", "title": name, "text": sketch_text})
        print(f"✅ Embedded: {name}")



