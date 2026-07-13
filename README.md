# CareerCompass AI — Intelligent Career Readiness & Placement Analytics Platform

CareerCompass AI is a production-ready, full-stack AI-powered placement readiness portal. The platform automatically tracks academic performance, quiz assessments, and resume structure to calculate a composite Career Readiness Index, predict placement probabilities using a Random Forest Classifier, identify skill gaps, match candidates with top employers, and generate personalized 30-60-90 day learning roadmaps.

---

## 🛠️ Technology Stack

- **Backend**: Python Flask (Application Factory & Blueprints)
- **Database**: SQLite with SQLAlchemy ORM
- **Machine Learning**: Scikit-Learn (Random Forest Classifier), Pandas, NumPy
- **Security**: Flask-WTF (CSRF Protection), Flask-Login (Session Management), Werkzeug (Password Hashing)
- **Frontend**: HTML5, CSS3 (Glassmorphism & Dark Theme), Bootstrap 5, Chart.js

---

## 🚀 Installation & Launch Instructions

Follow these simple steps in your terminal (Command Prompt or PowerShell) to run CareerCompass AI:

### 1. Clone or Navigate to the Workspace
```bash
cd "C:\Users\LENOVO\OneDrive\Desktop\Career Compass AI"
```

### 2. Install Pinned Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Train the Random Forest Model
This script generates a balanced synthetic dataset of 1,200 student records, fits a Scikit-Learn classifier, and exports model pickle files (`placement_model.pkl` and `scaler.pkl` in the `ml_models/` directory):
```bash
python app/ml/train_model.py
```

### 4. Create and Seed the SQLite Database
This creates all tables and seeds the database with 200 student profiles, 600 assessments, 180 placement logs, 1 admin account, and 1 placement officer account:
```bash
python data/seed_data.py
```

### 5. Launch the Flask Server
```bash
python run.py
```

Open **http://127.0.0.1:5000** in your browser to access the portal!

---

## 🔐 Seeder Accounts Credentials

| Role | Email Address | Password |
|---|---|---|
| **Administrator** | `admin@careercompass.ai` | `Admin@2025!` |
| **Placement Cell Officer** | `officer@careercompass.ai` | `Officer@2025!` |
| **Candidates (Students)** | `aarav.sharma.001@student.edu` | `Student@123` |

---

## 📑 Verification Flow

Confirm the end-to-end user flow by following these steps:
1. **Register**: Create a new student account at `/auth/register`.
2. **Dashboard**: Navigate to your dashboard and verify the empty metrics state.
3. **Profile**: Go to **My Profile** to add academic parameters, projects, and certifications.
4. **ATS Resume**: Upload any PDF resume on the **ATS Resume** page to get keyword scores.
5. **Quiz**: Navigate to **Assessments** and complete a Technical Quiz.
6. **Career Readiness**: Go to **Career Readiness** to view your placement probability calculated by the Random Forest model.
7. **Skill Gap**: Run a **Skill Gap Analysis** against a Software Engineer target role.
8. **Company Match**: Review eligible employer cards on the **Company Match Engine** page.
9. **Timeline**: Generate your **Learning Roadmap** milestone lists.
10. **Report**: Go back to the dashboard and click **Download Report** to export your PDF summary.
