from flask import Flask, render_template, url_for, request, session, redirect, g, jsonify
import sqlite3 as sql
import sqlite3
import os

app = Flask(__name__)
databasePath = os.getcwd() + '/database.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(databasePath)
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

            if check_duplicates(name):
                msg = "Username already taken"
            else:
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

# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         try:
#             name=request.form['name']
#             pin=request.form['pin']
#             with sql.connect(databasePath) as con:
#                 cur = con.cursor()
#                 try:
#                     sqlite_insert_query = """SELECT * from login where
#                     name='""" + name + """' and pin='""" + pin + """'"""
#                     cur.execute(sqlite_insert_query)
#                     records = cur.fetchall()
#                     if (len(records) >= 1):
#                         session['username'] = name
#                         msg ="Welcome back, " + name +"!"
#                     else:
#                         msg = "Wrong username or password"
#                 except:
#                     msg = "error"
#         except:
#             msg="error in insert operation" + " " + msg
#         finally:
#             return render_template("result.html", msg=msg)
#             con.close()

def check_duplicates(name):
    conn = sql.connect(databasePath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM login")
    rows = cursor.fetchall()
    usernames = [row[0] for row in rows]
    if name in usernames:
        return True
    return False


@app.route('/logon', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            name = request.form['name']
            pin = request.form['pin']
            with sql.connect(databasePath) as con:
                cur = con.cursor()
                try:
                    sqlite_insert_query = """SELECT * from login where
                    name='""" + name + """' and pin='""" + pin + """'"""
                    cur.execute(sqlite_insert_query)
                    records = cur.fetchall()
                    if len(records) >= 1:
                        session['username'] = name
                        if name == 'admin':
                           msg = "Admin Login successful"
                        else:
                            msg = "Welcome back, " + name +"!"
                    else:
                        msg = "Wrong username or password"
                except:
                    msg = "Error executing query"
        except:
            msg = "Error in form submission"
        finally:
            if msg == "Admin Login successful":
                conn1 = sql.connect(databasePath)
                conn1.row_factory = sql.Row
                cur1 = conn1.cursor()
                cur1.execute("SELECT * FROM login")
                rows1 = cur1.fetchall()
                conn1.close()

                # Connect to the second database
                conn2 = sql.connect(databasePath)
                conn2.row_factory = sql.Row
                cur2 = conn2.cursor()
                cur2.execute("SELECT * FROM markers")
                rows2 = cur2.fetchall()
                conn2.close()
                return render_template('admin_page.html',rows1=rows1, rows2=rows2)
            else:
                return render_template("result.html", msg=msg)
    
    return render_template('login.html')

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



@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id):
    conn = sql.connect(databasePath)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM login WHERE name = ?", (record_id,))

    conn.commit()
    conn.close()
    conn1 = sql.connect(databasePath)
    conn1.row_factory = sql.Row
    cur1 = conn1.cursor()
    cur1.execute("SELECT * FROM login")
    rows1 = cur1.fetchall()
    conn1.close()

    # Connect to the second database
    conn2 = sql.connect(databasePath)
    conn2.row_factory = sql.Row
    cur2 = conn2.cursor()
    cur2.execute("SELECT * FROM markers")
    rows2 = cur2.fetchall()
    conn2.close()
    return render_template("admin_page.html", rows1=rows1, rows2=rows2)

@app.route('/delete1/<string:record_id>', methods=['POST'])
def delete1_record(record_id):
    conn = sql.connect(databasePath)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM markers WHERE lat = ?", (record_id,))

    conn.commit()
    conn.close()

    conn1 = sql.connect(databasePath)
    conn1.row_factory = sql.Row
    cur1 = conn1.cursor()
    cur1.execute("SELECT * FROM login")
    rows1 = cur1.fetchall()
    conn1.close()

    # Connect to the second database
    conn2 = sql.connect(databasePath)
    conn2.row_factory = sql.Row
    cur2 = conn2.cursor()
    cur2.execute("SELECT * FROM markers")
    rows2 = cur2.fetchall()
    conn2.close()
    return render_template("admin_page.html", rows1=rows1, rows2=rows2)


@app.route('/add_data', methods=['POST'])
def add_data():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        pin = request.form['pin']

        # Insert data into database
        conn = sql.connect(databasePath)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO login (name, pin) VALUES (?, ?)", (name, pin))
        conn.commit()
        conn.close()

        # Redirect to homepage
        conn1 = sql.connect(databasePath)
        conn1.row_factory = sql.Row
        cur1 = conn1.cursor()
        cur1.execute("SELECT * FROM login")
        rows1 = cur1.fetchall()
        conn1.close()

        # Connect to the second database
        conn2 = sql.connect(databasePath)
        conn2.row_factory = sql.Row
        cur2 = conn2.cursor()
        cur2.execute("SELECT * FROM markers")
        rows2 = cur2.fetchall()
        conn2.close()
        return render_template("admin_page.html", rows1=rows1, rows2=rows2)

    # Handle GET request or other cases
    return render_template("admin_page.html", rows1=rows1, rows2=rows2)


if __name__ == "__main__":
    app.run(debug=True)