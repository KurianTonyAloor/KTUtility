import httpx  # Alternative to requests
from selectolax.parser import HTMLParser  # Faster alternative to BeautifulSoup
import pdfplumber  # Alternative to PyMuPDF for PDF parsing
import os
import re
from dateutil import parser  # Better for handling different date formats

# URL of the KTU timetable page
KTU_URL = "https://ktu.edu.in/exam/timetable"

# Step 1: Fetch the webpage and extract PDF titles and links
def get_pdf_details():
    try:
        response = httpx.get(KTU_URL, timeout=10, verify=False)
        response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Error fetching the webpage: {e}")
        return []
    
    soup = HTMLParser(response.text)  # Faster HTML parsing
    pdf_details = []
    
    # Extract all <a> tags with PDF links
    for link in soup.css("a[href$='.pdf']"):
        href = link.attributes.get("href", "")
        title = link.text(strip=True)
        
        if href:
            pdf_url = href if href.startswith("http") else f"https://ktu.edu.in{href}"
            pdf_details.append({"title": title, "url": pdf_url})
    
    return pdf_details

# Step 2: Extract exam timetable from PDFs
def extract_exam_timetable(course_code):
    pdf_details = get_pdf_details()
    
    if not pdf_details:
        print("No PDFs found on the page.")
        return []
    
    exam_dates = []
    
    for i, pdf in enumerate(pdf_details):
        if not re.search(rf"\b{re.escape(course_code)}\b", pdf["title"], re.IGNORECASE):
            continue  # Skip PDFs that don't match the course
        
        pdf_path = f"timetable_{i}.pdf"
        
        try:
            # Download PDF
            pdf_response = httpx.get(pdf["url"], timeout=10)
            pdf_response.raise_for_status()
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_response.content)
            
            # Parse PDF using PDFPlumber
            with pdfplumber.open(pdf_path) as doc:
                for page in doc.pages:
                    text = page.extract_text()
                    
                    if text:
                        # Extract dates using dateutil.parser
                        for word in text.split():
                            try:
                                parsed_date = parser.parse(word, fuzzy=True, dayfirst=True)
                                exam_dates.append(parsed_date.strftime("%d %b %Y"))
                            except ValueError:
                                continue  # Skip non-date text
        
        except httpx.RequestError as e:
            print(f"Error downloading {pdf['url']}: {e}")
        finally:
            # Clean up downloaded PDF
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    return sorted(set(exam_dates))  # Remove duplicates & sort dates

if __name__ == "__main__":
    course_code = input("Enter the course code (e.g., MBA S4): ").strip()
    exam_schedule = extract_exam_timetable(course_code)
    
    if exam_schedule:
        print("Extracted Exam Dates:", exam_schedule)
    else:
        print("No exam timetable found for the given course.")
