# Hostel Management System

A modern, full-featured hostel management system built with Flask. It supports student and room management, complaint tracking, admin dashboard, and secure authentication.

## Features
- User authentication (JWT, student/admin roles)
- Student CRUD and room assignment/transfer
- Hostel and room management
- Complaint submission and admin resolution
- Dashboard with stats, recent complaints, and available rooms

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/ItzSwapnil/Hostel_Management/tree/master
cd Hostel_Management
```

### 2. Create a virtual environment and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements/prod.txt
pip install -r requirements/dev.txt
```
    For UV 
```bash
uv venv venv
uv pip install -r requirements/prod.txt
uv pip install -r requirements/dev.txt
```


### 3. Configure environment variables
Create a `.env` file in the root directory:
```
DATABASE_URL=sqlite:///hostel.db
SECRET_KEY=your_secret_key_here
```

### 4. Initialize the database
```bash
python manage.py init-db
```

### 5. Run the application
```bash
python manage.py
```

## API Usage

### Authentication
- **Register:** `POST /api/v1/auth/register` `{ "username": "user", "password": "pass", "role": "student|admin" }`
- **Login:** `POST /api/v1/auth/login` `{ "username": "user", "password": "pass" }` → `{ "token": "..." }`
- Use the token in the `Authorization: Bearer <token>` header for protected endpoints.

### Students
- **List:** `GET /api/v1/students/`
- **Create:** `POST /api/v1/students/` `{ "name": ..., "email": ..., ... }`
- **Assign Room:** `POST /api/v1/students/assign-room` `{ "student_id": ..., "room_id": ... }`
- **Transfer Room:** `POST /api/v1/students/transfer-room` `{ "student_id": ..., "new_room_id": ... }`
- **Available Rooms:** `GET /api/v1/students/available-rooms`

### Hostels & Rooms
- **List Hostels:** `GET /api/v1/hostels/`
- **Create Hostel:** `POST /api/v1/hostels/` `{ "name": ..., "type": ..., "capacity": ... }`

### Complaints
- **List:** `GET /api/v1/complaints/`
- **Submit:** `POST /api/v1/complaints/` `{ "student_id": ..., "description": ... }`
- **Resolve (admin):** `POST /api/v1/complaints/<id>/resolve`
- **Update Status (admin):** `PATCH /api/v1/complaints/<id>` `{ "status": "..." }`

### Dashboard
- **Summary:** `GET /api/v1/dashboard/` (JWT required)
- **Details:** `GET /api/v1/dashboard/details` (recent complaints, available rooms)

## Example: Register, Login, and Use API
```bash
# Register a user
curl -X POST http://localhost:5000/api/v1/auth/register -H "Content-Type: application/json" -d '{"username":"admin","password":"adminpass","role":"admin"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"adminpass"}'
# Use the returned token for further requests:
# Authorization: Bearer <token>
```

## ER Diagram
Run `python er_diagram.py` to generate an entity-relationship diagram as `hostel_er_diagram.png`.

## Testing
```bash
pytest
```

---

For more details, see the code and API routes. Contributions welcome!

