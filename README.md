# KTUtility 🧠📚

A command-line based intelligent academic assistant for KTU students.  
This modular Python tool helps you **fetch, analyze, and optimize** your exam preparation using smart automation and topic-weight predictions.

> ⚙️ Built entirely in Python using web scraping, natural language parsing, and custom ML models.

---

## 🚀 Features

### 📆 `KTUTT.py`
- Fetches official **KTU exam timetables** directly from public sources.
- Parses and formats schedules for clean viewing.
- Used as the base module for time-aware exam planning.

### 📄 `PYQ_extract.py`
- Efficiently scrapes and extracts **Past Year Question papers** from web sources.
- Applies content filtering to maintain relevance and quality.
- Outputs structured data by subject, module, and year.

### 🧠 `mainSP.py` (inside `/backend`)
- In-house ML-powered analyzer that processes question papers.
- Generates a **graphical representation of important topics** by module weight.
- Designed to work seamlessly with extracted PYQ data.

### 🔁 `UtilVer.py`
- Combines all utilities into one intuitive CLI experience.
- Supports chaining: fetch -> analyze -> output.
- Great for daily exam prep workflows.

### 🧪 **Exam Mode**
- Auto-detects upcoming exams via timetable.
- Pulls corresponding PYQs and runs analysis.
- Recommends **what to study** and **how much**, based on available time.

---

## 🖥️ Usage

> **All scripts are CLI-based and self-explanatory.**

```bash
# Fetch the exam timetable
python KTUTT.py

# Extract past year question papers
python PYQ_extract.py

# Run the topic importance analysis
cd backend
python mainSP.py

# Use full utility with scheduler and recommendation
python UtilVer.py
