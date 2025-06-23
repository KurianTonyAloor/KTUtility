import sys
import os
import json
import requests
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QFileDialog, QInputDialog, QMessageBox, 
                             QProgressBar, QHBoxLayout, QFrame, QTextBrowser, 
                             QScrollArea)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from test21 import (fetch_timetable, get_exam_date, download_question_papers,
                     analyze_downloaded_papers, exam_prep_mode, initialize_user)

# ======================== LOGIN WINDOW ============================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KTU Exam Utility - Login")
        self.setGeometry(400, 200, 400, 250)
        self.layout = QVBoxLayout()

        self.label = QLabel("🔹 Welcome to KTU Exam Utility\nSelect an option:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.login_btn = QPushButton("👤 Existing User Login")
        self.register_btn = QPushButton("📝 New User Register")
        self.exit_btn = QPushButton("❌ Exit")

        for btn in [self.login_btn, self.register_btn, self.exit_btn]:
            btn.setStyleSheet("padding: 10px; margin: 5px; font-size: 14px;")

        self.layout.addWidget(self.login_btn)
        self.layout.addWidget(self.register_btn)
        self.layout.addWidget(self.exit_btn)

        self.setLayout(self.layout)

        # Button Connections
        self.login_btn.clicked.connect(self.login_user)
        self.register_btn.clicked.connect(self.register_user)
        self.exit_btn.clicked.connect(self.close)

    def login_user(self):
        """Handles existing user login."""
        user_id, user_details = initialize_user()  # No arguments
        if user_details:
            self.open_main_window(user_id, user_details)

    def register_user(self):
        """Handles new user registration."""
        user_id, user_details = initialize_user()  # No arguments
        if user_details:
            self.open_main_window(user_id, user_details)



    def open_main_window(self, user_id, user_details):
        """Opens the main dashboard after successful login."""
        self.main_window = KTUExamUtility(user_id, user_details)
        self.main_window.show()
        self.close()

# ======================== MAIN DASHBOARD ============================
class KTUExamUtility(QWidget):
    def __init__(self, user_id, user_details):
        super().__init__()
        self.user_id = user_id
        self.user_details = user_details
        self.dark_mode = False
        self.initUI()
        self.load_demo_news()

    def initUI(self):
        self.setWindowTitle("KTU Exam Utility")
        self.setGeometry(300, 150, 1000, 650)
        self.main_layout = QHBoxLayout()

        # Sidebar Navigation
        self.sidebar = QVBoxLayout()
        self.sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setLayout(self.sidebar)
        self.sidebar_frame.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px;")

        self.timetable_btn = QPushButton("📅 View Timetable")
        self.exam_date_btn = QPushButton("📅 Get Exam Date")
        self.qp_download_btn = QPushButton("📥 Download QPs")
        self.qp_analyze_btn = QPushButton("📊 Analyze QPs")
        self.exam_prep_btn = QPushButton("🎯 Exam Prep Mode")
        self.dark_mode_btn = QPushButton("🌙 Toggle Dark Mode")
        self.exit_btn = QPushButton("❌ Exit")

        for btn in [self.timetable_btn, self.exam_date_btn, self.qp_download_btn,
                    self.qp_analyze_btn, self.exam_prep_btn, self.dark_mode_btn, self.exit_btn]:
            btn.setStyleSheet("background-color: #34495e; color: white; padding: 10px; margin: 5px;")
            self.sidebar.addWidget(btn)

        # Main Content Area
        self.main_content = QVBoxLayout()
        self.timetable_display = QTextBrowser()
        self.progress_bar = QProgressBar()

        self.timetable_display.setText("Latest Exam Timetable Will Appear Here...")

        # Social Media-Style News Feed
        self.news_scroll_area = QScrollArea()
        self.news_scroll_area.setWidgetResizable(True)
        self.news_widget = QWidget()
        self.news_layout = QVBoxLayout(self.news_widget)
        self.news_scroll_area.setWidget(self.news_widget)

        # Add components to main content layout
        self.main_content.addWidget(QLabel("Latest Exam Timetable"))
        self.main_content.addWidget(self.timetable_display)
        self.main_content.addWidget(QLabel("KTU News Feed"))
        self.main_content.addWidget(self.news_scroll_area)
        self.main_content.addWidget(QLabel("Student Progress"))
        self.main_content.addWidget(self.progress_bar)

        # Floating AI Assistant
        self.ai_button = QPushButton()
        self.ai_button.setIcon(QIcon("ai_icon.png"))  
        self.ai_button.setIconSize(QPixmap("ai_icon.png").rect().size())
        self.ai_button.setStyleSheet("border-radius: 30px; width: 60px; height: 60px;")

        # Layout Setup
        self.main_layout.addWidget(self.sidebar_frame, 1)
        self.main_layout.addLayout(self.main_content, 3)
        self.main_layout.addWidget(self.ai_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.main_layout)

        # Button Connections
        self.timetable_btn.clicked.connect(self.view_timetable)
        self.exam_date_btn.clicked.connect(self.get_exam_date)
        self.qp_download_btn.clicked.connect(self.download_qp)
        self.qp_analyze_btn.clicked.connect(self.analyze_qp)
        self.exam_prep_btn.clicked.connect(self.exam_prep_mode)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        self.exit_btn.clicked.connect(self.close)
        self.ai_button.clicked.connect(self.open_ai_assistant)

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet("")
            self.dark_mode = False
        else:
            self.setStyleSheet("background-color: #1e1e1e; color: white;")
            self.dark_mode = True

    def view_timetable(self):
        timetable = fetch_timetable(self.user_details)
        self.timetable_display.setText(timetable if timetable else "Failed to fetch timetable!")

    def get_exam_date(self):
        get_exam_date(self.user_details)

    def download_qp(self):
        course_code, ok = QInputDialog.getText(self, "Course Code", "Enter Course Code:")
        if ok and course_code:
            course_name, ok = QInputDialog.getText(self, "Course Name", "Enter Course Name:")
            if ok and course_name:
                download_folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
                threading.Thread(target=download_question_papers, args=(course_code, course_name, download_folder)).start()

    def analyze_qp(self):
        pdf_files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if pdf_files:
            course_code, ok = QInputDialog.getText(self, "Course Code", "Enter Course Code:")
            if ok and course_code:
                analyze_downloaded_papers(pdf_files, course_code)

    def exam_prep_mode(self):
        threading.Thread(target=exam_prep_mode, args=(self.user_details,)).start()

    def open_ai_assistant(self):
        QMessageBox.information(self, "AI Assistant", "Chat assistant will be implemented soon!")

    def load_demo_news(self):
        """Load 15 manually added Instagram-style posts into the scrollable feed."""
        demo_posts = [
            "📢 KTU Semester 4 Exam Timetable Released! Check now.",
            "⚠️ Important: Internal marks submission deadline extended.",
            "📚 KTU Updates: New syllabus changes for 2025 batch.",
        ]
        for post in demo_posts:
            self.news_layout.addWidget(QLabel(post))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
