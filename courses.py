from db import db
from flask import session
import tasks


def frontpage():
    if session.get("role") == 'student':
        result = db.session.execute("SELECT id, name FROM courses WHERE visible=1")
        courses = result.fetchall()
        return courses
    if session.get("role") == 'teacher':
        user_id = session.get("user_id")
        sql = "SELECT id, name FROM courses WHERE visible=1 AND teacher_id=:user_id"
        result = db.session.execute(sql, {"user_id":user_id})
        courses = result.fetchall()
        return courses

def new_course(course_name, token):
    if session["csrf_token"] != token:
        abort(403)
    
    teacher_id = session["user_id"]
    try:
        sql = "INSERT INTO courses (name, teacher_id, visible) VALUES (:course_name, :teacher_id, 1) RETURNING id"
        result = db.session.execute(sql, {"course_name":course_name, "teacher_id":teacher_id})
        db.session.commit()
        return "Uusi kurssi " + course_name + " luotu!"
    except:
        return "Kurssi " + course_name + " on jo olemassa!"

def remove_course(course_name, course_id):
    try:
        sql = "UPDATE courses SET visible=0 WHERE id=:course_id"
        db.session.execute(sql, {"course_id":course_id})
        db.session.commit()
        return "Kurssi " + course_name + " poistettu"
    except:
        return "Kurssin " + course_name + " poistaminen epäonnistui"

def add_content(course_id, content):
    try:
        sql = "INSERT INTO content (course_id, content, visible) VALUES (:course_id, :content, 1) RETURNING id"
        result = db.session.execute(sql, {"course_id":course_id, "content":content})
        db.session.commit()
        return "Lisätty sisältöä"
    except:
        return "Lisääminen epäonnistui"

def delete_content(content_id):
    sql = "UPDATE content SET visible=0 WHERE id=:content_id"
    db.session.execute(sql, {"content_id":content_id})
    db.session.commit()
    
    return "Sisältöä poistettu!"

def get_contents(course_name, course_id):
    sql = "SELECT id, content FROM content WHERE course_id=:course_id AND visible=1"
    result = db.session.execute(sql, {"course_id":course_id})
    contents = result.fetchall()
    session["course_id"] = course_id
    session["course_name"] = course_name
    
    return contents
   
def get_tasks(course_id):
    sql = "SELECT id, name FROM tasks WHERE course_id=:course_id AND visible=1"
    result = db.session.execute(sql, {"course_id":course_id})
    tasks = result.fetchall()

    return tasks

def get_solved_count(course_id):
    user_id = session.get("user_id")
    sql = "SELECT COUNT(DISTINCT s.task_id) FROM solved s, tasks t WHERE t.course_id=:course_id AND s.task_id=t.id AND s.user_id=:user_id AND t.visible=1"
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    
    solved_count = result.fetchone()[0]
    return solved_count

def join_course(course_name, course_id):
    user_id = session["user_id"]

    if tasks.check_attending(course_id):
        return "Olet jo kurssilla"
    
    # Next query cheks if user has been on the course, but exited.
    # Attend value is updated if this is the case. 
    # This prevents user from adding multiple rows to the database
    sql = "SELECT COALESCE((SELECT id FROM participants WHERE course_id=:course_id AND user_id=:user_id AND attend=0), 0)"
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    attend_id = result.fetchone()[0]
    if int(attend_id) > 0:
        try:
            sql = "UPDATE participants SET attend=1 WHERE id=:attend_id"
            db.session.execute(sql, {"attend_id":attend_id})
            db.session.commit()
            return "Olet liittynyt kurssille " + course_name + "!" 
        except:
            return "Kurssille liittyminen epäonnistui"
    try:
        sql = "INSERT INTO participants (course_id, user_id, attend) VALUES (:course_id, :user_id, 1)"
        db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
        db.session.commit()
        return "Olet liittynyt kurssille " + course_name + "!"
    except:
        return "Kurssille liittyminen epäonnistui"
    

def exit_course(course_name, course_id):
    user_id = session["user_id"]
    try:
        sql = "UPDATE participants SET attend=0 WHERE user_id=:user_id"
        db.session.execute(sql, {"user_id":user_id})
        db.session.commit()
        return "Olet poistunut kurssilta " + course_name
    except:
        return "Kurssilta poistuminen epäonnistui"

def show_students(course_id):
    sql = "SELECT u.name, p.user_id FROM users u, participants p WHERE p.course_id=:course_id AND p.attend=1 AND p.user_id=u.id"
    result = db.session.execute(sql, {"course_id":course_id})
    students = result.fetchall()
        
    return students

def show_students_tasks(course_id, student_id):
    sql = "SELECT DISTINCT t.name FROM tasks t, solved s WHERE s.user_id=:student_id AND s.task_id=t.id AND t.course_id=:course_id"
    result = db.session.execute(sql, {"student_id":student_id, "course_id":course_id})
    tasks_list = result.fetchall()
    return tasks_list