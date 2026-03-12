import os
import json
import shutil
import pytesseract
import requests
import re

from pdf2image import convert_from_path
from PIL import Image
import easyocr

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

from faker import Faker

# ---------------------
# INITIAL SETUP
# ---------------------

app = FastAPI()

UPLOAD_FOLDER = "uploads"
REPORT_FILE = "reports.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

fake = Faker()

reader = easyocr.Reader(['en'])

OLLAMA_URL = "http://localhost:11434/api/generate"

# ---------------------
# SERVE FRONTEND
# ---------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html") as f:
        return f.read()

# ---------------------
# OCR FUNCTION
# ---------------------

def extract_text(file_path):

    text = ""

    if file_path.endswith(".pdf"):

        images = convert_from_path(file_path)

        for img in images:
            text += pytesseract.image_to_string(img)

    else:

        img = Image.open(file_path)

        text += pytesseract.image_to_string(img)

        # only run EasyOCR for images
        result = reader.readtext(file_path)

        for r in result:
            text += " " + r[1]

    return text

# ---------------------
# LLM PHI DETECTION
# ---------------------

def detect_phi(text):

    prompt = f"""
You are an AI system for HIPAA medical de-identification.

Find PHI entities in the text.

Entities:
NAME
PHONE
ADDRESS
EMAIL
DATE
MEDICAL_RECORD
HOSPITAL
DOCTOR

Return ONLY valid JSON like this:

{{
 "entities":[
   {{"type":"NAME","value":"John Smith"}},
   {{"type":"PHONE","value":"987654321"}}
 ]
}}

Text:
{text[:4000]}
"""

    payload = {
        "model": "llama3:latest",
        "prompt": prompt,
        "stream": False
    }

    try:

        r = requests.post(OLLAMA_URL, json=payload)

        response = r.json()["response"]

        # Extract JSON from response safely
        json_match = re.search(r"\{.*\}", response, re.DOTALL)

        if json_match:
            data = json.loads(json_match.group())
            return data.get("entities", [])

        return []

    except Exception as e:

        print("LLM error:", e)
        return []

# ---------------------
# SYNTHETIC DATA
# ---------------------

def fake_data(entity):

    if entity == "NAME":
        return fake.name()

    if entity == "PHONE":
        return fake.phone_number()

    if entity == "ADDRESS":
        return fake.address()

    if entity == "EMAIL":
        return fake.email()

    if entity == "DATE":
        return fake.date()

    return "[REDACTED]"

# ---------------------
# REDACTION
# ---------------------

def redact(text, entities):

    report = {}

    for e in entities:

        val = e.get("value")
        typ = e.get("type")

        if not val:
            continue

        replacement = fake_data(typ)

        # regex-safe replacement
        text = re.sub(re.escape(val), replacement, text)

        report[typ] = report.get(typ, 0) + 1

    return text, report

# ---------------------
# SAVE REPORT
# ---------------------

def save_report(report):

    data = []

    if os.path.exists(REPORT_FILE):

        with open(REPORT_FILE) as f:
            data = json.load(f)

    data.append(report)

    with open(REPORT_FILE, "w") as f:
        json.dump(data, f)

# ---------------------
# DASHBOARD DATA
# ---------------------

def dashboard_stats():

    if not os.path.exists(REPORT_FILE):
        return {}

    with open(REPORT_FILE) as f:

        data = json.load(f)

    stats = {}

    for r in data:

        for k, v in r.items():
            stats[k] = stats.get(k, 0) + v

    return stats

# ---------------------
# PROCESS FILE
# ---------------------

@app.post("/process")
async def process(file: UploadFile = File(...)):

    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(path)

    entities = detect_phi(text)

    print("Detected PHI:", entities)

    redacted, report = redact(text, entities)

    save_report(report)

    return {
        "original": text,
        "redacted": redacted,
        "report": report
    }

# ---------------------
# DASHBOARD
# ---------------------

@app.get("/dashboard")
async def dashboard():
    return dashboard_stats()