import requests

def send_to_admin(username, user_id, message_text):

    base_url = 'https://api.telegram.org/bot8017585127:AAGMatjy-svHzwCiN2hqHu5-FK6uqfiDI3k/sendMessage'

    parameters = {
        'chat_id':'1358545450',
        'text':f"The user with username @{username} and {user_id} sent message: \n{message_text}. "
    }

    resp = requests.post(base_url, data=parameters)
    