import firebase_admin
from firebase_admin import db, credentials, firestore
from datetime import datetime

# Initializes firebase database
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://sunlab-room-records-48685-default-rtdb.firebaseio.com/"})

# Reference to the Firestore database
firebase_db = db.reference()
db = firestore.client()

# Defines the logs for user access to room
def access_logs(user_id, timestamp):
    # Student log object that contains student's ID and timestamp
    user_log = {
        'user_id': user_id,
        'timestamp': timestamp
    }

    # Pushes access logs to database
    firebase_db.child('access_logs').push(user_log)
    db.collection('access_logs').add(user_log)

# Gets the access logs for user
def get_access_logs(user_id=None, start_date=None, end_date=None):
    log_ref = db.collection('access_logs')

    if user_id:
        log_ref = log_ref.where('user_id', '==', user_id)

    if start_date:
        log_ref = log_ref.where('timestamp', '>=', start_date)

    if end_date:
        log_ref = log_ref.where('timestamp', '<=', end_date)

    logs = log_ref.stream()
    return [(log.id, log.to_dict()) for log in logs]

# Search for log access records
def search_access_records(start_date=None, end_date=None, user_id=None):
    # Reference for access records
    access_ref = db.collection('access_records')

    # Build the query based on the provided filters
    query = access_ref

    if start_date and end_date:
        query = query.where('access_time', '>=', start_date).where('access_time', '<=', end_date)

    if user_id:
        query = query.where('user_id', '==', user_id)

    # Run query and get records
    records = query.stream()

    # Return each records
    for record in records:
        print(f'{record.id}: {record.to_dict()}')


# Updates user status
def user_id_status(user_id, status):
    firebase_db.child('users').child(user_id).update({'status': status})
    db.collection('users').document(user_id).update({'status': status})

class RoomAccessSystem:
    def __init__(self):
        self.users = {}

    def add_user(self, user):
        self.users[user.user_id] = user

    # Used to log access
    def log_access(self, user_id):
        user = self.users.get(user_id)
        if not user or not user.is_active():
            print(f"Access denied for user ID: {user_id}")
            return

        # To record timestamp
        timestamp = datetime.now()

        # Logs access
        access_logs(user_id, timestamp)
        print(f"{user.name} [ ({user.role}) ] accessed SunLAB at {timestamp}")

    # Activates users ID
    def activate_user(self, user_id):
        user = self.users.get(user_id)
        if user:
            user.activate()
            user_id_status(user_id, "active")
            print(f"{user.name} [ ({user.role}) ] is now activated.")
        else:
            print(f"User ID {user_id} not found.")

    # Suspends the users ID
    def suspend_user(self, user_id):
        user = self.users.get(user_id)
        if user:
            user.deactivate()
            user_id_status(user_id, "suspended")
            print(f"User {user.name} ({user.role}) suspended.")
        else:
            print(f"User ID {user_id} not found.")

    # Reactivates a suspended ID
    def reactivate_user(self, user_id):
        user = self.users.get(user_id)
        if user:
            user.activate()
            user_id_status(user_id, "active")
            print(f"User {user.name} ({user.role}) reactivated.")
        else:
            print(f"User ID {user_id} not found.")

    # Filter logs based on user_id, start_date, and end_date
    def filter_access_logs(self, user_id=None, start_date=None, end_date=None):
        logs = get_access_logs(user_id, start_date, end_date)
        return logs

class User:
    def __init__(self, user_id, name, personnel):
        self.user_id = user_id
        self.name = name
        self.personnel = personnel
        self.active = True

    def is_active(self):
        return self.active

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

class Student(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, personnel="student")

class FacultyMember(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, personnel="faculty")

class StaffMember(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, personnel="staff")

class Janitor(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, personnel="janitor")