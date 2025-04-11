from flask import Flask, request, jsonify
from db import init_db, SessionLocal, User, Meeting
from logic import *
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

app = Flask(__name__)
init_db()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

@app.before_request
def log_request_info():
    logging.info(f"{request.method} {request.path} | args: {request.args} | json: {request.get_json(silent=True)}")

@app.route("/create_user", methods=["POST"])
def create_user():
    session = SessionLocal()
    try:
        data = request.get_json()
        user = User(**data)
        session.add(user)
        session.commit()
        return jsonify({"status": "success", "message": "User created."})
    except IntegrityError:
        session.rollback()
        return jsonify({"status": "error", "message": "User with this email already exists."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/delete_user", methods=["POST"])
def delete_user():
    session = SessionLocal()
    try:
        email = request.json["email"]
        user = session.query(User).get(email)
        if user:
            session.delete(user)
            session.commit()
            return jsonify({"status": "success", "message": "User deleted"})
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/create_meeting", methods=["POST"])
def create_meeting():
    session = SessionLocal()
    try:
        data = request.get_json()
        meeting = Meeting(**data)
        session.add(meeting)
        session.commit()
        return jsonify({"status": "success", "message": "Meeting created"})
    except IntegrityError:
        session.rollback()
        return jsonify({"status": "error", "message": "Meeting ID already exists."}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/delete_meeting", methods=["POST"])
def delete_meeting():
    session = SessionLocal()
    try:
        meetingID = request.json["meetingID"]
        meeting = session.query(Meeting).get(meetingID)
        if meeting:
            session.delete(meeting)
            session.commit()
            return jsonify({"status": "success", "message": "Meeting deleted"})
        else:
            return jsonify({"status": "error", "message": "Meeting not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/get_nearby", methods=["GET"])
def get_nearby():
    try:
        email = request.args["email"]
        x = float(request.args["lat"])
        y = float(request.args["long"])
        return jsonify(get_nearby_active_meetings(email, x, y))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()
    return jsonify(join_meeting(data["email"], data["meetingID"]))

@app.route("/leave", methods=["POST"])
def leave():
    data = request.get_json()
    return jsonify(leave_meeting(data["email"], data["meetingID"]))

@app.route("/active_meetings", methods=["GET"])
def active():
    return jsonify(get_active_meetings())

@app.route("/end_meeting", methods=["POST"])
def end():
    return jsonify(end_meeting(request.json["meetingID"]))

@app.route("/post_message", methods=["POST"])
def post():
    data = request.get_json()
    return jsonify(post_message(data["email"], data["message"]))

@app.route("/get_chat", methods=["GET"])
def chat():
    return jsonify(get_chat(request.args["meetingID"]))

@app.route("/user_messages", methods=["GET"])
def user_messages():
    return jsonify(get_user_messages(request.args["email"]))

@app.route("/user_chat_in_meeting", methods=["GET"])
def user_chat():
    return jsonify(show_user_chat_in_meeting(request.args["email"]))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")