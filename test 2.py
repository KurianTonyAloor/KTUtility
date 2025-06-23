import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

KTU_NOTES_URL = "https://examtimetable.ktunotes.in/"
USER_DATA_FILE = "user_data.json"

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

def register_user():
    users = load_users()
    name = input("Enter your name: ")
    semester = input("Enter Semester (e.g., S1, S2, S3): ")
    branch = input("Enter Branch (e.g., Computer Science, Mechanical, Civil): ")
    scheme = input("Enter Scheme (e.g., 2019, 2022): ")
    users[name] = {"semester": semester, "branch": branch, "scheme": scheme}
    save_users(users)
    print(f"User {name} registered successfully!")

def select_user():
    users = load_users()
    if not users:
        print("No users found. Please register first.")
        register_user()
        return select_user()
    
    print("Available Users:")
    for index, name in enumerate(users.keys(), start=1):
        print(f"{index}. {name}")
    
    choice = int(input("Select your user number: "))
    user_name = list(users.keys())[choice - 1]
    print(f"Welcome back, {user_name}!")
    return user_name, users[user_name]

def get_exam_timetable(semester, branch, scheme):
    options = Options()
    options.add_argument("--headless")
    service = Service(r"C:\\Users\\Kurian Tony Aloor\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(KTU_NOTES_URL)
        time.sleep(3)
        
        Select(driver.find_element(By.ID, "sem")).select_by_visible_text(semester)
        time.sleep(2)
        Select(driver.find_element(By.ID, "branch")).select_by_visible_text(branch)
        time.sleep(2)
        Select(driver.find_element(By.ID, "scheme")).select_by_visible_text(scheme)
        time.sleep(2)
        
        timetable_element = driver.find_element(By.CLASS_NAME, "table-responsive.mt-3")
        timetable_text = timetable_element.text
        return timetable_text
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        driver.quit()

def find_exam_date(timetable, course):
    lines = timetable.split("\n")
    for line in lines:
        if course.lower() in line.lower():
            return line
    return "Course not found in timetable."

if __name__ == "__main__":
    user_name, user_details = select_user()
    semester, branch, scheme = user_details.values()
    
    exam_schedule = get_exam_timetable(semester, branch, scheme)
    
    if exam_schedule:
        print("\nExam Timetable Loaded Successfully!")
        course = input("Enter the course name to find its exam date: ")
        exam_date = find_exam_date(exam_schedule, course)
        print(f"\nExam Date for {course}: {exam_date}")
    else:
        print("Failed to retrieve exam timetable.")
