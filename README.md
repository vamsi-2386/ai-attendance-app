# Lumenor AI Attendance Platform

Welcome to the **Lumenor AI Attendance Platform**. 

## 🚀 Quick Start Guide

To start the platform locally, you just need to run one command. The startup script will automatically check for any missing packages, install them safely, and launch the application.

1. Open a PowerShell terminal in this folder.
2. Run the start script:
   ```powershell
   .\start.ps1
   ```

### What happens when you run `start.ps1`?
*   It automatically checks if you have all required Python packages (like `streamlit`, `opencv`, `dlib`, `face_recognition`, `webrtcvad`).
*   If they are missing, it runs `install.ps1` to automatically safely install them.
*   It cleans up any old or frozen app sessions in the background.
*   It starts the **Landing Page** at `http://127.0.0.1:5002`
*   It starts the **App Portal** at `http://localhost:8501`

---

## 🔐 Environment Variables

For the app to connect to the database locally, you need to create two simple configuration files with your API keys.

1. Create a file named **`.env`** inside the **`src/database/`** folder:
    ```env
    SUPABASE_URL=your-project-url
    SUPABASE_KEY=your-project-anon-key
    ```

2. Create a file named **`secrets.toml`** inside the **`.streamlit/`** folder:
    ```toml
    SUPABASE_URL = "your-project-url"
    SUPABASE_KEY = "your-project-anon-key"
    ```

*Note: Never commit your `.env` or `secrets.toml` files to Git. They are already ignored in the `.gitignore`.*