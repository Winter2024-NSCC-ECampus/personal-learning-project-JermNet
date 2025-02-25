from studentmanager import StudentManager

def main():
    student_manager = StudentManager()
    student_manager.load()

    while True:
        try:
            print("\nWhat would you like to do?")
            print("1. Print all Student data")
            print("2. Sort students by last name")
            print("3. Add a new student")
            print("4. Calculate letter grades for all students")
            print("5. Change student information")
            print("6. Print a specific student's data")
            print("7. Remove a student")
            print("8. Delete ALL student data")
            print("9. Change grading scheme")
            print("10. Load from file")
            print("11. Exit")

            choice = int(input("Enter your choice: "))

            if choice == 1:
                print(student_manager.print_all_students())

            elif choice == 2:
                student_manager.sort_students_by_name()
                print("Students have been sorted!")

            elif choice == 3:
                first_name = input("Enter first name: ")
                last_name = input("Enter last name: ")
                student_number = int(input("Enter student number: "))
                midterm1 = float(input("Enter first midterm grade: "))
                midterm2 = float(input("Enter second midterm grade: "))
                final = float(input("Enter final grade: "))
                if student_manager.add_student(first_name, last_name, student_number, midterm1, midterm2, final):
                    print("Student added!")
                else:
                    print("Could not add student! Ensure student number is unique.")

            elif choice == 4:
                print(student_manager.print_all_students_with_grades())

            elif choice == 5:
                student_number = int(input("Enter student number to modify: "))
                field_map = {
                    1: "first_name",
                    2: "last_name",
                    3: "student_number",
                    4: "midterm_grade1",
                    5: "midterm_grade2",
                    6: "final_grade"
                }
                print("1. First name\n2. Last name\n3. Student number\n4. First midterm grade\n5. Second midterm grade\n6. Final grade\n7. Exit")
                field_choice = int(input("Enter choice: "))
                if field_choice in field_map:
                    new_value = input("Enter new value: ")
                    if field_choice == 3:
                        new_value = int(new_value)
                    elif field_choice in [4, 5, 6]:
                        new_value = float(new_value)
                    student_manager.change_student_info(student_number, field_map[field_choice], new_value)
                    print("Student information updated!")

            elif choice == 6:
                student_number = int(input("Enter student number: "))
                student = student_manager.find_student(student_number)
                if student:
                    print(student)
                else:
                    print("Student does not exist!")

            elif choice == 7:
                student_number = int(input("Enter student number to remove: "))
                student_manager.delete_student(student_number)
                print("Student removed!")

            elif choice == 8:
                confirm = input("Are you sure you want to delete ALL data? (yes/no): ")
                if confirm.lower() == "yes":
                    student_manager.students = []
                    student_manager.save()
                    print("All data deleted!")

            elif choice == 9:
                midterm1_weight = float(input("Enter weight for midterm 1: "))
                midterm2_weight = float(input("Enter weight for midterm 2: "))
                final_weight = float(input("Enter weight for final: "))
                if student_manager.set_weights(midterm1_weight, midterm2_weight, final_weight):
                    print("Grading scheme updated!")
                else:
                    print("Invalid weights! They must sum to 100.")

            elif choice == 10:
                student_manager.load()
                print("Data loaded from file!")

            elif choice == 11:
                print("Exiting program.")
                break

            else:
                print("Invalid option! Try again.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
