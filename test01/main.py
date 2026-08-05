from typing import Any


from fastapi import FastAPI,Path,HTTPException,Query,Body
import json

app = FastAPI()

def load_data():
    try:
        with open("students.json", "r") as f:
            students = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found")
    return students

class StudentView:
    @staticmethod
    @app.get("/")
    def read_root():
        students = load_data()
        return {"Student management system": students}

    @staticmethod
    @app.get("/about")
    def read_about():
        return {"about": "About Student management system"}

    @staticmethod
    @app.get("/sort")
    def get_all_students(sort_by: str = Query(..., description="The field to sort by", example="name"), order: str = Query("asc", description="Sort order: asc or desc", example="asc")):
        valid_fields = ["name", "class", "age", "roll", "Math marks", "English marks", "Science marks", "phone"]

        if order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="Invalid sort order")

        # Case-insensitive field matching
        field_map = {f.lower(): f for f in valid_fields}
        sort_by_lower = sort_by.lower()
        if sort_by_lower not in field_map:
            raise HTTPException(status_code=400, detail="Invalid sort field")
        sort_by = field_map[sort_by_lower]

        students = load_data()
        reverse = order == "desc"
        # Convert dictionary values to list for sorting
        student_list = list(students.values())

        # Sort numerically for numeric fields
        numeric_fields = ["age", "roll", "Math marks", "English marks", "Science marks"]
        if sort_by in numeric_fields:
            student_list.sort(key=lambda x: int(x[sort_by]), reverse=reverse)
        else:
            student_list.sort(key=lambda x: str(x[sort_by]), reverse=reverse)

        return {"students": student_list}

    @staticmethod
    @app.get("/{student_id}")
    def get_student(student_id: str = Path(..., description="The ID of the student to get", example="S001")):
        students = load_data()
        if student_id not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"student": students[student_id]}
    
    @staticmethod
    @app.post("/create_student")
    def create_student(student: dict = Body(...)):
        students = load_data()
        if "id" not in student:
            raise HTTPException(status_code=400, detail="Student ID is required")
        if student["id"] in students:
            raise HTTPException(status_code=400, detail="Student ID already exists")
        students[student["id"]] = student
        with open("students.json", "w") as f:
            json.dump(students, f, indent=4)
        return {"message": "Student created successfully"}
