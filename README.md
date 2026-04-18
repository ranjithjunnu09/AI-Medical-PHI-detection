AI-Powered HIPAA Medical De-identification System
Overview

Healthcare organizations handle vast amounts of unstructured medical data such as:

Clinical notes

Discharge summaries

Medical reports

Scanned doctor notes

These documents contain Protected Health Information (PHI) such as:

Patient names

Phone numbers

Addresses

Medical record numbers

Hospital information

To comply with HIPAA regulations, PHI must be detected and removed before the data can be used for:

Medical research

AI training

Data analytics

This project implements an AI-powered automated de-identification system that:

Detects PHI using a local LLM

Redacts or replaces sensitive data

Supports OCR for scanned documents

Provides a simple web interface

Runs fully containerized using Docker Compose

The goal was to build a functional prototype of an Automated HIPAA De-identification System that:

Detects PHI in medical documents

Redacts or anonymizes sensitive information

Supports both raw text and scanned documents

Provides an audit trail of removed PHI

Runs fully containerized using Docker Compose

System Architecture
                +----------------------+
                |      Web Browser     |
                |  Upload Medical File |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      FastAPI API     |
                |  File Upload Server  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |     OCR Pipeline     |
                | Tesseract + Poppler  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Text Extraction    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |     Ollama LLM       |
                |  PHI Entity Detection|
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Redaction Engine   |
                | Synthetic Data Gen   |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | Compliance Dashboard |
                | Redaction Report     |
                +----------------------+
Tech Stack
Backend

Python

FastAPI – high performance API framework

Uvicorn – ASGI server

AI / NLP

Ollama LLM (Local)
Used to detect PHI entities from extracted text.

Model used:

phi

Other supported models:

llama3

mistral

gemma

OCR Pipeline

To support scanned documents:

Tesseract OCR

Poppler (PDF to Image conversion)

Pillow

Pipeline:

PDF → Image → OCR → Extracted Text
PHI Redaction

Redaction strategy includes:

Synthetic data replacement

Context preservation

Regex-safe replacements

Example:

Patient Name: John Doe
Phone: 9876543210

After de-identification:

Patient Name: Michael Carter
Phone: 555-392-1821

Synthetic values generated using:

Faker Library
PHI Entities Detected

The system detects the following HIPAA identifiers:

Patient Names

Phone Numbers

Email Addresses

Physical Addresses

Dates

Medical Record Numbers

Hospital Names

Doctor Names

Example detection output:

{
 "entities":[
   {"type":"NAME","value":"John Smith"},
   {"type":"PHONE","value":"987654321"}
 ]
}
Features
PHI Detection

AI-based entity detection using LLM reasoning.

OCR Support

Supports:

PDF medical documents

Image scans

Digital clinical text

Synthetic Data Generation

Instead of simple redaction:

[PATIENT_NAME]

The system replaces with realistic data:

Michael Johnson

This preserves clinical context.

Redaction Report

The system produces an audit report:

{
  "NAME": 2,
  "PHONE": 1,
  "EMAIL": 1
}
Compliance Dashboard

Shows statistics across uploaded files.

Example:

Detected PHI Types

NAME: 10
PHONE: 4
EMAIL: 3
ADDRESS: 2
Frontend

A simple UI allows:

Upload medical files

View original vs redacted output

Monitor PHI detection statistics

Interface:

Upload Document
      |
      v
Original Text | Redacted Text
Docker Deployment

The entire system is containerized using Docker Compose.

Services:

backend (FastAPI)
ollama (LLM server)
Project Structure
AI-Medical-PHI-detection
│
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
│
├── frontend
│   └── index.html
│
├── uploads
└── reports.json
Setup Guide
Option 1: Run Locally
Install dependencies
pip install -r requirements.txt
Start Ollama
ollama serve
Pull model
ollama pull phi
Run backend
uvicorn main:app --reload

Open:

http://localhost:8000
Option 2: Run with Docker

Build containers:

docker compose build

Start the system:

docker compose up

Pull model inside container:

docker exec -it ollama ollama pull phi

Open:

http://localhost:8000
Example Workflow

Upload medical document

OCR extracts text

LLM detects PHI entities

Redaction engine replaces sensitive data

Dashboard shows PHI statistics

Implementation Design
Model Choice

We used Ollama with the Phi model because:

Runs locally

No API cost

Good reasoning for entity detection

Fast inference

OCR Strategy

The system uses:

Poppler → convert PDF to images
Tesseract → extract text

This allows processing of:

scanned clinical documents

handwritten notes (basic support)

Context Preservation

Instead of removing PHI entirely:

[REDACTED]

The system replaces values using synthetic data generation.

This ensures:

readability

clinical meaning preservation

realistic anonymized datasets

Bonus Features Implemented

Synthetic Data Generation

OCR pipeline for scanned documents

Compliance dashboard

Docker Compose deployment

Local LLM inference using Ollama

Future Improvements

Handwritten OCR model integration

PHI highlighting in UI

Support for batch document processing

Redis queue for async processing

GPU acceleration
