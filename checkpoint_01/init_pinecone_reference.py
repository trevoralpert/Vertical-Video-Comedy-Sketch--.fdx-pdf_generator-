# init_pinecone_reference.py

from pinecone_utils import embed_and_store_script
from openai_utils import extract_screenplay_text_from_fdx

# Paste your screenplay-formatted text here, or load it from a file
reference_script = extract_screenplay_text_from_fdx("Don't threaten me.fdx")


# Call the embedding + store function
embed_and_store_script(reference_script, metadata={"source": "reference", "text": reference_script})
