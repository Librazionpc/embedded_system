from .user import User
import bcrypt


class Admin:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _hash_password(self, password):
        """Hash the password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _check_password(self, password, hashed_password):
        """Check if the provided password matches the hashed password."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def add_admin(self, username, password):
        """Add a new admin with hashed password."""
        hashed_password = self._hash_password(password)
        query = "INSERT INTO admin (username, password) VALUES (?, ?)"
        params = (username, hashed_password)
        self.db_manager.execute_query(query, params, commit=True)
        print(f"Admin {username} account is successfully created")

    def verify_admin(self, username, password):
        query = "SELECT password FROM admin WHERE username = ?"
        params = (username,)
        cursor = self.db_manager.execute_query(query, params)
        result = cursor.fetchone()

        if result:
            stored_hashed_password = result[0]
            return self._check_password(password, stored_hashed_password)
        else:
            return False

    def add_user(self, name, plate_number="Empty"):
        user_manager = User(self.db_manager)
        user_manager.add_user(name, plate_number)
        
    def view_users(self, user, fetch=None, value=None):
        user_manager = User(self.db_manager)
        if not fetch:
            if not (user_manager.view_users(user)):
                return False
            
        else:
            if not (user_manager.view_users(fetch, value, user)):
                return False
    
    def update_user(self, plate_number, new_plate_number=None, new_name=None):
        user_manager = User(self.db_manager)
        if plate_number:
            user_manager.update_user(plate_number, new_plate_number, new_name)
        else:
            print("Enter the user plate number")
            return False

    def delete_user(self, plate_number):
        user_manager = User(self.db_manager)
        if plate_number:
            user_manager.delete_user(plate_number)
        else:
            print("Enter the user plate number")
