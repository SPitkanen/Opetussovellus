from db import db
from flask import session, redirect
import users

def create_task_1(course_id, task_name, description, choices, correct_choices):
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
    
def create_task_2(course_id, choice, task_name, description):
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
    sql = "SELECT name, description, typ FROM tasks WHERE id=:task_id AND visible=1 ORDER BY id"
    result = db.session.execute(sql, {"task_id":task_id})
    task = result.fetchone()
    
    return task

def get_task_choices(task_id):
    sql = "SELECT id, text FROM choices WHERE task_id=:task_id AND visible=1"
    result = db.session.execute(sql, {"task_id":task_id})
    choices = result.fetchall()

    return choices

def answer_task_1(course_id, task_id, usr_answers):
    user_id = session["user_id"]
    if users.check_attending(course_id):
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

def answer_task_2(course_id, task_id, answer):
    user_id = session["user_id"]
    if users.check_attending(course_id):
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

def get_solved_tasks(course_id, student_id):
    sql = "SELECT DISTINCT t.name, t.id FROM tasks t, solved s WHERE s.user_id=:student_id AND s.task_id=t.id AND t.course_id=:course_id AND t.visible=1 ORDER BY t.id"
    result = db.session.execute(sql, {"student_id":student_id, "course_id":course_id})
    tasks_list = result.fetchall()
    return tasks_list

def get_tasks(course_id):
    sql = "SELECT DISTINCT id, name FROM tasks WHERE course_id=:course_id AND visible=1"
    result = db.session.execute(sql, {"course_id":course_id})
    tasks = result.fetchall()

    return tasks

def get_solved_count(course_id):
    user_id = session.get("user_id")
    sql = "SELECT COUNT(DISTINCT s.task_id) FROM solved s, tasks t WHERE t.course_id=:course_id AND s.task_id=t.id AND s.user_id=:user_id AND t.visible=1"
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    
    solved_count = result.fetchone()[0]
    return solved_count

def get_corrected_task_list(course_id):
    tasks = get_tasks(course_id)
    student_id = session.get("user_id")
    solved_tasks = get_solved_tasks(course_id, student_id)
    corrected_list = [list(range(3)) for i in range(len(tasks))]

    i = 0
    for task in tasks:
        correct = False
        for corr in solved_tasks:
            if corr[1] == task[0]:
                corrected_list[i][0] = task[0]
                corrected_list[i][1] = task[1]
                corrected_list[i][2] = 1
                correct = True
        print(correct)
        if correct == False:
            corrected_list[i][0] = task[0]
            corrected_list[i][1] = task[1]
            corrected_list[i][2] = 0
        i += 1
    print(corrected_list)
    return corrected_list