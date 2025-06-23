import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF parsing
import os
import re

# URL of the KTU timetable page
KTU_URL = "https://ktu.edu.in/exam/timetable"

# Step 1: Fetch the webpage and extract PDF titles and links
def get_pdf_details():
    response = requests.get(KTU_URL)
    if response.status_code != 200:
        print("Failed to fetch the page")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_details = []
    
    # Find all anchor tags with PDFs
    for link in soup.find_all('a', href=True):
        href = link['href']
        title = link.text.strip()
        
        if href.endswith(".pdf"):
            pdf_url = "https://ktu.edu.in" + href if href.startswith("/") else href
            pdf_details.append({"title": title, "url": pdf_url})
    
    return pdf_details

# Step 2: Parse PDF titles to extract metadata
def parse_pdf_title(title):
    pattern = re.compile(r"(?P<course>\w+\.\w+) S(?P<semester>\d+) .* (?P<month>\w+) (?P<year>\d{4}) \((?P<scheme>\d{4}) Scheme\)")
    match = pattern.search(title)
    
    if match:
        return match.groupdict()
    return {}

# Step 3: Download and extract exam timetable for a specific course
def extract_exam_timetable(course_code):
    pdf_details = get_pdf_details()
    
    if not pdf_details:
        print("No PDFs found on the page.")
        return []
    
    exam_dates = []
    
    for i, pdf in enumerate(pdf_details):
        if course_code not in pdf["title"]:
            continue  # Skip PDFs that don't match the course
        
        pdf_path = f"timetable_{i}.pdf"
        
        # Download PDF
        pdf_response = requests.get(pdf["url"])
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_response.content)
        
        # Parse PDF
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text()
                
                # Extract dates (custom logic based on PDF format)
                for line in text.split("\n"):
                    if any(month in line for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                        exam_dates.append(line.strip())
        
        # Clean up PDF
        os.remove(pdf_path)
    
    return exam_dates

if __name__ == "__main__":
    course_code = input("Enter the course code (e.g., MBA S4): ")
    exam_schedule = extract_exam_timetable(course_code)
    if exam_schedule:
        print("Extracted Exam Dates:", exam_schedule)
    else:
        print("No exam timetable found for the given course.")
