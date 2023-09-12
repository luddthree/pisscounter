import mysql.connector

# Establish a connection to the MySQL server
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Password123#@!",
)

# Create a cursor object to execute SQL queries
my_cursor = mydb.cursor()

# Create a new database
my_cursor.execute("CREATE DATABASE mydatabase")  
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
