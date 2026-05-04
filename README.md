# ⚡ Foresight — AI-Powered Personal Finance Tracker

> Predict your future spending before it happens.

Foresight is a full-stack web application that tracks personal expenses, 
trains machine learning models on your spending history, and predicts 
next month's expenditure by category — alerting you before you exceed 
your budget.

---

## 🚀 Live Demo
> Coming soon — deployed on Railway

---

## 🧠 What Makes This Interesting

Most finance apps tell you what you **already spent**.  
Foresight tells you what you **will spend** — before the month begins.

- Trains **4 ML models** (Linear Regression, Random Forest, KNN, SVM)
- Automatically selects the best model based on MAE and RMSE
- Generates **next-month predictions** per spending category
- Triggers **budget alerts** when predictions exceed limits
- Re-trains with one click via the dashboard

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x |
| Database | PostgreSQL 16 |
| ML Engine | Scikit-learn, Pandas, Joblib |
| Frontend | Bootstrap 5, Chart.js |
| Auth | Django built-in authentication |
| Deployment | Railway (coming soon) |

---

## 📊 ML Pipeline

Raw Transactions (PostgreSQL)
↓
Feature Engineering (Pandas)
→ month, quarter, rolling avg, lag features
↓
Train 4 Models (Scikit-learn)
→ Linear Regression
→ Random Forest
→ KNN
→ SVM
↓
Evaluate (MAE + RMSE)
↓
Best Model Saved (.pkl via Joblib)
↓
Predictions → PostgreSQL → Dashboard

---

## 📁 Project Structure
Foresight/
├── core/
│   ├── ml/
│   │   ├── features.py      # Feature engineering
│   │   ├── registry.py      # 4 model definitions
│   │   ├── trainer.py       # Train + evaluate all models
│   │   ├── predictor.py     # Generate predictions
│   │   └── pipeline.py      # Orchestration
│   ├── templates/core/      # HTML templates
│   ├── models.py            # DB schema (5 tables)
│   ├── views.py             # Django views
│   ├── importer.py          # CSV data pipeline
│   └── alerts.py            # Budget alert engine
├── foresight/
│   └── settings.py
├── sample_data/             # Sample CSV files
├── ml_models/               # Saved .pkl model files
└── requirements.txt

---

## ⚙️ Local Setup

```bash
# Clone the repo
git clone https://github.com/mansab019/foresight.git
cd foresight

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Import sample data
python manage.py shell
# >>> from core.importer import import_csv
# >>> from django.contrib.auth.models import User
# >>> user = User.objects.get(username='your_username')
# >>> import_csv('sample_data/transactions.csv', user)

# Run ML pipeline
# >>> from core.ml.pipeline import run_ml_pipeline
# >>> run_ml_pipeline(user)

# Start server
python manage.py runserver
```

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| transactions | Every expense recorded |
| budgets | Monthly spending limits per category |
| predictions | ML model output |
| alerts | Budget breach notifications |
| users | Django built-in auth |

---

## 📈 ML Model Results

| Model | MAE | RMSE |
|-------|-----|------|
| Linear Regression | 0.0 | 0.0 |
| Random Forest | 287.42 | 404.86 |
| KNN | 1154.74 | 1539.43 |
| SVM | 1136.02 | 1287.84 |

*Note: Linear Regression achieved perfect scores on this structured 
dataset. In production with more varied real-world data, Random Forest 
would likely perform better.*

---

## 🔮 Future Improvements

- [ ] Bank statement PDF parser
- [ ] Plaid API integration for live bank feeds
- [ ] Email/SMS alerts
- [ ] Multi-user support
- [ ] Docker containerization
- [ ] CI/CD with GitHub Actions

---

## 👤 Author

**Mansab Ali**  
BS Computer Science — The Superior University  
GitHub: [@mansab019](https://github.com/mansab019)

---

## 📄 License
MIT License
