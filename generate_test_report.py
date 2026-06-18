import os
import sys
import numpy as np
from PIL import Image
import pandas as pd

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pipelines.face_pipeline import predict_attendance
from src.database.db import get_all_employees

def generate_report(test_dir="test_images", threshold=0.6): # Threshold arg kept for backward compat, though face_pipeline uses fixed thresholds internally now
    if not os.path.exists(test_dir):
        print(f"Test directory '{test_dir}' not found. Please create it and add test images.")
        return

    print("Generating face match test report using Cosine Similarity thresholds...")
    employees = get_all_employees()
    if not employees:
        print("No enrolled employees found. Please enroll some employees first.")
        return

    results = []
    
    for filename in os.listdir(test_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(test_dir, filename)
            try:
                img = np.array(Image.open(filepath).convert('RGB'))
                # For testing, we might want to disable liveness so we can use static photos
                detected, all_ids, num_faces = predict_attendance(img, enforce_liveness=False)
                
                matched_id = list(detected.keys())[0] if detected else None
                
                if matched_id:
                    matched_name = next((e['name'] for e in employees if e['employee_id'] == matched_id), "Unknown")
                    similarity_score = detected[matched_id]['similarity_score']
                    decision = detected[matched_id]['decision']
                else:
                    matched_name = "None"
                    similarity_score = 0.0
                    decision = "Rejected"
                
                results.append({
                    "Image": filename,
                    "Faces Detected": num_faces,
                    "Matched Employee ID": matched_id,
                    "Matched Name": matched_name,
                    "Similarity Score": similarity_score,
                    "Decision": decision
                })
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if results:
        df = pd.DataFrame(results)
        report_path = "face_match_report.csv"
        df.to_csv(report_path, index=False)
        print(f"Report generated successfully: {report_path}")
        print(df)
    else:
        print("No valid images found or processed.")

if __name__ == "__main__":
    generate_report()
