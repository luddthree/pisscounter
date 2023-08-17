from flask import Flask, render_template, url_for, request, session, redirect
import sqlite3 as sql
import os

app = Flask(__name__)
app.secret_key = 'your secret key'  # Replace with your own secret key
databasePath = os.getcwd() + '/database.db'

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return render_template('index2.html')

@app.route('/logon')
def logon():
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    
    # Redirect the user to a specific page after logout
    return render_template('index2.html')

@app.route('/about')
def about():
    if 'username' in session:
        return render_template('about1.html')
    else:
        return render_template('about.html')
    

@app.route('/enternew')
def new_student():
    return render_template('student.html')

@app.route('/addrec', methods=['POST','GET'])
def addrec():
    if request.method == 'POST':
        try:
            name=request.form['name']
            pin=request.form['pin']

            with sql.connect(databasePath) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO login (name,pin) VALUES (?,?)",(name,pin))
                con.commit()
                session['username'] = name
                msg = "Welcome to Pisscounter " + name + "!"
                
        except BaseException as e:
            con.rollback()
            msg="error in insert operation: " + str(e)
        finally:
            return render_template("result.html", msg=msg)
            con.close()

@app.route('/list')
def list():
    con = sql.connect(databasePath)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from login")
    rows = cur.fetchall()
    return render_template('list.html',rows=rows)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            name=request.form['name']
            pin=request.form['pin']
            with sql.connect(databasePath) as con:
                cur = con.cursor()
                try:
                    sqlite_insert_query = """SELECT * from login where
                    name='""" + name + """' and pin='""" + pin + """'"""
                    cur.execute(sqlite_insert_query)
                    records = cur.fetchall()
                    if (len(records) >= 1):
                        session['username'] = name
                        msg ="Welcome back, " + name +"!"
                    else:
                        msg = "Wrong username or password"
                except:
                    msg = "error"
        except:
            msg="error in insert operation" + " " + msg
        finally:
            return render_template("result.html", msg=msg)
            con.close()

if __name__ == "__main__":
    app.run(debug=True)