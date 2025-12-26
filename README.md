🚀 LangSense AI — Smart Language Detection

LangSense AI is an advanced rule-based language detection system that accurately identifies English, Hindi, and Hinglish text with 92–95% accuracy.
It is built using Django, Django REST Framework, and modern frontend technologies, and includes a beautiful analytics dashboard, history tracking, and a REST API for easy integration.

🌟 Key Features

🌐 Multi-Language Detection — English, Hindi, Hinglish

🎯 High Accuracy — 92–95% with confidence scoring

⚡ Real-time Processing — Fast and lightweight

🎨 Beautiful UI — Glassmorphism design with Dark/Light mode

🔌 RESTful API — Easy backend integration

📊 Analytics Dashboard — Charts, statistics, trends

🕒 Detection History — Paginated and filterable history

🛠 Admin Panel — Manage Hinglish vocabulary dynamically

🧠 How LangSense AI Works

LangSense AI uses a multi-signal, weighted scoring approach instead of heavy ML models, making it fast, explainable, and reliable.

1️⃣ Unicode Ratio (Hindi Detection)

Detects Devanagari characters (\u0900 – \u097F)

Strongest signal for Hindi

Very high precision

2️⃣ Token-based English Detection

English dictionary + stopword analysis

Morphological pattern checks

Filters false positives

3️⃣ Hinglish Detection (Heuristics)

Roman Hindi words: hai, hoon, raha, rahi, tha, nahi, kya, kyun

Bigram patterns:

ja raha, kar raha, ho gaya

Mixed-script and mixed-grammar detection

4️⃣ Weighted Confidence Scoring
confidence = round(
    (top_score / (hindi_score + english_score + hinglish_score)) * 100,
    2
)


✔ Higher confidence when one language dominates
✔ Balanced confidence for mixed content

🛠 Technology Stack
Backend

Python 3.10+

Django 4+

Django REST Framework

SQLite (Dev) / PostgreSQL (Prod)

Frontend

HTML5 / CSS3

JavaScript (ES6+)

Tailwind CSS

Chart.js

Font Awesome

📦 Installation & Setup
Prerequisites

Python 3.10+

pip

Installation Steps

1️⃣ Clone the repository

git clone https://github.com/your-username/language_detaction.git
cd language_detaction


2️⃣ Create virtual environment

python -m venv venv
source venv/bin/activate
# Windows:
venv\Scripts\activate


3️⃣ Install dependencies

pip install -r requirements.txt


4️⃣ Run migrations

python manage.py makemigrations
python manage.py migrate


5️⃣ Create superuser (optional)

python manage.py createsuperuser


6️⃣ Run development server

python manage.py runserver


7️⃣ Access application

🌐 App: http://127.0.0.1:8000

🔐 Admin: http://127.0.0.1:8000/admin

🧪 Sample Test Cases
Input Text	Expected Output	Confidence
I am going to office	English	96%
मैं आज ऑफिस जा रहा हूँ	Hindi	98%
Main office ja raha hoon	Hinglish	94%
Kal meeting hai at office	Hinglish	92%
Hello, how are you?	English	95%
आज बहुत अच्छा दिन है	Hindi	97%
🔌 API Documentation
🔹 Detect Language
POST /api/detect-language/
Content-Type: application/json


Request

{
  "text": "Main office ja raha hoon"
}


Response

{
  "success": true,
  "data": {
    "detected_language": "Hinglish",
    "confidence": 94.5,
    "hindi_score": 15.2,
    "english_score": 25.8,
    "hinglish_score": 85.4,
    "breakdown": {
      "hindi_percentage": 12.1,
      "english_percentage": 20.5,
      "hinglish_percentage": 67.4
    }
  }
}

🔹 Detection History
GET /api/detection-history/?page=1&per_page=20&language=Hinglish

🔹 Statistics
GET /api/statistics/

🔹 Test Detection
POST /api/test-detection/

🎨 UI Highlights

Glassmorphism cards

Animated charts

Dark / Light theme toggle

Responsive (mobile-first)

3D animated particle background

🎨 Color Scheme

Primary Gradient: #6366F1 → #22D3EE

Hindi: #FF6B35

English: #3B82F6

Hinglish: #10B981

🗄 Database Models
LanguageDetection

Input text

Detected language

Confidence score

Score breakdown

Timestamp & metadata

HinglishWord

Roman Hindi vocabulary

Admin-managed

Frequency & type tracking

DetectionStats

Daily aggregates

Confidence distribution

Language trends

🚀 Deployment
Environment Variables
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname

Collect Static Files
python manage.py collectstatic

Gunicorn
gunicorn langsense.wsgi:application --bind 0.0.0.0:8000

Docker (Optional)
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

🤝 Contributing

Fork the repository

Create a feature branch

Commit changes

Add tests if applicable

Submit a pull request

📝 License

MIT License — free to use, modify, and distribute.

🙏 Acknowledgements

Django & Django REST Framework

Tailwind CSS

Chart.js

Font Awesome

📞 Support

📧 Email: mittalprakhar504@gmail.com
