from flask import Flask, render_template, request, redirect, send_file, url_for
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

DB_NAME = "student_info_db"
TABLE_NAME = "student_info"

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Home - list students
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    students = cursor.fetchall()
    conn.close()
    return render_template('index.html', students=students)

# Add student
@app.route('/add', methods=['POST'])
def add_student():
    data = (
        request.form.get('student_id'),
        request.form.get('name'),
        request.form.get('father_name'),
        request.form.get('mother_name'),
        request.form.get('dob'),
        request.form.get('address'),
        request.form.get('phone'),
        request.form.get('email'),
        request.form.get('degree'),
        request.form.get('stream'),
        request.form.get('year_of_joining'),
        request.form.get('year_of_pass_out')
    )
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {TABLE_NAME} (student_id, name, father_name, mother_name, dob, address, phone, email, degree, stream, year_of_joining, year_of_pass_out) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        data
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Update student
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = (
            request.form.get('student_id'),
            request.form.get('name'),
            request.form.get('father_name'),
            request.form.get('mother_name'),
            request.form.get('dob'),
            request.form.get('address'),
            request.form.get('phone'),
            request.form.get('email'),
            request.form.get('degree'),
            request.form.get('stream'),
            request.form.get('year_of_joining'),
            request.form.get('year_of_pass_out'),
            id
        )
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET student_id=%s, name=%s, father_name=%s, mother_name=%s, dob=%s, address=%s, phone=%s, email=%s, degree=%s, stream=%s, year_of_joining=%s, year_of_pass_out=%s WHERE id=%s",
            data
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id=%s", (id,))
    student = cursor.fetchone()
    conn.close()
    return render_template('update.html', student=student)

# Delete student
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Download all as table-style PDF
@app.route('/download_all')
def download_all():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    students = cursor.fetchall()
    conn.close()

    file_path = "all_students_table.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, height - 40, "All Students Report")

    # Table header
    c.setFont("Helvetica-Bold", 9)
    y = height - 70
    headers = ["AutoID","STD ID","Name","Father","Mother","DOB","Phone","Email","Degree","Stream","Year Join","Year Pass"]
    x_positions = [30,70,120,250,330,410,470,530,610,660,700,760]
    for i, h in enumerate(headers):
        c.drawString(x_positions[i], y, h)
    y -= 15
    c.setFont("Helvetica", 9)

    for s in students:
        # ensure tuple length
        row = [str(s[i]) if i < len(s) else "" for i in range(13)]
        for i, cell in enumerate(row):
            if x_positions[i] < width - 30:
                c.drawString(x_positions[i], y, cell[:25])
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return send_file(file_path, as_attachment=True)

# Download single student by student_id (table-style)
@app.route('/download_student/<student_id>')
def download_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE student_id=%s", (student_id,))
    student = cursor.fetchone()
    conn.close()
    if not student:
        return "Student not found", 404

    file_path = f"{student[2]}_{student[1]}.pdf"  # Name_STDID.pdf
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, height - 40, "Student Details")

    # Draw table-like two-column layout
    labels = ["Auto ID","Student ID","Name","Father Name","Mother Name","DOB","Address","Phone","Email","Degree","Stream","Year of Joining","Year of Pass Out"]
    values = [str(student[i]) if i < len(student) else "" for i in range(13)]

    x_label = 60
    x_value = 240
    y = height - 80
    c.setFont("Helvetica", 12)
    for label, value in zip(labels, values):
        c.drawString(x_label, y, f"{label}:")
        c.drawString(x_value, y, f"{value}")
        y -= 18
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
