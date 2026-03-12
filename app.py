import streamlit as st
import io
import json
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner_utils.script_requests import RerunData

from main import load_titles, load_prompts, generate_images_for_titles

# --- helpers ----------------------------------------------------------------

def get_image_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def save_titles_to_file(path, titles):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([{"title": t} for t in titles], f, ensure_ascii=False, indent=2)


def remove_title(idx: int):
    """Callback used by delete buttons to remove a specific title.

    Streamlit buttons can behave oddly inside loops, so using ``on_click``
    ensures the correct index is captured when the button is rendered.
    We simply mutate ``st.session_state``; Streamlit will automatically
    rerun the script after the callback finishes, so there's no need to
    call ``st.rerun`` or raise an exception.
    """
    # guard against out-of-range just in case
    if 0 <= idx < len(st.session_state.get("titles", [])):
        st.session_state["titles"].pop(idx)

# --- initialize session state ---------------------------------------------

if "titles" not in st.session_state:
    entries = load_titles("titles.json")
    st.session_state["titles"] = [e.get("title", "") for e in entries]

if "prompt_templates" not in st.session_state:
    st.session_state["prompt_templates"] = load_prompts("prompts.json")

if "prompt_type" not in st.session_state:
    # default to first template key
    st.session_state["prompt_type"] = list(st.session_state["prompt_templates"].keys())[0]

if "prompt_text" not in st.session_state:
    st.session_state["prompt_text"] = st.session_state["prompt_templates"][st.session_state["prompt_type"]]

if "generated" not in st.session_state:
    st.session_state["generated"] = []

# --- page layout -----------------------------------------------------------

st.set_page_config(page_title="AI Blog Header Generator", layout="wide")

# custom styling to mimic Endo blog theme and remove excessive top padding
st.markdown(
    """
    <style>
    /* layout tweaks */
    body, .block-container {padding-top: 2rem;}

    /* expander-as-card appearance */
    .streamlit-expander {
      border: 1px solid #A22A52;
      border-radius: 8px;
      padding: 16px;
      background: white;
      margin-bottom: 16px;
    }
    .streamlit-expanderHeader {
      font-weight: bold;
      color: #A22A52;
    }
    /* hide default arrow */
    .streamlit-expanderHeader:after {display: none;}

    /* card class for non-expander elements (prompt library) */
    .card {
      border: 1px solid #A22A52;
      border-radius: 8px;
      padding: 16px;
      background: white;
      margin-bottom: 16px;
    }

    /* scrollable container for prompt library */
    .scrollable {
      max-height: 400px;
      overflow-y: auto;
      padding-right: 8px;
    }
    
    /* button styling */
    div.stButton > button {
      background-color: #A22A52;
      color: white;
      border: none;
    }
    div.stButton > button:hover {
      background-color: #8C2246;
      color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# header section
st.markdown(
    "<h1 style='text-align:center;color:#A22A52;margin-bottom:1rem;'>AI Blog Header Generator for Endo-Health GmbH</h1>",
    unsafe_allow_html=True,
)

#add a text under the header "Generate unique and eye-catching blog header images based on your titles and style preferences.",
st.markdown(
    "<p style='text-align:center;color:#f00;font-size:18px;margin-bottom:2rem;'>Note: Please be careful when generating images, as they will are very costly.</p>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center;color:#00000;font-size:18px;margin-bottom:2rem;'>The images might not be the highest standard but we can always work on that once we get the detailed requirement from the client</p>",
    unsafe_allow_html=True,
)

# main workspace: two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Prompt Library")
    st.markdown("<div class='scrollable'>", unsafe_allow_html=True)
    for key, template in st.session_state["prompt_templates"].items():
        st.markdown(
            f"<div class='card'><strong>{key}</strong><p>{template}</p></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.subheader("Controls")

    with st.expander("Blog Titles Editor", expanded=True):
        # helper factory to bind index
        def make_remover(idx):
            def remover():
                # pop the title at idx if it still exists
                if 0 <= idx < len(st.session_state.get("titles", [])):
                    st.session_state["titles"].pop(idx)
            return remover

        for i, title in enumerate(st.session_state["titles"]):
            cols = st.columns([0.8, 0.1, 0.1])
            new_title = cols[0].text_input(
                f"Title {i+1}", value=title, key=f"title_{i}"
            )
            st.session_state["titles"][i] = new_title
            cols[1].button(
                "✖",
                key=f"remove_{i}",
                on_click=make_remover(i),
            )

        if st.button("Add Title"):
            st.session_state["titles"].append("")
            raise RerunException(RerunData())
        if st.button("Save Titles to file"):
            save_titles_to_file("blog_titles.json", st.session_state["titles"])
            st.success("Titles saved to blog_titles.json")

    with st.expander("Prompt Style", expanded=True):
        # description above the selector with bolded array; no extra gap
        st.markdown(
            "<p style='margin-bottom:0'>Choose your prompt style "
            "<strong>[Photorealistic, Modern Infographic, 3D Notion]</strong></p>",
            unsafe_allow_html=True,
        )
        prompt_type = st.selectbox(
            "",
            options=list(st.session_state["prompt_templates"].keys()),
            index=list(st.session_state["prompt_templates"].keys()).index(
                st.session_state["prompt_type"]
            ),
        )
        if prompt_type != st.session_state["prompt_type"]:
            st.session_state["prompt_type"] = prompt_type
            st.session_state["prompt_text"] = st.session_state["prompt_templates"][prompt_type]

    with st.expander("Prompt Editor", expanded=True):
        st.session_state["prompt_text"] = st.text_area(
            "Prompt template",
            value=st.session_state.get("prompt_text", ""),
            height=200,
        )

    with st.expander("Generate Images", expanded=True):
        if st.button("Generate Blog Header Images"):
            with st.spinner("Generating images..."):
                st.session_state["generated"] = []
                prompt_templates = {
                    st.session_state["prompt_type"]: st.session_state["prompt_text"]
                }
                results = generate_images_for_titles(
                    [{"title": t} for t in st.session_state["titles"]],
                    st.session_state["prompt_type"],
                    prompt_templates,
                    save_dir=None,
                )
                stored = []
                for img, title, fname in results:
                    stored.append({
                        "bytes": get_image_bytes(img),
                        "title": title,
                        "filename": fname,
                    })
                st.session_state["generated"] = stored
                st.success("Generation complete")

# 3. Image Results Section -------------------------------------------------
if st.session_state["generated"]:
    st.markdown("---")
    st.subheader("Generated Images")
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state["generated"]):
        with cols[idx % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.image(item["bytes"], caption=item["title"], width=300)
            st.download_button(
                label="Download",
                data=item["bytes"],
                file_name=item["filename"],
                mime="image/png",
            )
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.write("No images generated yet. Click the button above to start.")

