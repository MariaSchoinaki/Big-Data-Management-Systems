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
This launches both the Flask API and Redis server.


### 3. Launch GUI (from host, outside Docker)
```bash
python gui.py
```

Make sure to have dependencies installed (outside Docker for GUI):
```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure
```
project_1_redis/
├── app.py               # Flask API
├── db.py                # SQLAlchemy models + DB init
├── logic.py             # Core meeting logic
├── redis_client.py      # Redis interface
├── scheduler.py         # Meeting timeout scheduler
├── utils.py             # Reusable helpers
├── gui.py               # CustomTkinter GUI
├── test_script.py       # Script for testing endpoints
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

---

## 🧪 Testing
Run the included test script to simulate meeting lifecycle:
```bash
python test_script.py
```

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