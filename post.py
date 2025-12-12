#C:/Users/robiu/AppData/Local/Programs/Python/Python313/python.exe -m pip install --user mysql-connector-python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error

#http://localhost:5000/teacher?id=2

API_KEY = "mysecretkey123"
# DB config - update if your XAMPP uses different credentials
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",   # change if root has a password
    "database": "section_selection"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def add_section_course_to_db(course_name, course_code, department, faculty_name, section, day, course_credit):
    sql = "INSERT INTO section_details (course_name, course_code, department, faculty_name, section, day, course_credit) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (course_name, course_code, department, faculty_name, section, day, course_credit))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    except Error as e:
        # In production you might log this
        return None
    finally:
        if conn:
            conn.close()

class SimpleAPI(BaseHTTPRequestHandler):
    # AUTH CHECK
    def authenticate(self):
        """Check API key in request header"""
        key = self.headers.get("X-API-KEY")
        if key != API_KEY:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return False
        return True
    
    def do_POST(self):
        # AUTH REQUIRED
        if not self.authenticate():
            return


        parsed = urlparse(self.path)
        if parsed.path == "/teacher":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            course_name = data.get("course_name")
            course_code = data.get("course_code")
            department = data.get("department")
            faculty_name = data.get("faculty_name")
            section = data.get("section")
            day = data.get("day")
            course_credit = data.get("course_credit")
            new_id = add_section_course_to_db (course_name, course_code, department, faculty_name, section, day, course_credit)

            result = {
                "message": "Section or coure added successfully",
                "id": new_id
            }
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(result).encode())

server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()