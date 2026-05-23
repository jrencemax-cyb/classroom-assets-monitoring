from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "secretkey"


# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT username, password, role FROM users WHERE username=%s",
                (username,)
            )

            user = cursor.fetchone()

            if not user:
                return "Invalid Login ❌"

            db_username, db_password, db_role = user

            if password.strip() == db_password.strip():
                session["user"] = db_username
                session["role"] = db_role
                return redirect(url_for("dashboard"))

            return "Invalid Login ❌"

        return render_template("login.html")

    except Exception as e:
        print("ERROR:", e)
        return f"Server Error: {e}"
# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "").strip()

        ADMIN_PASSWORD = "ADMIN2026"

        if password.strip() == ADMIN_PASSWORD:
            session["user"] = "admin"
            session["role"] = "admin"
            return redirect(url_for("dashboard"))

        return "Wrong Admin Password ❌"

    return render_template("admin_login.html")


# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )

        conn.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    search = request.args.get("search")

    conn = get_db_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM assets
            WHERE asset_name ILIKE %s
            OR classroom ILIKE %s
            OR status ILIKE %s
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM assets")

    assets = cursor.fetchall()

    if role == "admin":
        return render_template("admin_dashboard.html", assets=assets)

    elif role == "teacher":
        return render_template("teacher_dashboard.html", assets=assets)

    elif role == "staff":
        return render_template("staff_dashboard.html", assets=assets)

    return redirect(url_for("login"))


# =========================
# ADD ASSET
# =========================
@app.route("/add_asset", methods=["POST"])
def add_asset():
    asset_name = request.form["asset_name"]
    quantity = request.form["quantity"]
    classroom = request.form["classroom"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO assets (asset_name, quantity, classroom) VALUES (%s, %s, %s)",
        (asset_name, quantity, classroom)
    )

    conn.commit()
    return redirect(url_for("dashboard"))


# =========================
# DELETE ASSET
# =========================
@app.route("/delete_asset/<int:id>")
def delete_asset(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM assets WHERE id=%s", (id,))
    conn.commit()

    return redirect(url_for("dashboard"))


# =========================
# EDIT ASSET
# =========================
@app.route("/edit_asset/<int:id>", methods=["GET", "POST"])
def edit_asset(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        asset_name = request.form["asset_name"]
        quantity = request.form["quantity"]
        classroom = request.form["classroom"]

        cursor.execute("""
            UPDATE assets
            SET asset_name=%s,
                quantity=%s,
                classroom=%s
            WHERE id=%s
        """, (asset_name, quantity, classroom, id))

        conn.commit()
        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM assets WHERE id=%s", (id,))
    asset = cursor.fetchone()

    return render_template("edit_asset.html", asset=asset)


# =========================
# REPORT ASSET
# =========================
@app.route("/report_asset/<int:id>", methods=["GET", "POST"])
def report_asset(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        issue = request.form["issue"]
        reported_by = session.get("user")

        cursor.execute(
            "INSERT INTO reports (asset_id, reported_by, issue) VALUES (%s, %s, %s)",
            (id, reported_by, issue)
        )

        conn.commit()
        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM assets WHERE id=%s", (id,))
    asset = cursor.fetchone()

    return render_template("report_asset.html", asset=asset)


# =========================
# VIEW REPORTS
# =========================
@app.route("/reports")
def reports():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports")
    reports = cursor.fetchall()

    return render_template("reports.html", reports=reports)


# =========================
# UPDATE STATUS
# =========================
@app.route("/update_status/<int:id>", methods=["GET", "POST"])
def update_status(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        status = request.form["status"]

        cursor.execute(
            "UPDATE assets SET status=%s WHERE id=%s",
            (status, id)
        )

        conn.commit()
        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM assets WHERE id=%s", (id,))
    asset = cursor.fetchone()

    return render_template("update_status.html", asset=asset)


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)