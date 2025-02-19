# # Please Dont Run This Code
# # Database Setup Thanks
# import sqlite3

# #Creates or Connect to the database
# database_connection = sqlite3.connect("smart_plate_number.db")
# database_init = database_connection.cursor()
# # Create user table
# database_init.execute('''CREATE TABLE IF NOT EXISTS user (
#                         id INTEGER PRIMARY KEY,
#                         name TEXT NOT NULL,
#                         time_in TEXT NOT NULL,
#                         plate_number TEXT NOT NULL UNIQUE,
#                         time_out TEXT)''')

# # Create admin table
# database_init.execute('''CREATE TABLE IF NOT EXISTS admin (
#                         id INTEGER PRIMARY KEY, 
#                         username TEXT NOT NULL,
#                         password TEXT NOT NULL UNIQUE)''')

# # Create a trigger to limit the number of admin accounts to 3

# database_init.execute('''CREATE TRIGGER IF NOT EXISTS limit_number_of_admin
#                     BEFORE INSERT ON admin
#                     BEGIN
#                         SELECT CASE
#                             WHEN (SELECT COUNT(*) FROM admin) >= 3
#                             THEN RAISE(ABORT , 'Maximum number of admin acciunts reached.')
#                         END;
#                     END;''')

# database_connection.commit()
# database_connection.close()
