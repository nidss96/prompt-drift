# app.py
import streamlit as st
from PIL import Image
from io import BytesIO
import requests
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
#API_KEY = os.getenv("NEBIUS_API_KEY") or st.secrets.get("NEBIUS_API_KEY")
API_KEY=os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
)

TEXT2IMAGE_MODEL = "dall-e-3"
MULTIMODAL_LLM_MODEL = "gpt-4o"

# Utility functions
def generate_image_from_text(prompt):
    response = client.images.generate(
        model=TEXT2IMAGE_MODEL,
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="b64_json"
    )
    image_b64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_b64)
    return Image.open(BytesIO(image_bytes))#.convert("RGB")

def describe_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_b64 = base64.b64encode(buffered.getvalue()).decode()
    response = client.chat.completions.create(
        model=MULTIMODAL_LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ]
            }
        ]
    )
    return response.choices[0].message.content.strip()

def load_image_from_url(url):
    return Image.open(BytesIO(requests.get(url).content)).convert("RGB")

def run_prompt_drift(starting_prompt=None, starting_image=None, n_rounds=3):
    assert (starting_prompt is not None) ^ (starting_image is not None), "Provide exactly one of `starting_prompt` or `starting_image`"
    history = []
    if starting_prompt:
        current_text = starting_prompt
        for _ in range(n_rounds):
            image = generate_image_from_text(current_text)
            history.append(("text", current_text))
            history.append(("image", image))
            current_text = describe_image(image)
    else:
        current_image = starting_image
        history.append(("image", current_image))
        for _ in range(n_rounds):
            text = describe_image(current_image)
            history.append(("text", text))
            current_image = generate_image_from_text(text)
            history.append(("image", current_image))
    return history

def visualize_history(history):
    round_num = 1
    i = 0
    n = len(history)
    while i < n - 1:
        mode1, content1 = history[i]
        mode2, content2 = history[i + 1]
        if mode1 == "text" and mode2 == "image":
            st.subheader(f"Round {round_num} - Text")
            st.markdown(content1)
            st.subheader(f"Round {round_num} - Image")
            st.image(content2)
        elif mode1 == "image" and mode2 == "text":
            st.subheader(f"Round {round_num} - Image")
            st.image(content1)
            st.subheader(f"Round {round_num} - Text")
            st.markdown(content2)
        else:
            st.error("Unexpected history structure.")
        round_num += 1
        i += 2

# Streamlit UI
st.title("🌀 Prompt Drift - Text ↔ Image")

MAX_ROUNDS = 5
if "round_count" not in st.session_state:
    st.session_state.round_count = 0

st.sidebar.header("Session Controls")
st.sidebar.markdown(f"Rounds used: {st.session_state.round_count}/{MAX_ROUNDS}")
if st.sidebar.button("Reset Usage"):
    st.session_state.round_count = 0
    st.sidebar.success("Session usage reset.")

mode = st.radio("Choose starting point:", ["Text prompt", "Image (Upload or URL)"])
n_rounds = st.slider("Number of rounds", 1, MAX_ROUNDS, 2)

if st.session_state.round_count >= MAX_ROUNDS:
    st.warning("You’ve reached the maximum number of rounds for this session.")
else:
    if mode == "Text prompt":
        prompt = st.text_input("Enter starting text:")
        if st.button("Run from text"):
            if prompt:
                with st.spinner("Running game..."):
                    history = run_prompt_drift(starting_prompt=prompt, n_rounds=n_rounds)
                    visualize_history(history)
                    st.session_state.round_count += n_rounds
            else:
                st.warning("Please enter a prompt.")

    else:
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        image_url = st.text_input("Or enter an image URL:")

        if st.button("Run from image"):
            if uploaded_file:
                try:
                    image = Image.open(uploaded_file).convert("RGB")
                    with st.spinner("Running game..."):
                        history = run_prompt_drift(starting_image=image, n_rounds=n_rounds)
                        visualize_history(history)
                        st.session_state.round_count += n_rounds
                except Exception as e:
                    st.error(f"Failed to read uploaded image: {e}")

            elif image_url:
                try:
                    image = load_image_from_url(image_url)
                    with st.spinner("Running game..."):
                        history = run_prompt_drift(starting_image=image, n_rounds=n_rounds)
                        visualize_history(history)
                        st.session_state.round_count += n_rounds
                except Exception as e:
                    st.error(f"Failed to load image from URL: {e}")
