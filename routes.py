from app import app
from flask import render_template, request, redirect, flash
import users, courses, tasks

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if users.login(username, password):
        return redirect("/frontpage")
    else:
        flash("Kirjautuminen epäonnistui")
        return render_template("index.html")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.signup(username, password):
            users.login(username, password)
            flash("Tunnuksen luominen onnistui, olet kirjautunut sisään")
            return redirect("/frontpage")
        else:
            flash("Tunnuksen luominen ei onnistunut")
            return redirect("/signup")

@app.route("/frontpage")
def frontpage():
    if users.check_logged() == False:
        return redirect("/")
    course_list = courses.frontpage()
    return render_template("frontpage.html", courses=course_list)

@app.route("/create_course", methods=["GET", "POST"])
def add_course():
    if users.check_logged() == False:
        return redirect("/")
    if request.method == "GET":
        return render_template("create_course.html")
    if request.method == "POST":
        course_name = request.form["name"]
        token = request.form["csrf_token"]
        message = courses.new_course(course_name, token)

        flash(message)
        return redirect("/frontpage")

@app.route("/courses/<string:course_name>/<int:course_id>")
def course(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    content = courses.get_contents(course_name, course_id)
    course_tasks = courses.get_tasks(course_id)
    on_course = tasks.check_attending(course_id)

    if users.role() == 'student':
        solved_count = courses.get_solved_count(course_id)
        task_count = len(course_tasks)
        return render_template("course.html", course_name=course_name, course_id=course_id, content=content, course_tasks=course_tasks, solved_count=solved_count, task_count=task_count, on_course=on_course)

    return render_template("course.html", course_name=course_name, course_id=course_id, content=content, course_tasks=course_tasks)

@app.route("/join/<string:course_name>/<int:course_id>", methods=["POST"])
def join(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    message = courses.join_course(course_name, course_id)
    flash(message)
    
    return redirect("/courses/" + course_name + "/" + str(course_id))

@app.route("/exit_course/<string:course_name>/<int:course_id>", methods=["POST"])
def exit(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    message = courses.exit_course(course_name, course_id)
    flash(message)
    
    return redirect("/courses/" + course_name + "/" + str(course_id))

# Show list of students attending course
@app.route("/<string:course_name>/<int:course_id>/students")
def students(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    students = courses.show_students(course_id)
    
    return render_template("students.html", students=students, course_name=course_name, course_id=course_id)

# Show list of tasks correctly answered by student
@app.route("/<string:course_name>/<int:course_id>/students/tasks/<int:student_id>")
def student_tasks(course_name, course_id, student_id):
    if users.check_logged() == False:
        return redirect("/")
    tasks_list = courses.show_students_tasks(course_id, student_id)
    
    return render_template("student_tasks.html", tasks_list=tasks_list, course_name=course_name, course_id=course_id)

@app.route("/<string:course_name>/<int:course_id>/tasks/<int:task_id>")
def show_task(course_name, course_id, task_id):
    if users.check_logged() == False:
        return redirect("/")
    task = tasks.get_task(task_id)
    contents = tasks.get_task_choices(task_id)
    
    return render_template("tasks.html", task=task, contents=contents, course_name=course_name, course_id=course_id, task_id=task_id)

@app.route("/<string:course_name>/<int:course_id>/tasks/answer/<int:task_id>", methods=["GET","POST"])
def answer(course_name, course_id, task_id):
    if users.check_logged() == False:
        return redirect("/")
    typ = request.form["hide"]
    token = request.form["csrf_token"]
    message = ""
    if typ == "1":
        usr_answers = request.form.getlist("answer")
        message = tasks.answer_task_1(course_id, task_id, usr_answers, token)
    
    if typ == "2":
        answer = request.form["answer"]
        message = tasks.answer_task_2(course_id, task_id, answer, token)
    
    flash(message)
    return redirect("/" + course_name + "/" + str(course_id) + "/tasks/" + str(task_id))

@app.route("/<string:course_name>/<int:course_id>/remove_task/<int:task_id>")
def remove_task(course_name, course_id, task_id):
    if users.check_logged() == False:
        return redirect("/")
    message = tasks.delete_task(course_name, task_id)

    flash(message)
    return redirect("/courses/" + course_name + "/" + str(course_id))

@app.route("/<string:course_name>/<int:course_id>/remove_content/<int:content_id>")
def remove_content(course_name, course_id, content_id):
    if users.check_logged() == False:
        return redirect("/")
    courses.delete_content(content_id)

    return redirect("/courses/" + course_name + "/" + str(course_id))

@app.route("/courses/<string:course_name>/<int:course_id>/add_text", methods=["GET", "POST"])
def add_text(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    if request.method == "GET":
        return render_template("add_text.html", course_name=course_name, course_id=course_id)
    if request.method == "POST":
        content = request.form["content"]
        message = courses.add_content(course_id, content)

        flash(message)
        return redirect("/courses/" + course_name + "/" + str(course_id))

@app.route("/courses/<string:course_name>/<int:course_id>/delete_course")
def delete_course(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    message = courses.remove_course(course_name, course_id)
    flash(message)
    return redirect("/frontpage")

@app.route("/<string:course_name>/<int:course_id>/add_task", methods=["GET", "POST"])
def add_task(course_name, course_id):
    if users.check_logged() == False:
        return redirect("/")
    if request.method == "GET":
        return render_template("create_task.html", course_name=course_name, course_id=course_id)
    if request.method == "POST":
        task_name = request.form["name"]
        description = request.form["description"]
        task_type = request.form["hide"]
        token = request.form["csrf_token"]

        if task_type == "1":
            choices = request.form.getlist("choice")
            correct_choices = request.form.getlist("correct")

            message = tasks.create_task_1(course_id, task_name, description, choices, correct_choices, token)
            flash(message)
            return redirect("/" + course_name + "/" + str(course_id) + "/add_task")
        
        if task_type == "2":
            choice = request.form["choice"]

            message = tasks.create_task_2(course_id, choice, task_name, description, token)
            flash(message)
            return redirect("/" + course_name + "/" + str(course_id) + "/add_task")

    