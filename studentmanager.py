import json
from student import Student

class StudentManager:
    midterm_grade1_weight = 25.0
    midterm_grade2_weight = 25.0
    final_weight = 50.0
    file_name = "students.json"

    def __init__(self):
        self.students = []

    # Add a student, doing a check for a student number
    def add_student(self, first_name, last_name, student_number, midterm1, midterm2, final):
        if any(s.student_number == student_number for s in self.students):
            return False
        self.students.append(Student(first_name, last_name, student_number, midterm1, midterm2, final))
        self.save()
        return True

    # Delete specified student based on student number
    def delete_student(self, student_number):
        self.students = [s for s in self.students if s.student_number != student_number]
        self.save()

    # Find specified student based on student number
    def find_student(self, student_number):
        return next((s for s in self.students if s.student_number == student_number), None)

    # Print all students, easy stuff
    def print_all_students(self):
        return "\n\n".join(str(s) for s in self.students) if self.students else "No students available."

    # Print all students, just as easy
    def print_all_students_with_grades(self):
        if not self.students:
            return "No students available."
        return "\n\n".join(f"{s}\nLetter Grade: {self.get_letter_grade(s.student_number)}" for s in self.students)

    # Get the final grade
    def get_final_grade(self, student_number):
        student = self.find_student(student_number)
        if student:
            return round((student.midterm_grade1 * self.midterm_grade1_weight +
                          student.midterm_grade2 * self.midterm_grade2_weight +
                          student.final_grade * self.final_weight) / 100, 1)
        return 0.0

    # Get a letter grade
    def get_letter_grade(self, student_number):
        grade = self.get_final_grade(student_number)
        if grade > 90:
            return "A"
        elif grade > 80:
            return "B"
        elif grade > 70:
            return "C"
        elif grade >= 60:
            return "D"
        return "F"

    # Change the info of a student
    def change_student_info(self, student_number, field, new_value):
        student = self.find_student(student_number)
        if student:
            setattr(student, field, new_value)
            self.save()
            return True
        return False

    # Use sort and lambda function to sort students by name
    def sort_students_by_name(self):
        self.students.sort(key=lambda s: (s.last_name, s.first_name))
        self.save()

    # Set weights
    def set_weights(self, weight1, weight2, weight3):
        if weight1 + weight2 + weight3 == 100:
            self.midterm_grade1_weight = weight1
            self.midterm_grade2_weight = weight2
            self.final_weight = weight3
            return True
        return False

    # Save to JSON file
    def save(self):
        with open(self.file_name, "w") as file:
            json.dump([s.__dict__ for s in self.students], file)

    # Load from JSON file
    def load(self):
        try:
            with open(self.file_name, "r") as file:
                data = json.load(file)
                self.students = [Student(**s) for s in data]
        except FileNotFoundError:
            self.students = []

if __name__ == "__main__":
    manager = StudentManager()
    manager.load()
    print(manager.print_all_students())
