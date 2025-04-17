# Redis Meeting App

A containerized Python + Redis application for managing and participating in geo-located meetings with chat support. Comes with a custom GUI and full Docker support.

---

## 🚀 Features

- 👤 Create/delete users
- 🗓️ Create/delete meetings with location and time
- 👥 Join/leave/end meetings
- 🗺️ Get active or nearby meetings
- 💬 Post/view chat messages (full or per user)
- 🧑‍💻 GUI using CustomTkinter
- 🐳 Docker + Redis integration

---

## 📦 Requirements

- Python 3.12+
- Docker & Docker Compose

---

## ⚙️ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/project_1_redis.git
cd project_1_redis
```

### 2. Build and run Docker containers
```bash
docker-compose up --build
```
This launches both the Flask API and Redis server. The meeting scheduler will also start running automatically inside the Flask app.

### 3. Launch GUI (from host, outside Docker)
```bash
python gui/gui.py
```
This opens the CustomTkinter GUI that interacts with the running Flask API.

Make sure to have dependencies installed (outside Docker for GUI):
```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure
```
project_1_redis/
├── gui/
│   └── gui.py                 # CustomTkinter GUI
├── src/
│   ├── __init__.py
│   ├── app.py                # Flask API (also starts the scheduler)
│   ├── db.py                 # SQLAlchemy models + DB init
│   ├── logic.py              # Core meeting logic
│   ├── redis_client.py       # Redis interface
│   ├── scheduler.py          # Meeting timeout scheduler logic
│   └── utils.py              # Reusable helpers
├── tests/
│   ├── test_script_easy.py   # Simple test scenario
│   └── test_script_difficult.py # Advanced multi-user test scenario
├── meetings.db               # SQLite database
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── Proj1_Redis.pdf
└── README.md
```

---

## 🧪 Testing
Run either of the included test scripts:
```bash
python tests/test_script_easy.py
python tests/test_script_difficult.py
```

---

### ▶️ Launch Script for GUI
Avoid manual Docker + GUI launching by using a single launcher:

---

## 🔐 Notes
- Meeting IDs and User emails must be unique.
- Redis holds active meetings and chat data.
- SQLite used as persistent local DB.

---

## 🛠️ To Improve
- Input validation (GUI/backend)
- Date pickers + dropdowns in GUI
- Export chat logs
- User authentication (future)