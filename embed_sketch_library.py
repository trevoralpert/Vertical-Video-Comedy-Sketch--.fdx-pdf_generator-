from fdx_utils import extract_screenplay_text_from_fdx
from pinecone_utils import embed_and_store_script


def embed_multiple_fdx(files: list[str]):
    for filepath in files:
        sketch_text = extract_screenplay_text_from_fdx(filepath)
        name = filepath.split("/")[-1].replace(".fdx", "").replace(" ", "_")
        embed_and_store_script(sketch_text, metadata={"source": "reference", "title": name, "text": sketch_text})
        print(f"✅ Embedded: {name}")

embed_multiple_fdx([
    "reference_scripts/dont_threaten_me.fdx",
    "reference_scripts/breakup_by_owl.fdx",
    "reference_scripts/barbershop_time_travel.fdx"
])