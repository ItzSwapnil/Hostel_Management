from flask import Flask
from app.config import Config
from app.utils.database import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.student_routes import student_bp
    from app.routes.hostel_routes import hostel_bp
    from app.routes.complaint_routes import complaint_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp

    app.register_blueprint(student_bp, url_prefix="/api/v1/students")
    app.register_blueprint(hostel_bp, url_prefix="/api/v1/hostels")
    app.register_blueprint(complaint_bp, url_prefix="/api/v1/complaints")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/api/v1/dashboard")

    from flask import render_template, redirect, url_for, session, flash, request as flask_request
    import functools

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if not session.get('user_id'):
                return redirect(url_for('login'))
            return view(**kwargs)
        return wrapped_view

    def admin_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if not session.get('user_id') or session.get('role') != 'admin':
                flash('Admin access required.')
                return redirect(url_for('dashboard_web'))
            return view(**kwargs)
        return wrapped_view

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if flask_request.method == "POST":
            from app.models.user import User
            user = User.query.filter_by(username=flask_request.form["username"]).first()
            if user and user.check_password(flask_request.form["password"]):
                session.clear()
                session["user_id"] = user.id
                session["username"] = user.username
                session["role"] = user.role
                return redirect(url_for("dashboard_web"))
            flash("Invalid username or password")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        from app.models.user import User
        from app.utils.database import db
        from flask import request
        if flask_request.method == "POST":
            username = flask_request.form["username"]
            password = flask_request.form["password"]
            if User.query.filter_by(username=username).first():
                flash("Username already exists.")
                return render_template("register.html")
            user = User(username=username, role="student")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/admin-login", methods=["GET", "POST"])
    def admin_login():
        if flask_request.method == "POST":
            from app.models.user import User
            user = User.query.filter_by(username=flask_request.form["username"], role="admin").first()
            if user and user.check_password(flask_request.form["password"]):
                session.clear()
                session["user_id"] = user.id
                session["username"] = user.username
                session["role"] = user.role
                return redirect(url_for("dashboard_web"))
            flash("Invalid admin credentials")
        return render_template("admin_login.html")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard_web():
        from app.models.student import Student
        from app.models.hostel import Hostel
        from app.models.room import Room
        from app.models.complaint import Complaint
        stats = {
            "total_students": Student.query.count(),
            "total_hostels": Hostel.query.count(),
            "total_rooms": Room.query.count(),
            "total_complaints": Complaint.query.count(),
        }
        recent_complaints = Complaint.query.order_by(Complaint.timestamp.desc()).limit(5).all()
        available_rooms = Room.query.filter(Room.occupied_beds < Room.bed_count).all()
        return render_template("dashboard.html", stats=stats, recent_complaints=recent_complaints, available_rooms=available_rooms)

    @app.route("/students")
    @login_required
    @admin_required
    def students_web():
        from app.models.student import Student
        students = Student.query.all()
        return render_template("students.html", students=students)

    @app.route("/students/add", methods=["GET", "POST"])
    @login_required
    @admin_required
    def add_student_web():
        from app.models.student import Student
        from app.models.hostel import Hostel
        from app.models.room import Room
        from app.utils.database import db
        from flask import request
        hostels = Hostel.query.all()
        rooms = Room.query.filter(Room.occupied_beds < Room.bed_count).all()
        if request.method == "POST":
            student = Student(
                name=request.form["name"],
                email=request.form["email"],
                course=request.form.get("course"),
                hostel_id=request.form.get("hostel_id"),
                room_id=request.form.get("room_id")
            )
            db.session.add(student)
            db.session.commit()
            flash("Student added successfully.")
            return redirect(url_for("students_web"))
        return render_template("student_form.html", student=None, hostels=hostels, rooms=rooms)

    @app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def edit_student_web(student_id):
        from app.models.student import Student
        from app.models.hostel import Hostel
        from app.models.room import Room
        from app.utils.database import db
        from flask import request
        student = Student.query.get_or_404(student_id)
        hostels = Hostel.query.all()
        rooms = Room.query.filter(Room.occupied_beds < Room.bed_count).all()
        if request.method == "POST":
            student.name = request.form["name"]
            student.email = request.form["email"]
            student.course = request.form.get("course")
            student.hostel_id = request.form.get("hostel_id")
            student.room_id = request.form.get("room_id")
            db.session.commit()
            flash("Student updated successfully.")
            return redirect(url_for("students_web"))
        return render_template("student_form.html", student=student, hostels=hostels, rooms=rooms)

    @app.route("/students/delete/<int:student_id>")
    @login_required
    @admin_required
    def delete_student_web(student_id):
        from app.models.student import Student
        from app.utils.database import db
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        flash("Student deleted successfully.")
        return redirect(url_for("students_web"))

    @app.route("/hostels")
    @login_required
    @admin_required
    def hostels_web():
        from app.models.hostel import Hostel
        hostels = Hostel.query.all()
        return render_template("hostels.html", hostels=hostels)

    @app.route("/hostels/add", methods=["GET", "POST"])
    @login_required
    @admin_required
    def add_hostel_web():
        from app.models.hostel import Hostel
        from app.models.room import Room
        from app.utils.database import db
        from flask import request
        if request.method == "POST":
            hostel = Hostel(
                name=request.form["name"],
                type=request.form["type"],
                capacity=request.form["capacity"]
            )
            db.session.add(hostel)
            db.session.commit()
            # Auto-generate rooms after hostel is created
            try:
                num_rooms = int(request.form.get("num_rooms", 0))
                beds_per_room = int(request.form.get("beds_per_room", 0))
                for i in range(1, num_rooms + 1):
                    room = Room(
                        room_number=f"{hostel.name[:2].upper()}-{i:03}",
                        hostel_id=hostel.id,
                        bed_count=beds_per_room,
                        occupied_beds=0
                    )
                    db.session.add(room)
                db.session.commit()
                flash(f"Hostel and {num_rooms} rooms created successfully.")
            except Exception as e:
                flash(f"Hostel created, but error creating rooms: {e}")
            return redirect(url_for("hostels_web"))
        return render_template("hostel_form.html", hostel=None)

    @app.route("/hostels/edit/<int:hostel_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def edit_hostel_web(hostel_id):
        from app.models.hostel import Hostel
        from app.utils.database import db
        from flask import request
        hostel = Hostel.query.get_or_404(hostel_id)
        if request.method == "POST":
            hostel.name = request.form["name"]
            hostel.type = request.form["type"]
            hostel.capacity = request.form["capacity"]
            db.session.commit()
            flash("Hostel updated successfully.")
            return redirect(url_for("hostels_web"))
        return render_template("hostel_form.html", hostel=hostel)

    @app.route("/hostels/delete/<int:hostel_id>")
    @login_required
    @admin_required
    def delete_hostel_web(hostel_id):
        from app.models.hostel import Hostel
        from app.utils.database import db
        hostel = Hostel.query.get_or_404(hostel_id)
        db.session.delete(hostel)
        db.session.commit()
        flash("Hostel deleted successfully.")
        return redirect(url_for("hostels_web"))

    @app.route("/rooms")
    @login_required
    @admin_required
    def rooms_web():
        from app.models.room import Room
        rooms = Room.query.all()
        return render_template("rooms.html", rooms=rooms)

    @app.route("/rooms/add", methods=["GET", "POST"])
    @login_required
    @admin_required
    def add_room_web():
        from app.models.room import Room
        from app.utils.database import db
        from flask import request
        if request.method == "POST":
            room = Room(
                room_number=request.form["room_number"],
                hostel_id=request.form["hostel_id"],
                bed_count=request.form["bed_count"],
                occupied_beds=request.form.get("occupied_beds", 0)
            )
            db.session.add(room)
            db.session.commit()
            flash("Room added successfully.")
            return redirect(url_for("rooms_web"))
        return render_template("room_form.html", room=None)

    @app.route("/rooms/edit/<int:room_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def edit_room_web(room_id):
        from app.models.room import Room
        from app.utils.database import db
        from flask import request
        room = Room.query.get_or_404(room_id)
        if request.method == "POST":
            room.room_number = request.form["room_number"]
            room.hostel_id = request.form["hostel_id"]
            room.bed_count = request.form["bed_count"]
            room.occupied_beds = request.form.get("occupied_beds", 0)
            db.session.commit()
            flash("Room updated successfully.")
            return redirect(url_for("rooms_web"))
        return render_template("room_form.html", room=room)

    @app.route("/rooms/delete/<int:room_id>")
    @login_required
    @admin_required
    def delete_room_web(room_id):
        from app.models.room import Room
        from app.utils.database import db
        room = Room.query.get_or_404(room_id)
        db.session.delete(room)
        db.session.commit()
        flash("Room deleted successfully.")
        return redirect(url_for("rooms_web"))

    @app.route("/complaints")
    @login_required
    @admin_required
    def complaints_web():
        from app.models.complaint import Complaint
        complaints = Complaint.query.order_by(Complaint.timestamp.desc()).all()
        return render_template("complaints.html", complaints=complaints)

    @app.route("/complaints/add", methods=["GET", "POST"])
    @login_required
    @admin_required
    def add_complaint_web():
        from app.models.complaint import Complaint
        from app.utils.database import db
        from flask import request
        if request.method == "POST":
            complaint = Complaint(
                student_id=request.form["student_id"],
                description=request.form["description"],
                status=request.form.get("status", "Pending")
            )
            db.session.add(complaint)
            db.session.commit()
            flash("Complaint added successfully.")
            return redirect(url_for("complaints_web"))
        return render_template("complaint_form.html", complaint=None)

    @app.route("/complaints/edit/<int:complaint_id>", methods=["GET", "POST"])
    @login_required
    @admin_required
    def edit_complaint_web(complaint_id):
        from app.models.complaint import Complaint
        from app.utils.database import db
        from flask import request
        complaint = Complaint.query.get_or_404(complaint_id)
        if request.method == "POST":
            complaint.student_id = request.form["student_id"]
            complaint.description = request.form["description"]
            complaint.status = request.form.get("status", "Pending")
            db.session.commit()
            flash("Complaint updated successfully.")
            return redirect(url_for("complaints_web"))
        return render_template("complaint_form.html", complaint=complaint)

    @app.route("/complaints/delete/<int:complaint_id>")
    @login_required
    @admin_required
    def delete_complaint_web(complaint_id):
        from app.models.complaint import Complaint
        from app.utils.database import db
        complaint = Complaint.query.get_or_404(complaint_id)
        db.session.delete(complaint)
        db.session.commit()
        flash("Complaint deleted successfully.")
        return redirect(url_for("complaints_web"))

    @app.route("/complaints/resolve/<int:complaint_id>")
    @login_required
    @admin_required
    def resolve_complaint_web(complaint_id):
        from app.models.complaint import Complaint
        from app.utils.database import db
        if session.get("role") != "admin":
            flash("Admin access required to resolve complaints.")
            return redirect(url_for("complaints_web"))
        complaint = Complaint.query.get_or_404(complaint_id)
        complaint.status = "Resolved"
        db.session.commit()
        flash("Complaint marked as resolved.")
        return redirect(url_for("complaints_web"))

    return app

