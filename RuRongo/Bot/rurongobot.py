# -*- coding: utf-8 -*-

import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from configs import *
import os
import rurongoscript as rs

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    update.message.reply_text('Начните с тренировки модели. Вы можете использовать готовую модель, которую мы натренировали на FAQ парах. Для этого используйте команду /train_faq. Чтобы натренировать модель на своих данных, создайте json файл с такой же структурой как наш faq.json но со своими тренировочными парами. Загрузите ваш json файл как Документ. Создание модели начнется автоматически сразу после загрузки файла.')

def help_command(update: Update, context: CallbackContext) -> None:
    """Sends a message when the command /help is issued."""
    update.message.reply_text('Загляните на https://github.com/nlptechbook/RongoScript/')

def reply(update: Update, context: CallbackContext) -> None:
    """replies to the user message."""
    response = ''
    if ("model" in context.user_data):
      model = context.user_data["model"]
      response = model.get_prediction(update.message.text)
    else:
      response = 'Нет натренированной модели для использования. Вы можете использовать готовую модель, которую мы натренировали на FAQ парах. Для этого используйте команду /train_faq. Чтобы натренировать модель на своих данных, загрузите ваш json файл как Документ со своими тренировочными парами. В этом случае создание модели начнется автоматически сразу после загрузки файла.'
    update.message.reply_text(response) 

def train_faq(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Минуточку ..')
    filename = os.path.join(filepath +'{}'.format(sample_file))
    model = rs.model(filename) 
    if isinstance(model.error, str):
      update.message.reply_text(str(model.error)) 
      return   
    context.user_data["model"] = model
    update.message.reply_text('Готово! Можно задавать вопросы из FAQ набора.')

def train_custom(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Минуточку ..')
    file_id = update.message.document.file_id
    doc_file = context.bot.get_file(file_id)
    filename = os.path.join(filepath +'{}.json'.format(doc_file.file_id))
    doc_file.download(filename)
    model= rs.model(filename)
    if isinstance(model.error, str):
      update.message.reply_text(str(model.error)) 
      return
    context.user_data['model'] = model
    update.message.reply_text('Готово! Можно задавать вопросы из тренировочного набора.')

def main() -> None:
    """Starts the bot."""
    # Creates the Updater and pass it your bot's token.
    updater = Updater("YOUR_API_TOKEN_HERE")

    # Gets the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answers in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("train_faq", train_faq))

    # on non command i.e message - sends a reply message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))
    dispatcher.add_handler(MessageHandler(Filters.document, train_custom))

    # Starts the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
