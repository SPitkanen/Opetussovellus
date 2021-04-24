
from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
import os

logged_in = False
# Check if user inputs correspond to a user in database
def login(username, password):
    sql = "SELECT id, password, role FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return False
    else:
        user_id = user[0]
        hash_value = user[1]
        role = user[2]
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["role"] = role
            session["user_id"] = user_id
            session["csrf_token"] = os.urandom(16).hex()
            global logged_in
            logged_in = True
            return True
        else:
            return False

# Delete sessions
def logout():
    global logged_in
    logged_in = False
    del session["username"]
    del session["role"]
    del session["user_id"]
    del session["csrf_token"]

# Database allows insertion if username and password are unique
def signup(username, password):
    try:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (name, password, role) VALUES (:username, :password, 'student') RETURNING id"
        result = db.session.execute(sql, {"username":username,"password":hash_value})
        db.session.commit()
        return True
    except:
        return False

def user_id():
    return session.get("user_id")

def username():
    return session.get("username")

def role():
    return session.get("role")

def csrf_token():
    return session.get("csrf_token")

def check_logged():
    global logged_in
    return logged_in