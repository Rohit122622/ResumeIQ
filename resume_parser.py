import spacy
import pdfplumber
import re
import os

nlp = spacy.load("en_core_web_sm")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match[0] if match else ""

def extract_phone(text):
    match = re.findall(r"\b\d{10}\b", text)
    return match[0] if match else ""

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_skills(text):
    skills = []
    skill_path = os.path.join(BASE_DIR, "data", "skills.txt")

    if not os.path.exists(skill_path):
        return skills

    with open(skill_path, "r", encoding="utf-8") as f:
        skill_list = f.read().splitlines()

    text = text.lower()
    for skill in skill_list:
        if skill.lower() in text:
            skills.append(skill)

    return list(set(skills))


def parse_resume(path):
    text = extract_text(path)

    data = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "text": text 
    }

    return data
