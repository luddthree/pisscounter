from flask import Flask, render_template, url_for, request, session, redirect, g, jsonify
import sqlite3 as sql
import sqlite3
import os

app = Flask(__name__)
databasePath = os.getcwd() + '/database.db'
markersPath = os.getcwd() + '/markers.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(markersPath)
#        g.db = sqlite3.connect('/var/www/html/markers.db')
        g.db.row_factory = sqlite3.Row
    return g.db
 
app.secret_key = 'your secret key'  # Replace with your own secret key


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


@app.route('/app')
def ap():
    return render_template('index_app.html')

@app.route('/abapp')
def aboutapp():
    return render_template('about_app.html')

@app.route('/mapapp')
def mapapp():
    return render_template('map_app.html')

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


@app.route('/map')
def root():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT lat, lon, popup FROM markers')
    markers = [{'lat': row['lat'], 'lon': row['lon'], 'popup': row['popup']} for row in cursor.fetchall()]
    
    if 'username' in session:
        return render_template('map.html',markers=markers )
    else:
        return render_template('map2.html')

@app.route('/save_marker', methods=['POST'])
def save_marker():
    data = request.json
    lat = data['lat']
    lon = data['lon']
    popup = data['popup']
 
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO markers (lat, lon, popup) VALUES (?, ?, ?)', (lat, lon, popup))
    conn.commit()

    return jsonify({'message': 'Marker saved successfully'})



@app.route('/remove_marker', methods=['POST'])
def remove_marker():
    data = request.json
    lat = data['lat']
    lon = data['lon']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM markers WHERE lat = ? AND lon = ?', (lat, lon))
    conn.commit()

    return jsonify({'message': 'Marker removed successfully'})



if __name__ == "__main__":
    app.run(debug=True)