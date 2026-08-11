
import csv
import io
from datetime import date
from flask import Flask, render_template, request, redirect, session, url_for, Response

# Import the shared DBManager
from core.db_manager import DBManager

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
        
    error = None
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        error = "Invalid Credentials"

    return render_template("login.html", error=error)

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    department_filter = request.args.get("department")
    semester_filter = request.args.get("semester")

    with DBManager.get_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT id, name, status, date, time, department, semester, roll_no FROM logs WHERE 1=1"
        params = []

        if department_filter:
            query += " AND department=?"
            params.append(department_filter)

        if semester_filter:
            query += " AND semester=?"
            params.append(semester_filter)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        logs = cursor.fetchall()

        cursor.execute("SELECT DISTINCT department FROM logs")
        departments = [row["department"] for row in cursor.fetchall() if row["department"]]

        cursor.execute("SELECT DISTINCT semester FROM logs")
        semesters = [row["semester"] for row in cursor.fetchall() if row["semester"]]

        cursor.execute("SELECT COUNT(*) as count FROM logs")
        total_logs = cursor.fetchone()["count"]

        today_str = str(date.today())
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE date=?", (today_str,))
        today_count = cursor.fetchone()["count"]

    return render_template(
        "dashboard.html",
        logs=logs,
        departments=departments,
        semesters=semesters,
        department_filter=department_filter,
        semester_filter=semester_filter,
        total_logs=total_logs,
        today_count=today_count
    )

# ---------------- EXPORT ----------------

@app.route("/export")
def export():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    department_filter = request.args.get("department")
    semester_filter = request.args.get("semester")

    with DBManager.get_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT id, name, status, date, time, department, semester, roll_no FROM logs WHERE 1=1"
        params = []

        if department_filter:
            query += " AND department=?"
            params.append(department_filter)

        if semester_filter:
            query += " AND semester=?"
            params.append(semester_filter)

        cursor.execute(query, params)
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Status", "Date", "Time", "Department", "Semester", "Roll No"])
    
    for row in rows:
        writer.writerow(tuple(row))

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=logs.csv"}
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    # Ensure DB is setup before running
    DBManager.setup_database()
    app.run(debug=True, port=5001)
