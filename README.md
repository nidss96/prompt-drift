# Prompt Drift

**Prompt Drift** is an interactive Streamlit app that explores how meaning evolves between text and images over multiple rounds of transformations.

Starting with either a text prompt or an image, the app alternates between generating an image from text and describing that image using a multimodal language model. The result is a fascinating "drift" in content between AI models.

---

## Features

- Start with a **text prompt** or an **image**
- Uses **OpenAI's DALL·E 3** to generate images
- Uses **GPT-4o** to describe images in text
- Watch how concepts shift over time through repeated generations

## Model Details

By default, this app uses the following models from OpenAI:

- **Image generation**: [`dall-e-3`](https://platform.openai.com/docs/guides/images) — to convert text prompts into images
- **Image description**: [`gpt-4o`](https://platform.openai.com/docs/guides/vision) — a multimodal model that can interpret image content

However, the app is modular and can be adapted to use **any provider** (e.g., Hugging Face) that supports:
- A **text-to-image generation** endpoint
- A **multimodal LLM** that can accept and describe images

---

## Setup Instructions

1. **Clone the repository**
```bash
   git clone https://github.com/YOUR_USERNAME/prompt-drift.git
   cd prompt-drift
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**

Create a .env file in the root directory:
```bash
OPENAI_API_KEY=your-api-key-here
```

##  How to Run

From the root folder of the project, run:
```bash
streamlit run app.py
```
This will launch the app in your browser.
