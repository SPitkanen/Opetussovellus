from db import db
from flask import session, redirect

def create_task_1(course_id, task_name, description, choices, correct_choices, token):
    if session["csrf_token"] != token:
        abort(403)
    if task_name == "":
        return "Nimeä tehtävä!"
    for i in range(0, 4):
        if choices[i] == "":
            return "Ei tyhjiä vastauksia!"

    sql = "INSERT INTO tasks (course_id, name, description, visible, typ) VALUES (:course_id, :task_name, :description, 1, 1) RETURNING id"
    result = db.session.execute(sql, {"course_id":course_id, "task_name":task_name, "description":description})
    task_id = result.fetchone()[0]
    
    answers = [0, 0, 0, 0]
    for i in range(0, len(correct_choices)):
        answers[int(correct_choices[i])] = 1
    
    for l in range(0, 4):
        sql = "INSERT INTO choices (task_id, text, correct, typ, visible) VALUES (:task_id, :text, :boolea, 1, 1)"
        db.session.execute(sql, {"task_id":task_id, "text":choices[l], "boolea":answers[l]})

    db.session.commit()
    return "Tehtävä " + task_name + " lisätty!"
    
def create_task_2(course_id, choice, task_name, description, token):
    if session["csrf_token"] != token:
        abort(403)
    if task_name == "":
        return "Nimeä tehtävä!"
    if choice == "":
        return "Lisää vastaus!"

    sql = "INSERT INTO tasks (course_id, name, description, visible, typ) VALUES (:course_id, :task_name, :description, 1, 2) RETURNING id"
    result = db.session.execute(sql, {"course_id":course_id, "task_name":task_name, "description":description})
    task_id = result.fetchone()[0]
    
    sql = "INSERT INTO choices (task_id, text, correct, typ, visible) VALUES (:task_id, :text, 1, 2, 1)"
    db.session.execute(sql, {"task_id":task_id, "text":choice})
    db.session.commit()
   
    return "Tehtävä " + task_name + " lisätty!"

def get_task(task_id):
    sql = "SELECT name, description, typ FROM tasks WHERE id=:task_id AND visible=1"
    result = db.session.execute(sql, {"task_id":task_id})
    task = result.fetchone()
    
    return task

def get_task_choices(task_id):
    sql = "SELECT id, text FROM choices WHERE task_id=:task_id AND visible=1"
    result = db.session.execute(sql, {"task_id":task_id})
    choices = result.fetchall()

    return choices

def answer_task_1(course_id, task_id, usr_answers, token):
    if session["csrf_token"] != token:
        abort(403)
    
    user_id = session["user_id"]
    if check_attending(course_id):
        sql = "SELECT id FROM choices WHERE task_id=:task_id AND correct=1"
        result = db.session.execute(sql, {"task_id":task_id})
        correct_answers = result.fetchall()
        if len(correct_answers) != len(usr_answers):
            return "Väärin!"
        else:
            i = 0
            for answer in correct_answers:
                if str(answer[0]) != usr_answers[i]:
                    return "Väärin!"
                i += 1
            sql = "INSERT INTO solved (task_id, user_id, sent) VALUES (:task_id, :user_id, NOW())"
            db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
            db.session.commit()
            return "Oikein!"
    return "Ilmoittaudu kurssille ratkoaksesi tehtäviä!"

def answer_task_2(course_id, task_id, answer, token):
    if session["csrf_token"] != token:
        abort(403)

    user_id = session["user_id"]
    if check_attending(course_id):
        sql = "SELECT text FROM choices WHERE task_id=:task_id AND visible=1"
        result = db.session.execute(sql, {"task_id":task_id})
        correct_answer = result.fetchone()

        if correct_answer[0] == answer:
            sql = "INSERT INTO solved (task_id, user_id, sent) VALUES (:task_id, :user_id, NOW())"
            db.session.execute(sql, {"task_id":task_id, "user_id":user_id})
            db.session.commit()
            return  "Oikein!"
        else:
            return "Väärin!"
    return "Ilmoittaudu kurssille ratkoaksesi tehtäviä!"

def delete_task(course_name, task_id):
    sql = "UPDATE tasks SET visible=0 WHERE id=:task_id"
    db.session.execute(sql, {"task_id":task_id})
    db.session.commit()
    
    return "Tehtävä poistettu!"

def check_attending(course_id):
    user_id = session["user_id"]
    sql = "SELECT COALESCE((SELECT attend FROM participants WHERE course_id=:course_id AND user_id=:user_id AND attend=1), 0)"
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    attend = result.fetchone()[0]
    if attend == 0:
        return False
    return True

def check_logged():
    if not session.username:
        return redirect("/")