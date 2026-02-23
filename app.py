from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Upload Folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# Database Init
# -------------------------
def init_db():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            gender TEXT,
            dob TEXT,
            course TEXT,
            photo TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME PAGE
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()

    # ADD STUDENT
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        gender = request.form['gender']
        dob = request.form['dob']
        course = request.form['course']

        photo = request.files.get('photo')
        filename = ""

        if photo and photo.filename != "":
            filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur.execute("""
            INSERT INTO students 
            (first_name, last_name, email, gender, dob, course, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fname, lname, email, gender, dob, course, filename))

        conn.commit()

    # SEARCH
    search = request.args.get('search')

    if search:
        cur.execute("""
            SELECT * FROM students 
            WHERE first_name LIKE ?
            OR last_name LIKE ?
            OR email LIKE ?
        """, ('%'+search+'%', '%'+search+'%', '%'+search+'%'))
    else:
        cur.execute("SELECT * FROM students")

    students = cur.fetchall()
    conn.close()

    return render_template('index.html', students=students)

# -------------------------
# DELETE
# -------------------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# -------------------------
# EDIT (ID WILL NOT CHANGE)
# -------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        gender = request.form['gender']
        dob = request.form['dob']
        course = request.form['course']

        photo = request.files.get('photo')

        # If new photo uploaded
        if photo and photo.filename != "":
            filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cur.execute("""
                UPDATE students
                SET first_name=?, last_name=?, email=?, gender=?, dob=?, course=?, photo=?
                WHERE id=?
            """, (fname, lname, email, gender, dob, course, filename, id))

        else:
            # Update without changing photo
            cur.execute("""
                UPDATE students
                SET first_name=?, last_name=?, email=?, gender=?, dob=?, course=?
                WHERE id=?
            """, (fname, lname, email, gender, dob, course, id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET Student Data
    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('edit.html', student=student)

# -------------------------
# RUN
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)