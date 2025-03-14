# pip install pyTelegramBotAPI
import telebot, time

class NotificationsTelegramBot(object):

    def __init__(self, token, chatId):

        self.token = token
        self.chatId = chatId

    def bot_send_msg(self, message):

        '''Telegram bot to send messages to the mobile app. When we import as: from telegramBot import bot_send_msg we are importing all the module; the thing that changes is the binding.'''

        bot = telebot.TeleBot(self.token)

        # Every function that calls the Telegram API is executed in a separate Thread.
        chat_id_group = self.chatId
        bot.send_message(chat_id_group, message)

        # Delete to save resources:
        del bot

if __name__ == '__main__':
	
    botObject = NotificationsTelegramBot("7078638445:AAH3OF4Usyiq6KPo46dtzdcvwA4US-ZJLJY", 803510108)
    botObject.bot_send_msg("One, two, three... TradeFlex!")

    ''' To get the updates, if the BOT was added far away to a chat, you may not get any updates until you issue the "/start" method. After sending the /start method as the creator of the bot, you can go to this link:

    https://api.telegram.org/bot"insert-bot-token"/getUpdates
    https://api.telegram.org/bot1159315823:AAFexwCPKJvMeulDnS-he3NCeAjWqcTgejY/getUpdates
    
    AND YOU WILL SEE THE CHAT ID. THE CHAT ID DOES NOT CHANGE WITH TIME, SO YOU CAN JUST SEND MESSAGES WITHOUT THE NEED OF LOOKING IT AGAIN AND AGAIN. 

    # updates = bot.get_updates()
    # print([u.message.chat.id for u in updates]) --- to get the chat id.'''