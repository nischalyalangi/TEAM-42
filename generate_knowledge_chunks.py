import os
import re
import uuid
import json
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text

RAW = r"C:\TEAM-42\knowledge_raw"
OUT = r"C:\TEAM-42\knowledge_processed"

os.makedirs(OUT, exist_ok=True)

def clean_text(txt):
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def html_to_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        text = soup.get_text(separator="\n")
    return clean_text(text)

def pdf_to_text(file_path):
    text = extract_text(file_path)
    return clean_text(text)

all_text = ""

for fname in os.listdir(RAW):
    path = os.path.join(RAW, fname)
    if fname.endswith(".html"):
        txt = html_to_text(path)
        print("Extracted HTML:", fname)
    elif fname.endswith(".pdf"):
        txt = pdf_to_text(path)
        print("Extracted PDF:", fname)
    elif fname.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            txt = clean_text(f.read())
        print("Loaded TXT:", fname)
    else:
        continue

    # Save clean text
    with open(os.path.join(OUT, f"{fname}.clean.txt"), "w", encoding="utf-8") as f:
        f.write(txt)

    all_text += txt + "\n\n"

print("\nExtraction Complete")
