import io
import base64
import requests
from PIL import Image
import streamlit as st

# Streamlit App Config
st.set_page_config(page_title="🎨 Prompt to Image Generator", layout="centered")

# Hugging Face Model Endpoint
DEFAULT_MODEL = "stabilityai/stable-diffusion-2"
API_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{}"

# Load token from Streamlit secrets
try:
    HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]
except KeyError:
    st.error("🚨 Hugging Face token not found. Please add it to Streamlit secrets.")
    st.stop()

# Helper Function
def generate_image(prompt, model, width, height, steps, seed=None):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True},
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": steps,
        },
    }
    if seed:
        payload["parameters"]["seed"] = seed

    response = requests.post(API_URL_TEMPLATE.format(model), headers=headers, json=payload, stream=True, timeout=120)
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.content
    try:
        return Image.open(io.BytesIO(data)).convert("RGB")
    except:
        # If it’s base64 JSON
        result = response.json()
        b64 = None
        if isinstance(result, dict):
            if "images" in result and isinstance(result["images"], list):
                b64 = result["images"][0]
            elif "image" in result:
                b64 = result["image"]
        elif isinstance(result, list) and len(result) > 0:
            b64 = result[0]
        if not b64:
            raise Exception("Unexpected response format")
        return Image.open(io.BytesIO(ba
