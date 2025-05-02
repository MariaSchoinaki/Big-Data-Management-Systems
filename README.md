# Big Data Management Projects

This repository contains four independent projects developed for the **Big Data Management Systems** course at AUEB (2024-2025). Each project applies a different NoSQL or big data technology: Redis, MongoDB, Neo4j, and Hadoop.

---

## 📌 Project 1: Redis Meeting App

A **Teams/Zoom-inspired platform** designed for **physical meetings**, where participants can join sessions based on their proximity to a meeting's location. It combines **SQLite** for persistent data and **Redis** for real-time meeting management, including chatrooms and participant tracking.

### Features

* Create/delete users and meetings
* Manage participation (join/leave/end meetings)
* Detect nearby active meetings (within 100 meters)
* Real-time chatrooms inside meetings
* Background scheduler to activate/deactivate meetings automatically
* GUI interface for ease of use

### How to Run

**Quick Run:**

1. Ensure Docker Desktop is running.
2. Run `launch.bat` to:

   * Start backend & Redis
   * Open the GUI
   * Cleanly shut down everything on exit

**Manual Run:**

* `docker-compose up --build`
* In another terminal: `python src/gui/gui.py`

### 📂 Project Structure

* `src/`: Backend (Flask + SQLAlchemy) & GUI (CustomTkinter)
* `tests/`: Automated Python scripts for functionality tests
* `docker-compose.yml`, `Dockerfile`, etc.

### Tech Stack

* Python (Flask, SQLAlchemy)
* Redis (Dockerized)
* SQLite
* CustomTkinter GUI
* Docker & Docker Compose

### API Highlights

* `/create_user`, `/delete_user`
* `/create_meeting`, `/delete_meeting`
* `/join`, `/leave`, `/end_meeting`
* `/post_message`, `/get_chat`, `/user_messages`
* `/get_nearby`, `/active_meetings`

---

## 📌 Project 2: MongoDB Student Analytics

A **MongoDB aggregation and analytics project** working with a large `students` collection (\~10,000 entries) created using a randomized `prep.js` script. The project involves querying, transforming, and aggregating student data based on their courses and hobbies.

### Features

* Count students currently taking classes
* Group students by home city
* Identify most popular hobbies
* Compute GPA and other student statistics
* Track classes (completed, in progress, dropped)
* Transform documents with additional fields (e.g., `hobbyist`, `completed_classes`)

### How to Run

1. Install MongoDB Community Server and `mongosh`
2. Load data with:

   ```
   use studentsDB
   load("path/to/prep.js")
   ```
3. Run aggregation commands inside the MongoDB shell

### 📂 Project Structure

### Tech Stack

### API Highlights


* MongoDB 8.x
* MongoDB Shell (mongosh)
* MongoDB Compass (GUI)

---

## 📌 Project 3: Neo4j Graph Database

This project explores **graph databases** using Neo4j, focusing on graph modeling, querying with Cypher, and advanced graph analytics.

### Features

* Graph data modeling
* Cypher queries and traversal
* Network analysis (e.g., shortest paths, community detection)
* Visualization of graph data

### How to Run


### 📂 Project Structure

### Tech Stack

### API Highlights


---

## 📌 Project 4: Hadoop & MapReduce

This project dives into **distributed storage and processing** with Hadoop, demonstrating file system operations (HDFS) and data analysis using MapReduce jobs.

### Features

* Set up Hadoop single-node cluster
* Work with HDFS (upload, read, process data)
* Implement MapReduce jobs for batch processing
* Analyze large datasets

### 📂 Project Structure

### Tech Stack

### API Highlights

---

## Developers

* Nikos Mitsakis
* Maria Schoinaki

> Big Data Management Systems Course @AUEB 2024-2025