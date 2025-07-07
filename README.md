

# 📄 PDF Extractor with GPT-4o

A Streamlit app to extract structured content (JSON, XML, Markdown, or HTML) from PDF files using OpenAI's `gpt-4o`. Convert scanned or digital PDFs into well-formatted structured data by leveraging GPT-4o's vision capabilities.

---

## 🚀 Features

* 🔍 Extract content from PDFs using GPT-4o (image-to-text)
* 🧠 **Auto Mode**: Let GPT infer fields and structure based on content
* ✍️ **Manual Mode**: Specify exact fields (e.g., `name`, `date`, `total_amount`)
* 📤 Output formats supported: **JSON**, **XML**, **Markdown**, **HTML**
* 🖼️ Converts each PDF page to an image and sends it to GPT-4o for parsing
* 💾 Download the extracted output in the chosen format

---

## 🛠️ Requirements

* Python 3.8+
* OpenAI API key (`OPENAI_API_KEY` in environment)

### Install dependencies

```bash
pip install streamlit openai pdf2image
```

You may also need to install poppler for `pdf2image`:

**Ubuntu/Debian:**

```bash
sudo apt-get install poppler-utils
```

**macOS (Homebrew):**

```bash
brew install poppler
```

---

## 🔑 Setup

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

This will launch the app in your browser.

---

## 🧪 How It Works

1. Upload a PDF.
2. Choose an **Extraction Mode**:

   * **Auto**: GPT guesses the structure.
   * **Manual**: You provide specific keys or sections.
3. Choose an **Output Format**: JSON, XML, Markdown, or HTML.
4. Click **Extract** and let GPT-4o process each page.
5. View per-page extracted content and download the full output.

---

