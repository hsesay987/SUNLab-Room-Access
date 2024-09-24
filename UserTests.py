import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sunlab-room-records-48685-default-rtdb.firebaseio.com/'})

# Samples used to push into firebase
class UserTests:
    def __init__(self):
        # Initialize Firebase database
        self.db = db.reference()

    def custom_logs(self):
        # Predefined list of logs
        logs = [
            {"user_id": "530493018", "name": "John Doe", "personnel": "student", "timestamp": "2024-09-01 14:30:00"},
            {"user_id": "201921583", "name": "Jane Smith", "personnel": "faculty", "timestamp": "2024-08-15 10:15:00"},
            {"user_id": "579006266", "name": "Emily Johnson", "personnel": "staff", "timestamp": "2024-07-20 09:45:00"},
            {"user_id": "461468941", "name": "Chris Brown", "personnel": "janitor", "timestamp": "2024-06-10 12:00:00"},
            {"user_id": "564585119", "name": "Alex Wilson", "personnel": "student", "timestamp": "2024-05-25 16:30:00"}
        ]

        for log in logs:
            print(f"Inserting log for {log['name']} ({log['personnel']}) at {log['timestamp']}")

            # Push user data
            self.db.child('users').child(log['user_id']).set({
                'name': log['name'],
                'role': log['personnel'],
                'status': 'active'
            })

            # Push access log data to Firebase
            log_data = {
                'user_id': log['user_id'],
                'timestamp': log['timestamp'],
                'role': log['personnel']
            }
            self.db.child('access_logs').push(log_data)

            print(f"Log inserted for {log['name']}")

if __name__ == "__main__":
    custom_log = UserTests()
    custom_log.custom_logs()
