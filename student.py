class Student:
    # Default student number increaser since student numbers aren't supposed to stay the same
    default_student_number = 1

    def __init__(self, first_name="", last_name="", student_number=None, midterm_grade1=0, midterm_grade2=0, final_grade=0):
        self.first_name = first_name
        self.last_name = last_name
        self.student_number = student_number if student_number is not None else Student.default_student_number
        Student.default_student_number += 1
        self.midterm_grade1 = midterm_grade1
        self.midterm_grade2 = midterm_grade2
        self.final_grade = final_grade

    # Getters
    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_student_number(self):
        return self.student_number

    def get_midterm_grade1(self):
        return self.midterm_grade1

    def get_midterm_grade2(self):
        return self.midterm_grade2

    def get_final_grade(self):
        return self.final_grade

    # Setters
    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_student_number(self, student_number):
        self.student_number = student_number

    def set_midterm_grade1(self, midterm_grade1):
        if 0 <= midterm_grade1 <= 100:
            self.midterm_grade1 = midterm_grade1
            return True
        return False

    def set_midterm_grade2(self, midterm_grade2):
        if 0 <= midterm_grade2 <= 100:
            self.midterm_grade2 = midterm_grade2
            return True
        return False

    def set_final_grade(self, final_grade):
        if 0 <= final_grade <= 100:
            self.final_grade = final_grade
            return True
        return False

    # Python's version of the toString()
    def __str__(self):
        return (f"{self.first_name} {self.last_name}\n"
                f"Student number: {self.student_number}\n"
                f"Midterm grade 1: {self.midterm_grade1:.1f}\n"
                f"Midterm grade 2: {self.midterm_grade2:.1f}\n"
                f"Final grade: {self.final_grade:.1f}")
