from app import create_app
from app.utils.database import db

app = create_app()

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        print("Initialized the database.")

@app.cli.command("create-admin")
def create_admin():
    from app.models.user import User
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print("Admin user already exists.")
            return
        admin = User(username=username, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "init-db":
        with app.app_context():
            db.create_all()
            print("Initialized the database.")
    else:
        app.run()

