import sqlite3 as sql
import html
import bcrypt
from threading import Lock

file_lock = Lock()

def insertUser(username, password, DoB):
    username = html.escape(username, quote=True)
    password = html.escape(password, quote=True)
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cur.execute("INSERT INTO users (username, password, dateOfBirth) VALUES (?, ?, ?)", (username, hash_password, DoB),)
    con.commit()
    con.close()

def userExists(username):
    username = html.escape(username, quote=True)
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    con.close()
    return result is not None

def retrieveUsers(username, password):
    username = html.escape(username, quote=True)
    password = html.escape(password, quote=True)
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    if result is None or not bcrypt.checkpw(password.encode(), result[0]):
        con.close()
        return False
    with file_lock:
        try:
            with open("visitor_log.txt", "r") as file:
                number = int(file.read().strip())
        except FileNotFoundError:
            number = 0
        number += 1
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))
    con.close()
    return True

def insertFeedback(feedback):
    feedback = html.escape(feedback, quote=True)
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()

def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    with open("templates/partials/success_feedback.html", "w") as f:
        for row in data:
            f.write("<p>\n")
            f.write(f"{row[1]}\n")
            f.write("</p>\n")