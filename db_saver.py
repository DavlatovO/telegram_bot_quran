import sqlite3 

def save_user(id, username, name):
    # Connect to the SQLite database
    conn = sqlite3.connect('telegram_bot_quran/data_collection.db')

    try:
        # Create a cursor object
        cursor = conn.cursor()

        # Check if the user already exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (id,))
        user_exists = cursor.fetchone()  # Fetch one result

        if user_exists:
            pass
        else:
            # Insert the new user into the 'users' table
            cursor.execute(f'''
                INSERT INTO users (user_id, username, name)
                VALUES ({id}, '{username}', '{name}');
            ''')
            
        # # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the database connection
        conn.close()
