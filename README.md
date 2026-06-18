# Lumenor AI Attendance Platform

Welcome to the **Lumenor AI Attendance Platform**. 

## 🚀 Quick Start Guide

To start the platform, you just need to run one command. The startup script will automatically check for any missing packages, install them if necessary, and launch the application.

1. Open a PowerShell terminal in this folder.
2. Run the start script:
   ```powershell
   .\start.ps1
   ```

### What happens when you run `start.ps1`?
*   It automatically checks if you have all required Python packages (like `streamlit`, `opencv`, `dlib`, `face_recognition`, `webrtcvad`).
*   If they are missing, it runs `install.ps1` to safely install them.
*   It cleans up any old or frozen app sessions in the background.
*   It starts the **Landing Page** at `http://127.0.0.1:5002`
*   It starts the **App Portal** at `http://localhost:8501`

---

## 🔐 Environment Variables and Secrets Setup

Because this project connects to external services like Supabase and Fly.io, you must securely store your API keys. **Never commit `.env` or `secrets.toml` to GitHub!**

### 1. Local Development
For the app to work on your machine, you need to create two files:

*   **`src/database/.env`** (for the database connection)
    ```env
    SUPABASE_URL=your-project-url
    SUPABASE_KEY=your-project-anon-key
    ```
*   **`.streamlit/secrets.toml`** (for Streamlit Cloud deployments, optional locally but good practice)
    ```toml
    SUPABASE_URL = "your-project-url"
    SUPABASE_KEY = "your-project-anon-key"
    ```

### 2. GitHub Secrets (For Automated Deployments)
If you want GitHub Actions (like `fly.yml`) to automatically deploy your app, you need to push these secrets to **GitHub Repository Secrets**.

1. Go to your repository on GitHub.
2. Click **Settings** (the tab below your repository name).
3. On the left sidebar, scroll down to **Security** and expand **Secrets and variables**.
4. Click **Actions**.
5. Click **New repository secret** and add the following:
    *   Name: `FLY_API_TOKEN` | Value: *(Your Fly.io authentication token)*
    *   Name: `SUPABASE_URL` | Value: *(Your Supabase URL)*
    *   Name: `SUPABASE_KEY` | Value: *(Your Supabase Anon Key)*

### 3. Fly.io Secrets (For Production Environment)
If you deploy to Fly.io, your production server needs these environment variables too. You can push them from your local `.env` file using the Fly CLI:
```bash
fly secrets set SUPABASE_URL=your-project-url SUPABASE_KEY=your-project-anon-key
```