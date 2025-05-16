# --- Imports (purely non-Streamlit stuff) ---
import os
import random
from dotenv import load_dotenv

# ✅ DO THIS FIRST: Streamlit import and config
import streamlit as st
st.set_page_config(page_title="Comedy Sketch Writer", page_icon="🎭")

# --- Now it's safe to run setup logic ---
load_dotenv()

# --- App-specific imports (after config) ---
from prompt_builder import build_prompt
from openai_utils import generate_script
from openai_utils import generate_random_topic
from pinecone_utils import fetch_reference_script

import tempfile
import zipfile
import io
from io import StringIO
import base64

from openai_utils import zip_fdx #create_pdf
from pinecone_utils import embed_and_store_script
from fdx_utils import create_fdx, extract_screenplay_text_from_fdx
from fdx_utils import extract_formatted_screenplay_from_fdx, create_pdf
from openai_utils import generate_creative_title
import re

import subprocess

from create_pdf import create_screenplay_pdf

def slugify(title: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', title).strip('_')

# --- Optional CSS (only after set_page_config) ---
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- Topic Input ---
st.subheader("Choose a Topic")

# Initialize topic state
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""
    

if "topic_history" not in st.session_state:
    st.session_state.topic_history = []

if st.session_state.topic_history:
    st.markdown("**🧠 Topic History:**")
    for i, past_topic in enumerate(reversed(st.session_state.topic_history[-5:]), 1):
        st.markdown(f"{i}. {past_topic}")

    if st.button("Clear Topic History"):
        st.session_state.topic_history.clear()

if "saved_sketches" not in st.session_state:
    st.session_state.saved_sketches = []



st.subheader("Creativity Settings")

topic_temperature = st.slider("Random Topic Creativity", 0.0, 1.0, value=0.9, step=0.1)
script_temperature = st.slider("Sketch Script Creativity", 0.0, 1.0, value=0.8, step=0.1)


# Button to get a GPT-generated topic
if st.button("Pick a Random Topic"):
    with st.spinner("Thinking of something funny..."):
        new_topic = generate_random_topic(topic_temperature)
        st.session_state.selected_topic = new_topic
        st.session_state.topic_history.append(new_topic)


# Allow editing topic manually (with fallback to session state)
topic = st.text_input("Enter a topic for the sketch:", value=st.session_state.selected_topic)



# --- Duration Slider (in seconds) ---
st.subheader("Sketch Duration")
duration_seconds = st.slider("How long should the sketch be?", min_value=10, max_value=90, value=30)

# --- Character Selection ---
st.subheader("Characters")
characters = []
if st.checkbox("Include Zach"):
    characters.append("ZACH")
if st.checkbox("Include Pally"):
    characters.append("PALLY")
if st.checkbox("Include Trevor"):
    characters.append("TREVOR")

if "custom_characters" not in st.session_state:
    st.session_state.custom_characters = []

st.subheader("Add Custom Character")
with st.form("add_character_form", clear_on_submit=True):
    new_name = st.text_input("Character Name")
    new_desc = st.text_input("Brief Description (optional)")
    submitted = st.form_submit_button("Add Character")
    if submitted and new_name:
        st.session_state.custom_characters.append({
            "name": new_name.upper(),
            "desc": new_desc
        })
        st.success(f"{new_name} added!")

# Show existing characters with checkboxes
for char in st.session_state.custom_characters:
    if st.checkbox(f"Include {char['name']}"):
        characters.append(char['name'])


# Optional preview
st.markdown(f"**Selected Topic**: `{topic}`")
st.markdown(f"**Duration**: `{duration_seconds} seconds`")
st.markdown(f"**Characters**: `{', '.join(characters) or 'None selected'}`")

reference_script = fetch_reference_script("comedy sketch")
reference_script = extract_formatted_screenplay_from_fdx("Don't threaten me.fdx")

if st.button("Generate Sketch"):
    if topic and topic not in st.session_state.topic_history:
        st.session_state.topic_history.append(topic)
    
    reference_script = fetch_reference_script("comedy sketch")
    prompt = build_prompt(topic, characters, duration_seconds, reference_script)
    generated_script = generate_script(prompt, temperature=script_temperature)
    title = generate_creative_title(generated_script)
    st.session_state.last_generated_script = generated_script
    st.session_state.last_generated_title = title
    st.subheader("🎬 Generated Script")
    st.text_area("Screenplay Output", generated_script, height=400)


script_to_show = st.session_state.get("last_generated_script", "")


if st.button("Regenerate with Same Topic"):
    if topic and topic not in st.session_state.topic_history:
        st.session_state.topic_history.append(topic)

    reference_script = fetch_reference_script("comedy sketch")
    prompt = build_prompt(topic, characters, duration_seconds, reference_script)
    generated_script = generate_script(prompt, temperature=script_temperature)
    st.session_state.last_generated_script = generated_script  # Save for export
    st.subheader("🎬 Regenerated Script")
    st.text_area("Screenplay Output", generated_script, height=400)
    

if st.session_state.get("last_generated_title"):
    st.subheader("🎬 Sketch Title")
    st.markdown(f"**{st.session_state.last_generated_title}**")

# Save button
if script_to_show:
    if st.button("Save This Sketch"):
        title = st.session_state.get("last_generated_title", "Untitled_Sketch")
        st.session_state.saved_sketches.append({
            "topic": title,
            "script": script_to_show
        })
        st.success(f"Sketch saved as: {title}")

# Display all saved sketches
if st.session_state.saved_sketches:
    st.subheader("💾 Saved Sketches")
    for i, sketch in enumerate(reversed(st.session_state.saved_sketches), 1):
        sketch_index = len(st.session_state.saved_sketches) - i
        title = sketch["topic"]
        script = sketch["script"]
        filename = slugify(title)

        col1, col2 = st.columns([5, 1])
        with col1:
            with st.expander(f"{i}. {title}"):
                st.code(script, language="markdown")

                # Download buttons
                buffer = StringIO()
                buffer.write(script)
                txt_data = buffer.getvalue()

                st.download_button("📥 Download as .txt", txt_data, f"{filename}.txt", mime="text/plain")

                pdf_path = create_screenplay_pdf(script, f"{filename}.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download as PDF", f.read(), f"{filename}.pdf", mime="application/pdf")


                #pdf_path = create_pdf(script, f"{filename}.pdf")
                #with open(pdf_path, "rb") as f:
                #    st.download_button("📄 Download as PDF", f.read(), f"{filename}.pdf", mime="application/pdf")

                fdx_path = create_fdx(script, f"{filename}.fdx")
                with open(fdx_path, "rb") as f:
                    st.download_button("🎬 Download as Final Draft (.fdx)", f.read(), f"{filename}.fdx", mime="application/octet-stream")

        with col2:
            if st.button("🗑️", key=f"delete_{i}"):
                st.session_state.saved_sketches.pop(sketch_index)
                st.rerun()

# ZIP export (outside the loop)
def export_all_sketches(sketches: list[dict]) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for sketch in sketches:
            name = sketch['topic'].replace(" ", "_")
            script = sketch['script']

            zipf.writestr(f"{name}.txt", script)
            pdf_path = create_screenplay_pdf(script, f"{name}.pdf")
            zipf.write(pdf_path, arcname=f"{name}.pdf")
            fdx_path = create_fdx(script, f"{name}.fdx")
            zipf.write(fdx_path, arcname=f"{name}.fdx")
    return zip_buffer.getvalue()

if st.session_state.saved_sketches:
    zip_data = export_all_sketches(st.session_state.saved_sketches)
    latest_title = st.session_state.saved_sketches[-1]["topic"] if st.session_state.saved_sketches else "sketch_bundle"
    slugged_title = slugify(latest_title)
    st.download_button(
        label="📦 Download all file types",
        data=zip_data,
        file_name=f"{slugged_title}.zip",
        mime="application/zip"
    )


uploaded = st.file_uploader("Upload a Final Draft (.fdx) sketch to add to the library", type=["fdx"])
if uploaded:
    with open("temp_uploaded.fdx", "wb") as f:
        f.write(uploaded.read())
    sketch_text = extract_screenplay_text_from_fdx("temp_uploaded.fdx")
    embed_and_store_script(sketch_text, metadata={"source": "reference", "title": uploaded.name, "text": sketch_text})
    st.success(f"✅ Embedded: {uploaded.name}")
