import PyPDF2
import re
import string

def extract_text_from_pdf(pdf_file):
    """
    Extracts raw text from PDF.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text.strip()
    except Exception:
        return ""

def clean_text_for_matching(text):
    """
    Normalize text: lowercase, remove punctuation, remove extra spaces (#1 Upgrade).
    """
    if not text:
        return ""
    
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Remove punctuation (using string.punctuation)
    # We replace punctuation with space to avoid merging words incorrectly
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    
    # 3. Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
