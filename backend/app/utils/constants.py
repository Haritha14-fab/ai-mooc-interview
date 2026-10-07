"""Application constants"""

# Subjects
SUBJECTS = [
    "Python",
    "SQL",
    "Java",
    "C",
    "C++",
    "HTML & CSS",
    "JavaScript",
    "Data Structures",
    "DBMS",
    "Computer Networks"
]

# Difficulty levels
DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]

# Assessment status
ASSESSMENT_STATUS = {
    "IN_PROGRESS": "in_progress",
    "SUBMITTED": "submitted",
    "FINAL_SUBMITTED": "final_submitted"
}

# Pass/Fail threshold
PASS_THRESHOLD = 80  # Must score more than 80% to pass

# Performance levels
PERFORMANCE_LEVELS = {
    "EXCELLENT": (90, 100),
    "VERY_GOOD": (81, 89),
    "GOOD": (60, 80),
    "NEEDS_IMPROVEMENT": (40, 59),
    "POOR": (0, 39),
}

# Questions per assessment
QUESTIONS_PER_ASSESSMENT = 10
