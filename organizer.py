import os
import shutil
import requests
import pdfplumber

FOLDER_PATH = "messyFolder"


def extract_pdf_text(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except:
        return ""

    return text[:1000]  


def classify_file(file_path):
    filename = os.path.basename(file_path)

    
    content = ""
    if filename.lower().endswith(".pdf"):
        content = extract_pdf_text(file_path)

    if not content:
        content = "No readable content"

    prompt = f"""
    Classify this file into one category:
    Finance, Study, Work, Personal, Code, Images, Others

    File name: {filename}

    Content:
    {content}

    Rules:
    - If invoice, bill, receipt → Finance
    - If assignment, notes, university → Study
    - If resume, project, report → Work
    - If code (.py, .js) → Code
    - If image → Images
    - If unclear → Others

    Only return the category name.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()["response"].strip().split()[0]

   
    allowed = ["Finance", "Study", "Work", "Personal", "Code", "Images", "Others"]
    if result not in allowed:
        result = "Others"

    return result



def organize_folder():
    print("🤖 AI Folder Organizer Started...\n")

    for file in os.listdir(FOLDER_PATH):
        file_path = os.path.join(FOLDER_PATH, file)

        if os.path.isfile(file_path):
            print(f"📂 Processing: {file}")

            category = classify_file(file_path)
            print(f"👉 Category: {category}")

            category_path = os.path.join(FOLDER_PATH, category)

        
            os.makedirs(category_path, exist_ok=True)

            
            new_path = os.path.join(category_path, file)
            shutil.move(file_path, new_path)

            print(f"✅ Moved → {category}/{file}\n")


if __name__ == "__main__":
    organize_folder()