#!/usr/bin/python3
from datetime import datetime

class User:
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.time_in = None
        self.time_out = None

    def add_user(self, name, plate_number="Empty"):
        self.time_out="not set"
        if self.time_in is None:
            self.time_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO user (name, plate_number, time_in, time_out) VALUES (?, ?, ?, ?)"
        params = (name, plate_number, self.time_in, self.time_out)
        if not self.db_manager.execute_query(query, params, commit=True):
            return False
        print("Admin Successfully added new user")
        
           
    def update_user(self, plate_number, new_plate_number=None, new_name=None):
        if new_name and self.db_manager.record_exist("user", "name", new_name):
            print(f"Error: The name {new_name} already exists")
            new_name = None
        if new_plate_number and self.db_manager.record_exist("user", "plate_number", new_plate_number):
            print(f"Error: The plate number {new_plate_number} already exists")
            new_plate_number = None
        
        fields = []
        params = []

        if new_name is not None:
            fields.append("name = ?")
            params.append(new_name)

        if new_plate_number is not None:
            fields.append("plate_number = ?")
            params.append(new_plate_number)

        if not fields:
            print("No Info to be updated")
            return

        query = f"UPDATE user SET {', '.join(fields)} WHERE plate_number = ?"
        params.append(plate_number)
        if not self.db_manager.execute_query(query, params, commit=True):
            return False
        print(f"User with plate number {plate_number} data have been updated")
    
    def update_user_time(self, plate_number, sensor):
        """Update the user time based on their movement through the gate.

        Args:
            plate_number (str): User Car Plate Number
            sensor (bool): State of the hardware
        """
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results = self.view_users(fetch="plate_number", value=plate_number, user="cam")
        if not results:
            return
        else:
            row = results[0]
            if sensor == "out":
                self.update_user(row[4], time_out=time)
            else:
                self.update_user(row[2], time_in=time)
        
    def view_users(self, user, fetch="all", value=None):
        """Check the database for the parameters passed if they exist in the database.

        Args:
            fetch (str, optional): accepts all, name, plate_number, time_in, time_off. Defaults to "all".
            value (str, optional): specific data or it Defaults to None.

        Raises:
            ValueError: If an invalid fetch type is provided.

        Returns:
            list: The result of the query.
        """
        if user == 'cam':
            query = "SELECT * FROM user WHERE plate_number = ?" if value else "SELECT plate_number FROM user"
            params = (value,) if value else ()
        elif fetch == "all":
            query = "SELECT * FROM user"
            params = ()
        elif fetch == "name":
            query = "SELECT * FROM user WHERE name = ?" if value else "SELECT name FROM user"
            params = (value,) if value else ()
        elif fetch == "plate_number":
            query = "SELECT * FROM user WHERE plate_number = ?" if value else "SELECT plate_number FROM user"
            params = (value,) if value else ()
        elif fetch == "time_in":
            query = "SELECT * FROM user WHERE time_in = ?" if value else "SELECT time_in FROM user"
            params = (value,) if value else ()
        elif fetch == "time_off":
            query = "SELECT * FROM user WHERE time_off = ?" if value else "SELECT time_off FROM user"
            params = (value,) if value else ()
        else:
            raise ValueError("Invalid fetch parameter provided")

        cursor = self.db_manager.execute_query(query, params)
        results = cursor.fetchall()

        if not results and user == "cam":
            print("Plate number not found. Please contact admin.")
            return False
        elif not results and user == "admin":
            print("No info matches your requirements.")
        elif user == "cam":
            return results
        elif user == "admin":
            for row in results:
                print(f"Name: {row[1]}, Plate Number: {row[3]}, Time In: {row[2]}, Time Out: {row[4]}")
        else:
            print("Unknown user")
            return False

    def delete_user(self, plate_number):
        query = "DELETE FROM user WHERE name = ?"
        param = (plate_number,)
        self.db_manager.execute_query(query, param, commit=True)
        print("User with name {plate_number} has been deleted sucessfully")
        
