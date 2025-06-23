from flask import Flask, request, jsonify
from flask_cors import CORS
from ktu_exam_scraper import extract_exam_timetable

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route("/get_exam_schedule", methods=["POST"])
def get_exam_schedule():
    data = request.get_json()
    course_code = data.get("course_code")
    
    if not course_code:
        return jsonify({"error": "Course code is required"}), 400
    
    exam_dates = extract_exam_timetable(course_code)
    
    return jsonify({"exam_dates": exam_dates})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
