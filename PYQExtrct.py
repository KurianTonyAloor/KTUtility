import requests
from bs4 import BeautifulSoup
import re
import os

def format_course_url(course_code, course_name, format_type=1):
    """
    Generate possible URL formats for downloading question papers.
    format_type:
        1 -> "https://www.ktunotes.in/ktu-{course_code}-{course_name}-solved-question-papers/"
        2 -> "https://www.ktunotes.in/ktu-{course_code_alpha}-{course_code_numeric}-{course_name}-solved-question-papers/"
        3 -> "https://www.ktunotes.in/ktu-{course_name}-question-papers-{course_code}/"
    """
    course_name_formatted = course_name.replace(" ", "-").lower()
    
    if format_type == 1:
        return f"https://www.ktunotes.in/ktu-{course_code.lower()}-{course_name_formatted}-solved-question-papers/"
    
    elif format_type == 2:
        course_code_alpha = re.match(r'[A-Za-z]+', course_code).group()
        course_code_numeric = re.search(r'\d+', course_code).group()
        return f"https://www.ktunotes.in/ktu-{course_code_alpha.lower()}-{course_code_numeric}-{course_name_formatted}-solved-question-papers/"
    
    elif format_type == 3:
        return f"https://www.ktunotes.in/ktu-{course_name_formatted}-question-papers-{course_code.lower()}/"

def extract_file_id(drive_url):
    """Extract the Google Drive file ID from the URL."""
    match = re.search(r'(file/d/|id=)([\w-]+)', drive_url)
    return match.group(2) if match else None

def download_google_drive_file(file_id, save_path):
    """Download a file from Google Drive using its file ID."""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"✅ File downloaded: {save_path}")
    else:
        print(f"❌ Failed to download file. Status code: {response.status_code}")

def download_question_papers(course_code, course_name, download_folder):
    """
    Fetch and download question papers for the given course code and name.
    Tries 3 different URL formats.
    """
    for format_type in range(1, 4):
        url = format_course_url(course_code, course_name, format_type)
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ Fetching papers from: {url}")
            course_folder = os.path.join(download_folder, f"{course_code}_{course_name.replace(' ', '_')}")
            os.makedirs(course_folder, exist_ok=True)

            soup = BeautifulSoup(response.text, 'html.parser')
            question_links = [link['href'] for link in soup.find_all('a', href=True) if 'drive.google.com' in link['href']]
            
            if question_links:
                for i, link in enumerate(question_links):
                    file_id = extract_file_id(link)
                    if file_id:
                        save_location = os.path.join(course_folder, f"{course_code}_{course_name.replace(' ', '_')}_{i+1}.pdf")
                        download_google_drive_file(file_id, save_location)
                    else:
                        print(f"❌ Failed to extract file ID from: {link}")
                return
            else:
                print("⚠ No question papers found at this URL. Trying next format...")

    print("❌ Failed to load webpage with all URL formats. Please check the course details.")

if __name__ == "__main__":
    course_code = input("Enter the course code (e.g., 'MAT206'): ").strip().upper()
    course_name = input("Enter the course name (e.g., 'Graph Theory'): ").strip()
    download_folder = r"C:\Users\Kurian Tony Aloor\Downloads\KTU"
    
    download_question_papers(course_code, course_name, download_folder)
