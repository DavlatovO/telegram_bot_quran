import sqlite3 

def save_user(id, is_bot, first_name, username, user_type, message_text, message_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('db_database.db')

    try:
        # Create a cursor object
        cursor = conn.cursor()

        # Check if the user already exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (id,))
        user_exists = cursor.fetchone()  # Fetch one result

        if user_exists:
            pass
            # Insert the message into the 'messages' table
            # cursor.execute(f'''
                # INSERT INTO messages (message_id, user_id, message_text)
                # VALUES ({message_id}, {id}, '{message_text}');
            # ''')
            # print('user exists')
        else:
            # Insert the new user into the 'users' table
            cursor.execute(f'''
                INSERT INTO users (id, is_bot, first_name, username, type)
                VALUES ({id}, {is_bot}, {first_name}, {username}, {user_type});
            ''')

        #     # Insert the message into the 'messages' table
        #     cursor.execute(f'''
        #         INSERT INTO messages (message_id, user_id, message_text)
        #         VALUES ({message_id}, {id}, {message_text});
        #     ''')
        # # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the database connection
        conn.close()
