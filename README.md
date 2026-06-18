<div align="center">
  <img src="./static/img/app_logo.png" alt="Lumenor AI Logo" width="120" />
  <h1>Lumenor AI Attendance Platform</h1>
  <p><strong>A highly secure, biometric attendance system utilizing Face Recognition, Voice Matching, and Geofencing.</strong></p>

  <p>
    <a href="https://www.python.org/downloads/release/python-390/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
    <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"></a>
    <a href="https://supabase.com/"><img src="https://img.shields.io/badge/Supabase-3ECF8E?logo=supabase&logoColor=white" alt="Supabase"></a>
    <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white" alt="OpenCV"></a>
  </p>
</div>

---

## 📖 About The Project

**Lumenor AI** is an advanced, multi-modal attendance tracking platform designed for modern enterprises and educational institutions. It completely eliminates buddy-punching and location-spoofing by combining three powerful verification layers:

1. **Facial Recognition**: High-accuracy face detection and matching using `dlib` and OpenCV.
2. **Voice Biometrics**: Audio processing and speaker verification using `webrtcvad` and `resemblyzer`.
3. **Geofencing**: Location-based verification ensuring the user is physically within the authorized radius using `geopy`.

The platform consists of a responsive **Flask Landing Page** and a highly interactive **Streamlit Dashboard** for administrators and employees, all powered by a real-time **Supabase** backend.

---

## ✨ Key Features

*   **🔒 Triple-Layer Verification**: Face, Voice, and GPS location must all pass to log attendance.
*   **🏢 Multi-Tenant Architecture**: Supports multiple companies/organizations with isolated data.
*   **📡 Real-Time Dashboard**: Live attendance tracking, leave requests, and audit logs.
*   **📍 Dynamic Geofencing**: Administrators can set custom GPS coordinates and allowed radiuses for their offices.
*   **📸 Automated Enrollment**: Employees can enroll their facial and vocal biometrics directly through the web interface.
*   **🛡️ Audit & Security**: Full tracking of failed attempts, location spoofing, and system overrides.

---

## 🛠️ Technology Stack

*   **Frontend / UI**: [Streamlit](https://streamlit.io/), [Flask](https://flask.palletsprojects.com/) (Landing Page), HTML/CSS
*   **Backend & Database**: [Supabase](https://supabase.com/) (PostgreSQL + Realtime APIs)
*   **AI / ML Libraries**: 
    *   `face_recognition` / `dlib` (Facial Embeddings)
    *   `resemblyzer` / `webrtcvad` (Voice Verification)
    *   `OpenCV` (Image Processing)
*   **Geolocation**: `geopy`

---

## 🚀 Getting Started (Local Development)

It is incredibly simple to run Lumenor AI on your local machine.

### Prerequisites
*   Python 3.9 or higher
*   Git

### 1. Clone the repository
```bash
git clone https://github.com/vamsi-2386/ai-attendance-app.git
cd ai-attendance-app
```

### 2. Configure Environment Variables
You will need a Supabase project to run the database. Once created, add your API keys to the application:

1. Create a `.env` file in the `src/database/` folder:
    ```env
    SUPABASE_URL=your-project-url
    SUPABASE_KEY=your-project-anon-key
    ```
2. Create a `secrets.toml` file in the `.streamlit/` folder:
    ```toml
    SUPABASE_URL = "your-project-url"
    SUPABASE_KEY = "your-project-anon-key"
    ```
*(Note: These files are ignored by git to protect your credentials).*

### 3. Start the Application
To run the app, simply execute the `start.ps1` script. 
This script will **automatically install all required dependencies** (including the complex C++ libraries for OpenCV and Dlib) and start both the landing page and the main portal.

```powershell
.\start.ps1
```

Once running, you can access:
*   **Landing Page**: [http://127.0.0.1:5002](http://127.0.0.1:5002)
*   **App Portal**: [http://localhost:8501](http://localhost:8501)

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/vamsi-2386/ai-attendance-app/issues).

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).