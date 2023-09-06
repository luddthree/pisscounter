from flask import Flask, render_template, url_for, request, session, redirect, g, jsonify
import sqlite3 as sql
import mysql.connector
import sqlite3
import os

app = Flask(__name__)
databasePath = os.getcwd() + '/database.db'


# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(databasePath)
# #        g.db = sqlite3.connect('/var/www/html/markers.db')
#         g.db.row_factory = sqlite3.Row
#     return g.db
 
app.secret_key = 'your secret key'  # Replace with your own secret key

db_config = {
    'host': 'localhost',
    'user': 'ludvik',
    'password': 'Password123#@!',
    'database': 'mydatabase',
}


@app.before_request
def before_request():
    g.db = mysql.connector.connect(**db_config)
    g.cursor = g.db.cursor(dictionary=True)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.cursor.close()
        g.db.close()

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

@app.route('/tos')
def tos():
    return render_template('tos.html')


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

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            name = request.form['name']
            pin = request.form['pin']
            email = request.form['email']

            if check_duplicates(name):
                msg = "Username already taken"
            else:
                # Insert data into the MySQL database
                query = "INSERT INTO login (name, pin, email) VALUES (%s, %s, %s)"
                values = (name, pin, email)
                g.cursor.execute(query, values)
                g.db.commit()
                session['username'] = name
                msg = "Welcome to Pisscounter " + name + "!"
                
        except Exception as e:
            g.db.rollback()
            msg = "Error in insert operation: " + str(e)
        finally:
            return render_template("result.html", msg=msg)

# @app.route('/list')
# def list():
#     con = sql.connect(databasePath)
#     con.row_factory = sql.Row
#     cur = con.cursor()
#     cur.execute("select * from login")
#     rows = cur.fetchall()
#     return render_template('list.html',rows=rows)

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
    try:
        query = "SELECT name FROM login WHERE name = %s"
        values = (name,)
        g.cursor.execute(query, values)
        row = g.cursor.fetchone()

        if row is not None:
            return True
        return False
    except Exception as e:
        print("Error checking duplicates:", str(e))
        return False


@app.route('/logon', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            name = request.form['name']
            pin = request.form['pin']

            query = "SELECT * FROM login WHERE name = %s AND pin = %s"
            values = (name, pin)
            g.cursor.execute(query, values)
            records = g.cursor.fetchall()

            if len(records) >= 1:
                session['username'] = name
                if name == 'admin':
                    msg = "Admin Login successful"
                else:
                    msg = "Welcome back, " + name + "!"
            else:
                msg = "Wrong username or password"
        except Exception:
            msg = "Error executing query"
        finally:
            if msg == "Admin Login successful":
                g.cursor.execute("SELECT * FROM login")
                rows1 = g.cursor.fetchall()

                g.cursor.execute("SELECT * FROM markers")
                rows2 = g.cursor.fetchall()

                return render_template('admin_page.html', rows1=rows1, rows2=rows2)
            else:
                return render_template("result.html", msg=msg)

@app.route('/map')
def root():
    if 'username' in session:
        # Fetch markers from the MySQL database
        g.cursor.execute('SELECT lat, lon, popup FROM markers')
        markers = [{'lat': row['lat'], 'lon': row['lon'], 'popup': row['popup']} for row in g.cursor.fetchall()]
        return render_template('map.html', markers=markers)
    else:
        return render_template('map2.html')

# Route to save a marker to the database
@app.route('/save_marker', methods=['POST'])
def save_marker():
    data = request.json
    lat = data['lat']
    lon = data['lon']
    popup = data['popup']
 
    # Insert the marker data into the MySQL database
    query = "INSERT INTO markers (lat, lon, popup) VALUES (%s, %s, %s)"
    values = (lat, lon, popup)
    g.cursor.execute(query, values)
    g.db.commit()

    return jsonify({'message': 'Marker saved successfully'})

# Route to remove a marker from the database
@app.route('/remove_marker', methods=['POST'])
def remove_marker():
    data = request.json
    lat = data['lat']
    lon = data['lon']

    # Delete the marker from the MySQL database
    query = "DELETE FROM markers WHERE lat = %s AND lon = %s"
    values = (lat, lon)
    g.cursor.execute(query, values)
    g.db.commit()

    # return jsonify({'message': 'Marker removed successfully'}



@app.route('/delete/<string:record_id>', methods=['POST'])
def delete_record(record_id):
    try:
        # Delete the record from the login table in the MySQL database
        query = "DELETE FROM login WHERE name = %s"
        values = (record_id,)
        g.cursor.execute(query, values)
        g.db.commit()
        msg = "Record deleted successfully"
    except Exception as e:
        g.db.rollback()
        msg = f"Error in delete operation: {str(e)}"
    finally:
        # Fetch data from the MySQL database for rendering
        g.cursor.execute("SELECT * FROM login")
        rows1 = g.cursor.fetchall()

        g.cursor.execute("SELECT * FROM markers")
        rows2 = g.cursor.fetchall()

        return render_template("admin_page.html", rows1=rows1, rows2=rows2, msg=msg)

@app.route('/delete1/<string:record_id>', methods=['POST'])
def delete1_record(record_id):
    try:
        # Delete the record from the markers table in the MySQL database
        query = "DELETE FROM markers WHERE lat = %s"
        values = (record_id,)
        g.cursor.execute(query, values)
        g.db.commit()
        msg = "Record deleted successfully"
    except Exception as e:
        g.db.rollback()
        msg = f"Error in delete operation: {str(e)}"
    finally:
        # Fetch data from the MySQL database for rendering
        g.cursor.execute("SELECT * FROM login")
        rows1 = g.cursor.fetchall()

        g.cursor.execute("SELECT * FROM markers")
        rows2 = g.cursor.fetchall()

        return render_template("admin_page.html", rows1=rows1, rows2=rows2, msg=msg)



@app.route('/add_data', methods=['POST'])
def add_data():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        pin = request.form['pin']

        try:
            # Insert data into the MySQL database
            query = "INSERT INTO login (name, pin) VALUES (%s, %s)"
            values = (name, pin)
            g.cursor.execute(query, values)
            g.db.commit()
            msg = "Data added successfully"
        except Exception as e:
            g.db.rollback()
            msg = f"Error in insert operation: {str(e)}"
        finally:
            # Fetch data from the MySQL database for rendering
            g.cursor.execute("SELECT * FROM login")
            rows1 = g.cursor.fetchall()

            g.cursor.execute("SELECT * FROM markers")
            rows2 = g.cursor.fetchall()

            return render_template("admin_page.html", rows1=rows1, rows2=rows2, msg=msg)

    # Handle GET request or other cases
    return render_template("admin_page.html", rows1=rows1, rows2=rows2)



if __name__ == "__main__":
    app.run(debug=True)