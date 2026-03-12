# AI Blog Header Generator

## Introduction

This repository contains a Streamlit application that generates AI‑powered header images
for medical blog articles based on their titles. The goal is to automatically produce
visually consistent blog headers that align with the branding of the Endo Blog
website. Users provide a list of titles and choose a style; the app then constructs
prompts and sends them to OpenAI's image‑generation models.

![App Screenshot](path-to-image)

## Features

- Automatic generation of blog header images
- Multiple visual styles for image generation (photorealistic, modern infographic, 3D, etc.)
- Editable prompt templates stored in `prompts.json`
- Editable blog title list via the UI or JSON file
- Interactive Streamlit interface with two‑column dashboard layout
- Image preview grid with captions and download buttons
- Consistent healthcare‑themed visual style matching Endo Blog

## Current Limitation

Due to API cost limitations during development, the app currently generates **only
5 images per run**. This restriction exists in the demo but can be easily relaxed
or removed for a production deployment.

## Customization

All prompt texts are stored in `prompts.json` and may be adjusted to better match
company branding, messaging, or design requirements. The Streamlit UI also allows
you to edit the prompt before each generation.

## Deployment

The application is temporarily deployed using Streamlit for demonstration purposes.
The project is architected in a way that makes it straightforward to migrate the
backend to a production environment (e.g. containerization, serverless functions,
or integrated into an existing web platform) with minimal changes.

## How to Run the App Locally

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```
2. Install dependencies (listed in `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```
3. Add your OpenAI API key to a `.env` file at the project root:
   ```text
   OPENAI_API_KEY=sk-...
   ```
4. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Example Commands

```bash
git clone <repo-url>
cd <repo-folder>
pip install -r requirements.txt
streamlit run app.py
```