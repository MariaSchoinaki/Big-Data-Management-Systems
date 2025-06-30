# Big Data Management Projects

This repository includes four independent and production-grade projects developed for the course **Big Data Management Systems** at the **Athens University of Economics and Business (AUEB)** during the academic year **2024–2025**.

Each project demonstrates practical application of a different **NoSQL** or **Big Data** technology and follows a real-world data processing scenario using modern tools and deployment techniques.

## Project Index

| No. | System     | Technology            | Focus Area                                                           |
|-----|------------|------------------------|----------------------------------------------------------------------|
| 1   | Redis      | Key-Value Store        | Real-time meeting management with location-based participation       |
| 2   | MongoDB    | Document Store         | Aggregation pipelines and document analytics on student data         |
| 3   | Neo4j      | Graph Database         | Modeling and querying of MOOC learner-course interactions            |
| 4   | StreamProc | Azure Stream Analytics | Real-time ATM stream processing and fraud pattern detection          |

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

### ▶️ How to Run

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

* `src/`: Backend (Flask + SQLAlchemy)
* `tests/`: Automated Python scripts for functionality tests
* `gui/`: User Interface, GUI (CustomTkinter)
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

### ▶️ How to Run

1. Install MongoDB Community Server and `mongosh`
2. Load data with:

   ```
   use studentsDB
   load("path/to/prep.js")
   ```
3. Run aggregation commands inside the MongoDB shell

### 📂 Project Structure

* `data/`: Input data or prep scripts (e.g., `prep.js`)
* `output.txt`: Aggregation results or log output

### Tech Stack

* MongoDB Shell
* MongoDB Compass
* BSON Aggregations

### API Highlights

* MongoDB 8.x
* MongoDB Shell (mongosh)
* MongoDB Compass (GUI)

---

## 📌 Project 3: Neo4j Graph Database

This project explores **graph databases** using Neo4j, focusing on graph modeling, querying with Cypher, and advanced graph analytics for a MOOC (Massive Open Online Course) platform.

### Features

* Graph data modeling of students, courses, completions, and follow relationships.
* Cypher queries for path traversal, influence detection, and structural analysis.
* Compute:
  - Shortest paths between users.
  - Shared course enrollments.
  - Users with high follow counts.
* Perform **community detection**, **influence ranking**, and **graph projections**.
* Clean schema design with labels, relationships, and constraints.
* Visualization using Neo4j Desktop UI and browser tools.

### ▶️ How to Run

1. **Install Neo4j Desktop** and create a local project.
2. Extract the `act-mooc.tar.gz` file and import its contents into Neo4j.
3. Open `cypher_queries.txt` and execute the queries in Neo4j Browser or Desktop.
4. To view programmatic analysis, open `solution.ipynb` and run it in Jupyter Notebook (install dependencies via `requirements.txt`).

---

### 📂 Project Structure

* `results/`: Query results, metrics, and visual outputs
* `act-mooc.tar.gz`: Dataset archive containing MOOC interaction data
* `cypher_queries.txt`: Saved Cypher queries for Neo4j analysis
* `requirements.txt`: Python dependencies for `solution.ipynb`
* `solution.ipynb`: Jupyter Notebook with additional Cypher logic and outputs

---

### Tech Stack

* **Neo4j Desktop** – Local graph database engine
* **Cypher** – Graph query language for modeling and analysis
* **Jupyter Notebook** – Additional experimentation and analysis
* **Python** – Scripting and graph analysis
* **Graph Algorithms** – Shortest paths, communities, centrality metrics

---

### API Highlights

While Neo4j is primarily driven through **Cypher queries**, key patterns used in this project include:

* `MATCH`, `MERGE`, and `CREATE` for graph modeling
* `MATCH (a)-[:FOLLOWS]->(b)` for social links
* `shortestPath()` for pathfinding
* `apoc.*` procedures for advanced analytics (if enabled)
* `CALL db.schema.visualization()` for inspecting schema design

---

## 📌 Project 4: Azure Stream Analytics – Real-Time ATM Transactions

This project showcases real-time stream processing using **Azure Stream Analytics**, leveraging simulated **ATM transaction data**. Using **Event Hub**, **Blob Storage**, and **Stream Analytics Query Language**, we developed a live analytics pipeline for fraud detection and operational insights.

### Features

- **Sliding, Tumbling, and Hopping Window Aggregations**
- Detect high-frequency transactions and spatial inconsistencies
- Integrate ATM, area, and customer metadata using stream joins
- Output to **Azure Blob Storage** for logging or visualization

### ▶️ How to Run

1. **Create an Azure Free Trial Account**
2. **Set up Event Hub + Blob Storage**
3. **Use `Generator.html`** to push events to Event Hub
4. **Configure Stream Analytics Job:**
   - Add Event Hub and `*.json` files as inputs
   - Add Blob Storage as output
5. **Deploy Queries** using the Stream Analytics dashboard
6. **View Output** in Blob Storage or visualize via Power BI

### 📂 Project Structure

* `Reference_Data/`: JSON files for static lookup data (e.g., customers, ATMs, regions)
* `results/`: Query results and logs from stream execution
* `screenshots/`: Visual evidence of query outputs and dashboard integrations


### Tech Stack

- **Azure Event Hub** – real-time event ingestion
- **Azure Stream Analytics** – SQL-based stream query engine
- **Azure Blob Storage** – output sink for results
- **Stream Analytics Query Language (SQL-like)**
- **RedDog SAS Generator** – secure event publishing

### Queries Implemented

1. **Sliding Window (10 min)**: Sum of `Type=0` at `ATMCode=21`
2. **Tumbling Window (1 hr)**: Sum of `Type=1` at `ATMCode=21`
3. **Hopping Window (1 hr, every 30min)**: Same as above, overlapping windows
4. **Sliding by ATMCode**: Sum `Type=1` per ATM over 1 hour
5. **Tumbling by Area Code**: Sum `Type=1` transactions joined with ATM metadata
6. **Tumbling by City & Gender**: Joined across `atm.json`, `area.json`, and `customer.json`
7. **Alert Rule 1**: If customer has 2+ `Type=1` transactions in a 1hr window
8. **Alert Rule 2**: Alert if customer’s area ≠ ATM’s area


---

## Developers

> **Maria Schoinaki, BSc Student**  
> Department of Informatics, Athens University of Economics and Business  
> p3210191@aueb.gr  
>
> **Nikos Mitsakis, BSc Student**  
> Department of Informatics, Athens University of Economics and Business  
> p3210122@aueb.gr  


> Big Data Management Systems Course @AUEB 2024-2025