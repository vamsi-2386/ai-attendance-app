import os
import requests
import numpy as np
from PIL import Image
from io import BytesIO
import sys
sys.path.append(os.path.dirname(__file__))

from src.database.db import create_company, create_subject, create_employee, assign_employee_to_project
from src.pipelines.face_pipeline import get_face_embeddings

from PIL import Image
import io

def download_image(url, save_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    img = Image.open(io.BytesIO(response.content))
    img = img.resize((400, 400)) # Resize to prevent any OOM or dlib stride issues
    img = img.convert('RGB')
    img.save(save_path)
    # Return exactly what st.camera_input does: np.array(Image.open(file))
    return np.array(Image.open(save_path))

def main():
    print("Setting up dummy data...")
    
    # Create folder for photos
    photos_dir = os.path.join(os.path.dirname(__file__), "employee_photos")
    os.makedirs(photos_dir, exist_ok=True)
    
    # 1. Create a company
    print("Creating company...")
    from src.database.db import check_company_exists
    from src.database.config import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not check_company_exists("techtitans"):
        company = create_company("techtitans", "password123", "Tech Titans Inc")
    
    cursor.execute("SELECT id, company_invite_code FROM companys WHERE username='techtitans'")
    row = cursor.fetchone()
    company_id = row['id']
    invite_code = row['company_invite_code']
    print(f"Company ready! Invite Code: {invite_code}")
    
    # 2. Create a project
    print("Creating project...")
    cursor.execute("INSERT INTO subjects (subject_code, name, section, company_id) VALUES (?, ?, ?, ?)",
                   ("PRJ-001", "Billionaires Club", "A", company_id))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 3. Download and register Bill Gates
    print("Registering Bill Gates...")
    bill_url = "https://upload.wikimedia.org/wikipedia/commons/a/a0/Bill_Gates_2018.jpg"
    bill_path = os.path.join(photos_dir, "bill_gates.jpg")
    bill_img = download_image(bill_url, bill_path)
    bill_encodings = get_face_embeddings(bill_img)
    if bill_encodings:
        emp = create_employee("EMP-001", "Bill Gates", company_id, face_embedding=bill_encodings[0].tolist())
        assign_employee_to_project(emp[0]['employee_id'], project_id)
        print("Bill Gates registered successfully!")
    else:
        print("Failed to get Bill Gates encodings!")
    
    # 4. Download and register Elon Musk
    print("Registering Elon Musk...")
    elon_url = "https://upload.wikimedia.org/wikipedia/commons/c/cb/Elon_Musk_Royal_Society_crop.jpg"
    elon_path = os.path.join(photos_dir, "elon_musk.jpg")
    elon_img = download_image(elon_url, elon_path)
    elon_encodings = get_face_embeddings(elon_img)
    if elon_encodings:
        emp = create_employee("EMP-002", "Elon Musk", company_id, face_embedding=elon_encodings[0].tolist())
        assign_employee_to_project(emp[0]['employee_id'], project_id)
        print("Elon Musk registered successfully!")
    else:
        print("Failed to get Elon Musk encodings!")
        
    print("Dummy data seeding complete! You can log in with username 'techtitans' and password 'password123'.")
    print(f"Photos are saved in {photos_dir}")

if __name__ == "__main__":
    main()
