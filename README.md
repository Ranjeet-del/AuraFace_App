# 👋 Welcome to AuraFace! 

Hey there! Thanks for checking out **AuraFace**. This repository houses the complete source code for my 6th-semester project, which is a comprehensive **student attendance, monitoring, and placement tracking system**. 

The main goal behind this project is to create an all-in-one platform for students, teachers, and admins to stay synced, track academic and placement progress, and make administrative tasks a little less tedious and a lot more seamless.

---

## 🏗️ What's Inside?

We’ve split this repository into two main parts—the backend engine and the user-facing mobile app:

### 1. 🧠 `AuraFace` (The Backend)
This folder is where the magic happens behind the scenes. It's an API backend (built primarily using Python) that handles:
- **Database & Business Logic:** Managing student, teacher, and placement databases safely via SQLite.
- **Web Dashboard:** Providing a web interface with real-time web socket communication for chats and administrative notices.
- **Attendance & Monitoring Engine:** Handling attendance logs seamlessly.
- **Data Integrations:** Serving endpoints that the mobile app consumes.

### 2. 📱 `AuraFace_App` (The Mobile Client)
This is the native Android application (written in Kotlin) you actually install on your phone. Key features include:
- **Smart Attendance:** Leverages device camera and location capabilities.
- **Placement Tracker:** A detailed dashboard where students can upload and edit their skills, project links, hackathon results, internships, and certifications.
- **Real-Time Push Notifications:** Powered by Firebase Cloud Messaging (FCM) to keep students updated on the fly.
- **Teacher Controls:** Teachers have roles and specific management UIs (like an availability toggle) natively integrated.

---

## 🚀 Key Features
- **Face/Camera integrations:** Core module for attendance/monitoring capabilities.
- **Role-Based Workflows:** Distinct privileges and views for Students, Teachers, and Admins.
- **Real-Time Communications:** WebSocket integration for instant messaging and system-wide announcements.
- **Academic & Placement Tracking:** Robust tracker for tracking resumes, certifications, and project updates.

---

## 🛠️ Tech Stack Snippet
- **Frontend (Android):** Kotlin, XML, Firebase Cloud Messaging, Retrofit
- **Backend:** Python, SQLite (with SQLAlchemy/equivalent ORMs), WebSockets. 
- **Deployment:** Render (for API/Dashboard hosting)

---

## 💡 A Quick Note on the Journey
This project has seen a lot of iteration—from adding the *Placement Tracker* to refining database migrations and introducing real-time chat with a nice web-dashboard. I’m quite proud of how the system architecture (including the frontend-to-backend orchestration) has turned out.

*Feel free to explore the code! If you are wandering around, checking out the Android components in `AuraFace_App/` or the server routes in `AuraFace/app/routes/` is a good place to start!*
