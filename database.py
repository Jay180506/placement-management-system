import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="placement_management_system"
)

print("Database Connected Successfully")

