from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
        }


# Initialize Database
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    filter_status = request.args.get("status", "all")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 5))

    query = Task.query

    if filter_status == "completed":
        query = query.filter_by(completed=True)
    elif filter_status == "notCompleted":
        query = query.filter_by(completed=False)

    tasks = query.paginate(page=page, per_page=size)
    return jsonify(
        {"tasks": [task.to_dict() for task in tasks.items], "totalPages": tasks.pages}
    )


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    new_task = Task(description=data["description"], completed=False)
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict())


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    task = Task.query.get(task_id)
    if task:
        task.description = data.get("description", task.description)
        task.completed = data.get("completed", task.completed)
        db.session.commit()
        return jsonify(task.to_dict())
    return jsonify({"error": "Task not found"}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted"})
    return jsonify({"error": "Task not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
