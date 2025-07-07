import os
import base64
import tempfile
import streamlit as st
from openai import OpenAI
from pdf2image import convert_from_path

# --- OpenAI client setup ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not set in environment.")
    st.stop()
client = OpenAI(api_key=api_key)

# --- Utilities ---
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def build_instruction(mode, fields, output_format):
    fmt = output_format.lower()
    if mode == "Manual":
        field_list = ", ".join(fields)
        if fmt == "json":
            return (
                f"Extract all relevant text from the image and structure it as a JSON object "
                f"with the following fields: {field_list}. Return only the JSON."
            )
        elif fmt == "xml":
            return (
                f"Extract all relevant text from the image and structure it as an XML document "
                f"with a root element <document> and the following child elements: {field_list}. "
                f"Return only the XML."
            )
        elif fmt == "markdown":
            return (
                f"Extract all relevant text from the image and structure it as a Markdown document "
                f"with headings for each of the following sections: {field_list}. "
                f"Return only the Markdown."
            )
        elif fmt == "html":
            return (
                f"Extract all relevant text from the image and structure it as an HTML document "
                f"using semantic tags (e.g., headings, paragraphs) for the following sections: {field_list}. "
                f"Return only the HTML."
            )
    else:
        if fmt == "json":
            return (
                "Analyze this image and return the extracted content as a well-structured JSON object. "
                "Guess the most meaningful keys based on the layout. Do not return explanations or plain text."
            )
        elif fmt == "xml":
            return (
                "Analyze this image and return the extracted content as a well-structured XML document "
                "with meaningful tag names based on the layout. Do not return explanations or plain text."
            )
        elif fmt == "markdown":
            return (
                "Analyze this image and return the extracted content formatted as Markdown "
                "using headings and lists based on the content. Do not return explanations or plain text."
            )
        elif fmt == "html":
            return (
                "Analyze this image and return the extracted content formatted as HTML "
                "using semantic tags based on the content. Do not return explanations or plain text."
            )
    raise ValueError(f"Unsupported format: {output_format}")

def process_pdf(pdf_path, instruction, dpi=300):
    images = convert_from_path(pdf_path, dpi=dpi)
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, image in enumerate(images):
            img_path = os.path.join(tmpdir, f"page_{i+1}.png")
            image.save(img_path)

            b64_image = encode_image_to_base64(img_path)
            image_url = f"data:image/png;base64,{b64_image}"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": image_url}}]}
                ],
                max_tokens=2048
            )

            text = response.choices[0].message.content
            results.append((f"Page {i+1}", text))
    
    return results

# --- Streamlit UI ---
st.set_page_config(page_title="PDF Extractor", layout="wide")
st.title("📄 PDF Extractor")

uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

mode = st.radio("Extraction Mode", ["Manual", "Auto"], horizontal=True)

fields = []
if mode == "Manual":
    raw_fields = st.text_input("Enter desired JSON keys (comma-separated)", "name, date, total_amount")
    fields = [f.strip() for f in raw_fields.split(",") if f.strip()]
# Select output format
output_format = st.radio("Output Format", ["JSON", "XML", "Markdown", "HTML"], horizontal=True)

# Only enable the run button when everything's ready
if uploaded_pdf and (mode == "Auto" or fields):
    instruction = build_instruction(mode, fields, output_format)
    st.code(instruction, language="markdown")

    if st.button(f"🔍 Extract {output_format}"):
        with st.spinner("Processing PDF with GPT-4o..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_pdf.read())
                tmp.flush()
                output = process_pdf(tmp.name, instruction)

        st.success("✅ Extraction complete!")

        full_text = ""
        for page_title, text in output:
            with st.expander(page_title):
                st.code(text, language=output_format.lower())
            full_text += f"--- {page_title} ---\n{text}\n\n"

        # Prepare download button with correct format and file extension
        fmt = output_format.lower()
        if fmt not in ["json", "xml", "markdown", "html"]:
            ext = "txt"
            mime = "text/plain"
        else:
            ext = "md" if fmt == "markdown" else fmt
            mime = ("application/json" if ext == "json" else
                    "application/xml" if ext == "xml" else
                    "text/markdown" if ext == "md" else
                    "text/html")
        st.download_button(
            f"📥 Download Extracted {output_format}",
            full_text,
            file_name=f"extracted_output.{ext}",
            mime=mime
        )

