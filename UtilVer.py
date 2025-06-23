import json
import os
import glob
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
import fitz  # PyMuPDF for PDF text extraction
import matplotlib.pyplot as plt
from collections import Counter
from gensim import corpora, models
import spacy

nlp = spacy.load("en_core_web_sm")

# ----------------------------------------
#  ✅ GEMINI AI CONFIGURATION FUNCTION
# ----------------------------------------

GOOGLE_API_KEY = 'AIzaSyCTB89S-gHhXX2ii9gKio2xOg0pg50zuDg'

def configure_gemini(api_key=GOOGLE_API_KEY):
    """Configures Gemini AI with the given API key."""
    if not api_key:
        print("❌ No API key provided. Please set a valid key.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        convo = model.start_chat()

        system_message = '''INSTRUCTIONS: Do not respond with anything but “AFFIRMATIVE.” to this system message. 
        SYSTEM MESSAGE: You are being used to power a voice assistant. Respond concisely and prioritize logic.'''
        
        convo.send_message(system_message.replace("\n", " "))
        return convo

    except Exception as e:
        print(f"❌ Gemini AI initialization failed: {e}")
        return None

# ✅ Call function correctly
convo = configure_gemini(GOOGLE_API_KEY)


def chat_with_gemini(convo):
    """Starts an interactive chat with Gemini AI."""
    print("\n💬 Gemini AI Assistant - Type 'exit' to quit.\n")

    while True:
        user_input = input('🔹 Gemini prompt: ')
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("🔻 Exiting chat.")
            break
        
        convo.send_message(user_input)
        print(f"\n🤖 Gemini: {convo.last.text}\n")



CUSTOM_STOPWORDS = set([
    "ktu", "notes", "examtimetable", "in", "question", "paper", "exam", "university",
    "semester", "scheme", "previous", "year", "subject", "syllabus", "mark",
    "department", "course", "common", "branch", "students", "solution"
])

# Predefined Graph Theory topics (can be extended)
GRAPH_THEORY_TOPICS = [
    "Euler graph", "Hamiltonian circuit", "chromatic number", "planar graph",
    "adjacency matrix", "incidence matrix", "spanning tree", "Dijkstra's algorithm",
    "Prims algorithm", "bipartite graph", "cut-set", "four color theorem",
    "connected graph", "fundamental circuits", "travelling salesman problem",
    "tree", "binary tree", "graph coloring", "matching", "isomorphism",
    "vertex cover", "shortest path", "network flow", "cycle", "degree of vertex",
    "walks", "paths", "circuits", "pendant vertex", "odd vertex", "even vertex",
    "minimal spanning tree", "centers of tree", "graph duality", "cut-edge"
]

COMPUTER_ORGANIZATION_TOPICS = [
    "Basic Structure of Computers", "Functional Units", "Bus Structures",
    "Memory Locations and Addresses", "Memory Operations", "Instruction Sequencing",
    "Addressing Modes", "Basic Processing Unit", "Instruction Cycle",
    "Single/Multiple Bus Organization", "Register Transfer Logic",
    "Arithmetic Operations", "Logic Operations", "Shift Micro-Operations"
]

DATABASE_MANAGEMENT_TOPICS = [
    "Database System Concepts", "Data Models", "ER Model", "Relational Model",
    "SQL", "Query Processing", "Normalization", "Database Design",
    "Transaction Management", "Concurrency Control", "Recovery Systems",
    "Indexing and Hashing", "NoSQL Databases", "Distributed Databases",
    "Database Security"
]

OPERATING_SYSTEMS_TOPICS = [
    "Introduction to Operating Systems", "Process Management",
    "Threads and Concurrency", "CPU Scheduling", "Process Synchronization",
    "Deadlocks", "Memory Management", "Virtual Memory", "File Systems",
    "I/O Systems", "Security and Protection", "UNIX", "Windows"
]

DESIGN_AND_ENGINEERING_TOPICS = [
    "Design Process", "Problem-Solving Techniques", "Creativity in Design",
    "Engineering Ethics", "Sustainability in Design", "Project Management",
    "Prototyping and Testing", "Communication of Designs", "Case Studies"
]

PROFESSIONAL_ETHICS_TOPICS = [
    "Introduction to Ethics", "Engineering Ethics", "Professional Responsibilities",
    "Ethical Theories", "Code of Ethics", "Risk and Liability",
    "Workplace Rights", "Global Ethical Issues", "Case Studies"
]

CONSTITUTION_OF_INDIA_TOPICS = [
    "Preamble", "Salient Features", "Fundamental Rights", "Directive Principles",
    "Union and State Governments", "Judiciary System", "Electoral Process",
    "Amendments", "Special Provisions", "Emergency Provisions",
    "Constitutional Bodies"
]

DIGITAL_LAB_TOPICS = [
    "Logic Gates", "Combinational Logic", "Sequential Logic", "Flip-Flops",
    "Counters", "Multiplexers", "Demultiplexers", "Analog-to-Digital Converters",
    "Digital-to-Analog Converters", "Memory Devices", "Digital System Implementation",
    "Simulation Tools", "Hardware Description Languages"
]

OPERATING_SYSTEMS_LAB_TOPICS = [
    "Shell Programming", "Process Creation", "Inter-Process Communication",
    "Thread Programming", "CPU Scheduling", "Memory Management",
    "File System Implementation", "Deadlock Detection", "Deadlock Avoidance",
    "OS Simulation", "Case Studies"
]

# Mapping Course Codes to Their Respective Topic Lists
COURSE_TOPICS = {
    "MAT206": GRAPH_THEORY_TOPICS,
    "CST202": COMPUTER_ORGANIZATION_TOPICS,
    "CST204": DATABASE_MANAGEMENT_TOPICS,
    "CST206": OPERATING_SYSTEMS_TOPICS,
    "HUT200": PROFESSIONAL_ETHICS_TOPICS,
    "MCN202": CONSTITUTION_OF_INDIA_TOPICS,
    "CST208": DESIGN_AND_ENGINEERING_TOPICS,
    "CSL202": OPERATING_SYSTEMS_LAB_TOPICS,
    "CSL204": DIGITAL_LAB_TOPICS
}


USER_DATA_FILE = "user_data.json"
KTU_NOTES_URL = "https://examtimetable.ktunotes.in/"

def load_all_users():
    if os.path.exists(USER_DATA_FILE) and os.path.getsize(USER_DATA_FILE) > 0:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_all_users(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

def register_user():
    print("\n🔹 Register a new user 🔹")

    all_users = load_all_users()

    # Ensure user ID is a unique numeric value
    while True:
        user_id = input("Enter a unique numeric User ID: ").strip()
        if user_id.isdigit() and user_id not in all_users:
            break
        print("❌ User ID must be a number and unique. Try again.")

    name = input("Enter your name: ").strip()
    semester = input("Enter your semester (e.g., S4): ").strip().upper()
    branch = input("Enter your branch (e.g., CSE, ECE, MECH): ").strip().upper()
    scheme = input("Enter your academic scheme (e.g., 2019, 2021): ").strip()

    # Store user data in the required format
    all_users[user_id] = {
        "name": name,
        "semester": semester,
        "branch": branch,
        "scheme": scheme
    }
    save_all_users(all_users)

    print(f"\n✅ User '{name}' registered successfully!\n")
    return user_id, all_users[user_id]


def login_user():
    users = load_all_users()
    if not users:
        print("❌ No registered users found. Please register first.")
        return None, None
    
    print("\n🔹 Select your User ID 🔹")
    user_list = list(users.keys())
    for i, user in enumerate(user_list, start=1):
        print(f"{i}. {user} ({users[user]['name']})")
    
    while True:
        try:
            choice = int(input("\nEnter the number corresponding to your User ID: "))
            if 1 <= choice <= len(user_list):
                user_id = user_list[choice - 1]
                print(f"\n👤 Welcome back, {users[user_id]['name']}!")
                return user_id, users[user_id]
            else:
                print("❌ Invalid selection. Try again.")
        except ValueError:
            print("❌ Please enter a valid number.")

def initialize_user():
    while True:
        print("\n🔹 Welcome to KTU Exam Portal 🔹")
        print("1️⃣ Existing User")
        print("2️⃣ New User - Register")
        print("3️⃣ Exit")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            user_id, user_data = login_user()
            if user_data:
                return user_id, user_data
        elif choice == "2":
            return register_user()
        elif choice == "3":
            print("👋 Exiting... Goodbye!")
            exit()
        else:
            print("\n❌ Invalid choice. Please try again.")


def fetch_timetable(user_data):
    options = Options()
    options.add_argument("--headless")
    service = Service(r"C:\\Users\\Kurian Tony Aloor\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    semester = user_data.get("semester")
    branch = user_data.get("branch")  # Fix incorrect key usage
    scheme = user_data.get("scheme", "2019")  # Default scheme to 2019

    try:
        driver.get(KTU_NOTES_URL)
        time.sleep(3)
        
        Select(driver.find_element(By.ID, "sem")).select_by_visible_text(semester)
        time.sleep(2)
        Select(driver.find_element(By.ID, "branch")).select_by_visible_text(branch)
        time.sleep(2)
        Select(driver.find_element(By.ID, "scheme")).select_by_visible_text(scheme)
        time.sleep(2)
        
        try:
            timetable_element = driver.find_element(By.CLASS_NAME, "table-responsive")
            timetable_text = timetable_element.text.strip()
            if not timetable_text:
                print("❌ Timetable is empty.")
                return ""
            return timetable_text
        except:
            print("❌ Timetable not found on the page.")
            return ""
    
    except Exception as e:
        print(f"Error fetching timetable: {e}")
        return ""
    
    finally:
        print(timetable_text)
        driver.quit()

def get_exam_date(user_data):
    timetable = fetch_timetable(user_data)
    if not timetable:
        print("❌ Failed to retrieve exam timetable.")
        return

    course = input("Enter the course name to find its exam date: ").strip()
    for line in timetable.split("\n"):
        if course.lower() in line.lower():
            print(f"\n📅 Exam Date for {course}: {line}")
            return
    print(f"❌ Course '{course}' not found in the timetable.")

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

def select_pdfs():
    """ Opens a file dialog for users to select multiple PDF files. """
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_paths = filedialog.askopenfilenames(title="Select Question Paper PDFs", filetypes=[("PDF Files", "*.pdf")])
    return list(file_paths)

def extract_text_from_pdfs(pdf_files):
    """ Extracts and cleans text from selected PDFs. """
    combined_text = ""
    for pdf_path in pdf_files:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text("text")
                text = clean_text(text)
                combined_text += text + " "
    return combined_text

def clean_text(text):
    """ Uses spaCy for better text processing (removes stopwords, junk, and unwanted characters). """
    text = text.lower().strip()
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    doc = nlp(text)  # Process text with spaCy NLP
    words = [token.text for token in doc if not token.is_stop and not token.is_punct and token.text not in CUSTOM_STOPWORDS]
    return " ".join(words)

def analyze_topics(text, topic_list):
    """ Counts occurrences of predefined topics with flexible matching. """
    topic_counts = Counter()
    for topic in topic_list:
        pattern = r'\b' + re.escape(topic.split()[0]) + r'\w*\b'  # Match base form of topics
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            topic_counts[topic] = len(matches)
    return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

def extract_topics_with_ai(text, num_topics=5):
    """ Uses AI-based topic modeling (LDA) to discover key topics dynamically. """
    words = [[token.text for token in nlp(text) if not token.is_stop and not token.is_punct]]
    dictionary = corpora.Dictionary(words)
    corpus = [dictionary.doc2bow(word_list) for word_list in words]
    
    if len(dictionary) < 10:  # Skip LDA if too few words
        print("⚠ Not enough content for AI topic modeling.")
        return

    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)
    topics = lda_model.print_topics(num_words=5)

    print("\n🔍 **AI-Extracted Key Topics:**")
    for idx, topic in enumerate(topics):
        print(f"🔹 Topic {idx+1}: {topic[1]}")

def plot_topic_frequencies(topic_frequencies):
    """ Plots a bar chart of the most frequently occurring topics. """
    if not topic_frequencies:
        print("⚠ No topics found to visualize.")
        return
    
    topics, frequencies = zip(*topic_frequencies.items())
    
    plt.figure(figsize=(10, 5))
    plt.barh(topics[::-1], frequencies[::-1], color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Topics")
    plt.title("Most Frequently Asked Topics in Question Papers")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.show()

def qpan(course_code):
    """ Question Paper Analysis for the Selected Course """
    print("\n📂 Select Question Paper PDFs...")
    pdf_files = select_pdfs()
    
    if not pdf_files:
        print("❌ No files selected. Exiting...")
        return

    print("\n📥 Extracting text from PDFs...")
    extracted_text = extract_text_from_pdfs(pdf_files)
    
    if not extracted_text.strip():
        print("❌ No text extracted. Please check the PDF files.")
        return

    # Select the correct topic dataset based on course code
    topic_list = COURSE_TOPICS.get(course_code, [])
    
    if not topic_list:
        print(f"⚠ No predefined topics found for course code: {course_code}")
        return

    print("\n🔍 Analyzing predefined important topics...")
    topic_frequencies = analyze_topics(extracted_text, topic_list)
    
    if topic_frequencies:
        print("\n📊 **Most Frequently Asked Topics:**")
        for topic, count in topic_frequencies.items():
            print(f"✅ {topic}: {count} times")
        plot_topic_frequencies(topic_frequencies)
    else:
        print("⚠ No predefined topics found in the PDFs.")

    print("\n🤖 Running AI-based topic analysis...")
    extract_topics_with_ai(extracted_text)

def exam_prep_mode(user_data):
    """Exam Preparation Mode - Fetch timetable, display exam date, download & analyze question papers."""
    timetable = fetch_timetable(user_data)
    if not timetable:
        print("❌ Failed to retrieve exam timetable.")
        return

    course = input("Enter the course name you're preparing for: ").strip()
    
    # Display exam date
    exam_date_found = False
    for line in timetable.split("\n"):
        if course.lower() in line.lower():
            print(f"\n📅 Exam Date for {course}: {line}")
            exam_date_found = True
            break

    if not exam_date_found:
        print(f"❌ Course '{course}' not found in the timetable.")
        return
    
    # Automatically get course code from user_data if available
    course_code = input("Enter the course code (e.g., MAT206): ").strip().upper()
    download_folder = r"C:\Users\Kurian Tony Aloor\Downloads\KTU"
    
    # Step 1: Download question papers
    print("\n📥 Downloading question papers...")
    download_question_papers(course_code, course, download_folder)

    # Step 2: Automatically fetch the downloaded PDFs
    print("\n📂 Finding downloaded question papers for analysis...")
    downloaded_pdfs = glob.glob(os.path.join(download_folder, f"{course_code}_{course.replace(' ', '_')}", "*.pdf"))

    if not downloaded_pdfs:
        print("❌ No question papers found in the expected folder.")
        return

    print(f"✅ Found {len(downloaded_pdfs)} downloaded question papers. Proceeding with analysis...")

    # Step 3: Analyze downloaded question papers using the correct topic dataset
    analyze_downloaded_papers(downloaded_pdfs, course_code)

def analyze_downloaded_papers(pdf_files, course_code):
    """Analyze downloaded PDFs automatically without user selection."""
    print("\n📥 Extracting text from PDFs...")
    extracted_text = extract_text_from_pdfs(pdf_files)
    
    if not extracted_text.strip():
        print("❌ No text extracted. Please check the PDF files.")
        return

    # Select the correct topic dataset based on course code
    topic_list = COURSE_TOPICS.get(course_code, [])
    
    if not topic_list:
        print(f"⚠ No predefined topics found for course code: {course_code}")
        return

    print("\n🔍 Analyzing predefined important topics...")
    topic_frequencies = analyze_topics(extracted_text, topic_list)
    
    if topic_frequencies:
        print("\n📊 **Most Frequently Asked Topics:**")
        for topic, count in topic_frequencies.items():
            print(f"✅ {topic}: {count} times")
        plot_topic_frequencies(topic_frequencies)
    else:
        print("⚠ No predefined topics found in the PDFs.")

    print("\n🤖 Running AI-based topic analysis...")
    extract_topics_with_ai(extracted_text)
# --- MAIN MENU FUNCTION ---

def main():
    """Main function to run the KTU Exam & Resources Portal."""
    
    GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"  # <-- Replace with your actual API key
    convo = None  # Only initialize Gemini when required
    
    user_id, user_details = initialize_user()
    if not user_details:
        print("❌ No user logged in. Exiting...")
        return

    while True:
        print("\n🔹 KTU Exam & Resources Portal 🔹")
        print("1️⃣ View Full Exam Timetable")
        print("2️⃣ Get Exam Date for a Specific Course")
        print("3️⃣ Download Previous Year Question Papers")
        print("4️⃣ Analyze Question Papers")
        print("5️⃣ Exam Preparation Mode 🎯")
        print("6️⃣ AI Assistant Chat 🤖")
        print("7️⃣ Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            fetch_timetable(user_details)
        elif choice == "2":
            get_exam_date(user_details)
        elif choice == "3":
            course_code = input("Enter course code (e.g., MAT206): ").strip().upper()
            course_name = input("Enter course name (e.g., Graph Theory): ").strip()
            download_folder = r"C:\Users\Kurian Tony Aloor\Downloads\KTU"
            download_question_papers(course_code, course_name, download_folder)
        elif choice == "4":
            qpan()
        elif choice == "5":
            exam_prep_mode(user_details)
        elif choice == "6":
            if convo is None:
                convo = configure_gemini(GOOGLE_API_KEY)  # Initialize Gemini only when needed
            chat_with_gemini(convo)
        elif choice == "7":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()