from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(41, 128, 185)
        self.set_x(12)
        self.multi_cell(0, 8, 'AuraFace - Smart Campus Application', align='C')
        self.set_font('helvetica', 'I', 13)
        self.set_text_color(100, 100, 100)
        self.set_x(12)
        self.multi_cell(0, 8, '6th Semester Project - Presenter Guide', align='C')
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 9)
        self.set_text_color(128)
        self.set_x(12)
        self.multi_cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title):
        self.ln(2)
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(44, 62, 80)
        self.set_fill_color(220, 230, 240)
        self.set_x(12)
        self.multi_cell(0, 10, title, align='L', fill=True)
        self.ln(4)

    def sub_title(self, title):
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(41, 128, 185)
        self.set_x(12)
        self.multi_cell(0, 8, title, align='L')
        self.ln(2)

    def body_text(self, body):
        self.set_font('helvetica', '', 12)
        self.set_text_color(0, 0, 0)
        self.set_x(12)
        self.multi_cell(0, 8, body, align='L')
        self.ln(4)

    def bullet_point(self, title, desc):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(20, 110, 50)
        self.set_x(12)
        self.multi_cell(0, 7, title, align='L')
        
        self.set_font('helvetica', '', 12)
        self.set_text_color(0, 0, 0)
        self.set_x(12)
        self.multi_cell(0, 7, "- " + desc, align='L')
        self.ln(3)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_left_margin(12)
pdf.set_right_margin(12)

pdf.chapter_title(' 1. Introduction (How to Explain the Project) ')
pdf.body_text(
    "AuraFace is a comprehensive 'Smart Campus' Android application built for our 6th-semester academic project. "
    "If you are explaining this to a teacher, the easiest way to describe it is: 'AuraFace is an all-in-one digital "
    "solution that replaces physical ID cards, paper timetables, and notice boards with a single, smart mobile application. "
    "It connects students, teachers, and admins in real-time.'"
)
pdf.body_text(
    "To make this work, the project is split into two main parts: The Frontend (what you see on the phone) and "
    "the Backend (the hidden brain that processes rules and stores data)."
)

pdf.chapter_title(' 2. The Technologies (Explained Simply) ')

pdf.sub_title('A. The Frontend (The Android App)')
pdf.body_text(
    "The Frontend is the mobile application installed on the student's phone. It is responsible for showing buttons, "
    "fetching user clicks, and displaying beautiful screens."
)
pdf.bullet_point("Language: Kotlin", "A modern, extremely fast language used heavily by Google to build Android apps today. We used it instead of older Java.")
pdf.bullet_point("UI Design: Jetpack Compose", "The newest way to build screens on Android. Instead of dragging and dropping buttons, we write code that 'declares' how the screen should look. It makes animations very smooth.")
pdf.bullet_point("Architecture: MVVM (Model-View-ViewModel)", "Think of it like a restaurant! The View is the customer area (screen), the Model is the ingredients in the back (data), and the ViewModel is the waiter that smoothly passes data between them without freezing the screen.")

pdf.sub_title('B. The Backend (The Server & Brain)')
pdf.body_text(
    "The Backend is a computer (server) that runs 24/7. It holds the Database. When the Android App needs information "
    "(like viewing the timetable), it asks the Backend. The Backend checks its Database and sends the answers back."
)
pdf.bullet_point("Framework: FastAPI (Python)", "A modern tool for building servers in Python. It is called 'Fast' because it is incredibly quick at receiving a request from the phone and instantly giving back data.")
pdf.bullet_point("Database: SQLite / PostgreSQL", "The secure digital filing cabinet. All student passwords, timetables, and movie listings are permanently saved here so they are never lost.")

pdf.add_page()
pdf.sub_title('C. The Bridge (The API / Retrofit)')
pdf.bullet_point("Networking: Retrofit API", "The Android app and the Python server are different technologies. To make them talk to each other over the Wi-Fi/Internet, we use Retrofit. The app sends a 'Request', and the server replies with a 'Response' in a standardized text format called JSON.")

pdf.chapter_title(' 3. Detailed Features (How They Really Work) ')

pdf.sub_title('A. Digital Campus ID Engine')
pdf.bullet_point("What it is", "A virtual ID card stored securely on the user's phone.")
pdf.bullet_point("How to explain it", "Instead of printing physical plastic cards, when a student logs in, the FastAPI Server grabs their details (Name, Roll No, Photo) from the database and sends it securely to the App. The App then draws a beautiful digital ID that cannot be easily faked. This is used anywhere on campus that requires identification.")

pdf.sub_title('B. Dynamic Timetable Management')
pdf.bullet_point("What it is", "A fully editable, role-based weekly schedule viewer.")
pdf.bullet_point("How to explain it", "Students can only 'View' their timetables. However, Teachers and Admins have special permission to 'Edit' them. If an admin tries to create a schedule conflict or enters an invalid date, our Python Backend automatically catches the error (HTTP 422 Validation Error) and prevents it from saving, ensuring the timetable is always correct.")

pdf.sub_title('C. Movies & Sports Hub')
pdf.bullet_point("What it is", "A recreational dashboard for discovering campus extracurricular events.")
pdf.bullet_point("How to explain it", "University isn't just about studying. We built dedicated screens (CampusMoviesScreen and CampusSportsScreen) that fetch lists of upcoming sports events or movie screenings dynamically from our database. If an event is cancelled, the server instantly updates the list on everyone's phone.")

pdf.sub_title('D. Real-time Slot Availability Checker')
pdf.bullet_point("What it is", "A live counting system for limited campus resources (like Labs or Event seating).")
pdf.bullet_point("How to explain it", "If an event only has 50 seats, every time a student registers, the App tells the Server. The Server subtracts 1 from the available seats. If the seat count hits 0, the Server immediately tells the App to block any further bookings, displaying 'Slots Full'.")

pdf.add_page()
pdf.chapter_title(' 4. How to Explain the Step-by-Step Flow ')
pdf.body_text("If a teacher asks 'Show me the exact data flow when a user clicks View Timetable', explain these 4 simple steps:")
pdf.body_text("Step 1 (The Click): The student presses 'Timetable' on the screen. The Jetpack Compose UI tells the ViewModel that the user wants instructions.")
pdf.body_text("Step 2 (The Request): The ViewModel uses the Retrofit Network Client to send a secure HTTP message across the internet saying 'Send me the timetable for Student ID 101'.")
pdf.body_text("Step 3 (The Brain): The Python FastAPI Server receives this message, validates that the student is logged in, and asks the Database to pull up their schedule.")
pdf.body_text("Step 4 (The Result): The server packs those rows into JSON text format and sends it back to the phone. The App decodes it and instantly draws the timetable grid securely on the screen!")

pdf.output("d:/6th Sem/Project/AuraFace_Project_Detailed_Guide.pdf")
print("PDF successfully generated!")
