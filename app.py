from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task, StudySession

app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "change-this-to-something-random-later"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///studybuddy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"success": False, "message": "Not logged in"}), 401


# ---------------------------------------------------------
# Serve frontend pages
# ---------------------------------------------------------
@app.route("/")
def home():
    return redirect("/login.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


# ---------------------------------------------------------
# Auth routes
# ---------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or len(password) < 6:
        return jsonify({"success": False, "message": "Please fill all fields correctly."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "An account with that email already exists."}), 400

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"success": True, "user": {"name": user.name, "email": user.email}})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Incorrect email or password."}), 401

    login_user(user)
    return jsonify({"success": True, "user": {"name": user.name, "email": user.email}})


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})


@app.route("/api/me", methods=["GET"])
def me():
    if current_user.is_authenticated:
        return jsonify({"loggedIn": True, "user": {"name": current_user.name, "email": current_user.email}})
    return jsonify({"loggedIn": False})


# ---------------------------------------------------------
# Task routes
# ---------------------------------------------------------
@app.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([t.to_dict() for t in tasks])


@app.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    text = (data.get("text") or "").strip()
    date = data.get("date")

    if not text:
        return jsonify({"success": False, "message": "Task text is required."}), 400

    task = Task(user_id=current_user.id, text=text, date=date, done=False)
    db.session.add(task)
    db.session.commit()
    return jsonify({"success": True, "task": task.to_dict()})


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"success": False, "message": "Task not found."}), 404

    data = request.get_json()
    if "done" in data:
        task.done = data["done"]
    if "text" in data:
        task.text = data["text"]
    if "date" in data:
        task.date = data["date"]

    db.session.commit()
    return jsonify({"success": True, "task": task.to_dict()})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"success": False, "message": "Task not found."}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"success": True})


# ---------------------------------------------------------
# Study session routes (Pomodoro history)
# ---------------------------------------------------------
@app.route("/api/sessions", methods=["GET"])
@login_required
def get_sessions():
    sessions = (
        StudySession.query.filter_by(user_id=current_user.id)
        .order_by(StudySession.id.desc())
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])


@app.route("/api/sessions", methods=["POST"])
@login_required
def create_session():
    data = request.get_json()
    session_entry = StudySession(
        user_id=current_user.id,
        mode=data.get("mode"),
        minutes=data.get("minutes"),
        date=data.get("date"),
        time_label=data.get("timeLabel"),
        partial=data.get("partial", False),
    )
    db.session.add(session_entry)
    db.session.commit()
    return jsonify({"success": True, "session": session_entry.to_dict()})


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
