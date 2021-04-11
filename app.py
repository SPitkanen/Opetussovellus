from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import pdb
import os

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT password FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return redirect("/signup")
    else:
        sql = "SELECT role FROM users WHERE name=:username"
        result = db.session.execute(sql, {"username":username})
        role = result.fetchone()[0]
        hash_value = user[0]
        sql = "SELECT id FROM users WHERE name=:username AND password=:hash_value"
        result = db.session.execute(sql, {"username":username, "hash_value":hash_value})
        user_id = result.fetchone()
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["role"] = role
            session["user_id"] = user_id[0]
            session["csrf_token"] = os.urandom(16).hex()
            return redirect("/frontpage")
        else:
            return redirect("/login")

@app.route("/logout")
def logout():
    del session["username"]
    del session["role"]
    del session["user_id"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/frontpage")
def frontpage():
    if session["role"] == 'student':
        result = db.session.execute("SELECT id, name FROM courses WHERE visible=1")
        courses = result.fetchall()
        return render_template("frontpage.html", courses=courses)
    if session["role"] == 'teacher':
        user_id = session["user_id"]
        sql = "SELECT id, name FROM courses WHERE visible=1 AND teacher_id=:user_id"
        result = db.session.execute(sql, {"user_id":user_id})
        courses = result.fetchall()
        return render_template("frontpage.html", courses=courses)

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "SELECT name FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    users = result.fetchall()
    if users == []:
        sql = "INSERT INTO users (name,password, role) VALUES (:username,:password, 'student')"
        db.session.execute(sql, {"username":username,"password":hash_value})
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/signup")

@app.route("/courses/<string:course_name>/<int:course_id>")
def course(course_name, course_id):
    sql = "SELECT id, content FROM content WHERE course_id=:course_id AND visible=1"
    result = db.session.execute(sql, {"course_id":course_id})
    content = result.fetchall()
    sql = "SELECT id, name FROM tasks WHERE course_id=:course_id AND visible=1"
    result = db.session.execute(sql, {"course_id":course_id})
    tasks = result.fetchall()
    if len(tasks) == 0:
        task_count = 0
    else:
        task_count = len(tasks)
    user_id = session["user_id"]
    sql = "SELECT COUNT(DISTINCT s.task_id) FROM solved s, tasks t WHERE t.course_id=:course_id AND s.task_id=t.id AND s.user_id=:user_id"
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    count = result.fetchone()[0]
    session["course_id"] = course_id
    session["course_name"] = course_name
    return render_template("course.html", course_name=course_name, content=content, tasks=tasks, course_id=course_id, count=count, task_count=task_count)

@app.route("/join/<int:course_id>")
def join(course_id):
    user_id = session["user_id"]
    sql = "INSERT INTO participants (course_id, user_id, attend) VALUES (:course_id, :user_id, 1)"
    db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    db.session.commit()
    return redirect("/frontpage")

@app.route("/students/<int:course_id>")
def students(course_id):
    sql = "SELECT u.name, p.user_id FROM users u, participants p WHERE p.course_id=:course_id AND p.attend=1 AND p.user_id=u.id"
    result = db.session.execute(sql, {"course_id":course_id})
    students = result.fetchall()
    course_name = session["course_name"]
    return render_template("students.html", students=students, course_name=course_name, course_id=course_id)

@app.route("/students/tasks/<int:student_id>")
def student_tasks(student_id):
    course_id = session["course_id"]
    sql = "SELECT DISTINCT t.name FROM tasks t, solved s WHERE s.user_id=:student_id AND s.task_id=t.id AND t.course_id=:course_id"
    result = db.session.execute(sql, {"student_id":student_id, "course_id":course_id})
    tasks = result.fetchall()
    return render_template("student_tasks.html", tasks=tasks, course_id=course_id)

@app.route("/tasks/<int:task_id>")
def tasks(task_id):
    sql = "SELECT id, text FROM choices WHERE task_id=:task_id AND visible=1"
    result = db.session.execute(sql, {"task_id":task_id})
    contents = result.fetchall()
    sql = "SELECT name, description, typ FROM tasks WHERE id=:task_id AND visible=1"
    result = db.session.execute(sql, {"task_id":task_id})
    task = result.fetchone()
    return render_template("tasks.html", task=task, contents=contents, task_id=task_id)

@app.route("/answer/<int:task_id>", methods=["POST"])
def answer(task_id):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    typ = request.form["hide"]
    user_id = session["user_id"]
    path = "/tasks/" + str(task_id)
    if typ == "1":
        usr_answers = request.form.getlist("answer")
        sql = "SELECT id FROM choices WHERE task_id=:task_id AND boolea=1"
        result = db.session.execute(sql, {"task_id":task_id})
        correct_answers = result.fetchall()
        if len(correct_answers) != len(usr_answers):
            return redirect(path)
        else:
            a = True
            i = 0
            for answer in correct_answers:
                if str(answer[0]) != usr_answers[i]:
                    return redirect(path)
                i += 1
            if a:
                sql = "INSERT INTO solved (task_id, user_id, sent) VALUES (:task_id, :user_id, NOW())"
                db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
                db.session.commit()
    if typ == "2":
        answer = request.form["answer"]
        sql = "SELECT text FROM choices WHERE task_id=:task_id AND visible=1"
        result = db.session.execute(sql, {"task_id":task_id})
        correct = result.fetchone()[0]
        if correct == answer:
            sql = "INSERT INTO solved (task_id, user_id, sent) VALUES (:task_id, :user_id, NOW())"
            db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
            db.session.commit()
        else:
            return redirect(path)
    path = "/courses/" + session["course_name"] + "/" + str(session["course_id"])
    return redirect(path)

@app.route("/create_course")
def create_course():
    return render_template("create_course.html")

@app.route("/add_course", methods=["POST"])
def add_course():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    course_name = request.form["name"]
    teacher_id = session["user_id"]
    sql = "SELECT name FROM courses WHERE name=:course_name"
    result = db.session.execute(sql, {"course_name":course_name})
    courses = result.fetchall()
    if len(courses) > 0:
        prev = courses[0]
    else:
        prev = None
    if prev == None:
        sql = "INSERT INTO courses (name, teacher_id, visible) VALUES (:course_name, :teacher_id, 1)"
        db.session.execute(sql, {"course_name":course_name, "teacher_id":teacher_id})
        db.session.commit()
        return redirect("/frontpage")
    return render_template("create_course.html")

@app.route("/remove_task/<int:task_id>")
def remove_task(task_id):
    sql = "SELECT c.id, c.name FROM courses c LEFT JOIN tasks t ON t.course_id=c.id WHERE t.id=:task_id"
    result = db.session.execute(sql, {"task_id":task_id})
    tupl = result.fetchone()
    sql = "UPDATE tasks SET visible=0 WHERE id=:task_id"
    db.session.execute(sql, {"task_id":task_id})
    db.session.commit()
    path = "/courses/" + tupl[1] + "/" + str(tupl[0])
    return redirect(path)

@app.route("/remove_content/<int:content_id>")
def remove_content(content_id):
    sql = "SELECT c.id, c.name FROM courses c, content co WHERE co.course_id=c.id AND co.id=:content_id"
    result = db.session.execute(sql, {"content_id":content_id})
    tupl = result.fetchone()
    sql = "UPDATE content SET visible=0 WHERE id=:content_id"
    db.session.execute(sql, {"content_id":content_id})
    db.session.commit()
    path = "/courses/" + tupl[1] + "/" + str(tupl[0])
    return redirect(path)

@app.route("/courses/<string:course_name>/<int:course_id>/add_text")
def add_text(course_name, course_id):
    return render_template("add_text.html", course_id=course_id)

@app.route("/insert_text/<int:course_id>", methods=["POST"])
def insert_text(course_id):
    content = request.form["content"]
    sql = "INSERT INTO content (course_id, content, visible) VALUES (:course_id, :content, 1)"
    db.session.execute(sql, {"course_id":course_id, "content":content})
    db.session.commit()
    sql = "SELECT c.id, c.name FROM courses c, content co WHERE co.course_id=c.id AND c.id=:course_id"
    result = db.session.execute(sql, {"course_id":course_id})
    tupl = result.fetchone()
    path = "/courses/" + tupl[1] + "/" + str(tupl[0])
    return redirect(path)

@app.route("/courses/<string:course_name>/<int:course_id>/delete_course")
def delete_course(course_name, course_id):
    sql = "UPDATE courses SET visible=0 WHERE id=:course_id"
    db.session.execute(sql, {"course_id":course_id})
    db.session.commit()
    return redirect("/frontpage")

@app.route("/add_task/<int:course_id>")
def add_task(course_id):
    return render_template("create_task.html", course_id=course_id)

@app.route("/create_task/<int:course_id>", methods=["POST"])
def create_task(course_id):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    task_name = request.form["name"]
    description = request.form["description"]
    task_type = request.form["hide"]
    if task_type == "1":
        choices = request.form.getlist("choice")
        booleas = request.form.getlist("boolean")
        sql = "INSERT INTO tasks (course_id, name, description, visible, typ) VALUES (:course_id, :task_name, :description, 1, 1) RETURNING id"
        result = db.session.execute(sql, {"course_id":course_id, "task_name":task_name, "description":description})
        task_id = result.fetchone()[0]
        answers = [0, 0, 0, 0]
        for i in range(0, len(booleas)):
            answers[int(booleas[i])] = 1
        for l in range(0, 4):
            sql = "INSERT INTO choices (task_id, text, boolea, typ, visible) VALUES (:task_id, :text, :boolea, 1, 1)"
            db.session.execute(sql, {"task_id":task_id, "text":choices[l], "boolea":answers[l]})
        db.session.commit()
    if task_type == "2":
        choice = request.form["choice"]
        sql = "INSERT INTO tasks (course_id, name, description, visible, typ) VALUES (:course_id, :task_name, :description, 1, 2) RETURNING id"
        result = db.session.execute(sql, {"course_id":course_id, "task_name":task_name, "description":description})
        task_id = result.fetchone()[0]
        sql = "INSERT INTO choices (task_id, text, boolea, typ, visible) VALUES (:task_id, :text, 1, 2, 1)"
        db.session.execute(sql, {"task_id":task_id, "text":choice})
        db.session.commit()
    sql = "SELECT name FROM courses WHERE id=:course_id"
    result = db.session.execute(sql, {"course_id":course_id})
    course_name = result.fetchone()[0]
    path = "/courses/" + course_name + "/" + str(course_id)
    return redirect(path)