# -*- coding: utf-8 -*-

import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from configs import *
import os
import rongoscript as rs

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hello {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    update.message.reply_text('Start by training the model. You can use our ready-made model trained on the FAQ pairs found in faq_en.json. To do this, use the /train_faq command. To train the model on your data, create a json file with the same structure as our faq_en.json but with your own training pairs. Upload your json file as Document. Model creation will start automatically as soon as the file is uploaded.')

def help_command(update: Update, context: CallbackContext) -> None:
    """Sends a message when the command /help is issued."""
    update.message.reply_text('For details, visit https://github.com/nlptechbook/RongoScript')

def reply(update: Update, context: CallbackContext) -> None:
    """replies to the user message."""
    response = ''
    if ("model" in context.user_data):
      model = context.user_data["model"]
      response = model.get_prediction(update.message.text)
    else:
      response = 'No trained model to use. You can use our ready-made model trained on the FAQ pairs found in the faq_en.json file. To do this, use the /train_faq command. To train the model on your data, upload your json file as a Document with your training pairs. In this case, the creation of the model will start automatically after the file is loaded.'
    update.message.reply_text(response) 

def train_faq(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('One moment please ..')
    filename = os.path.join(filepath +'{}'.format(sample_file))
    model = rs.model(filename) 
    if isinstance(model.error, str):
      update.message.reply_text(str(model.error)) 
      return   
    context.user_data["model"] = model
    update.message.reply_text('Done! You can now ask questions from the FAQ.')

def train_custom(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('One moment please ..')
    file_id = update.message.document.file_id
    doc_file = context.bot.get_file(file_id)
    filename = os.path.join(filepath +'{}.json'.format(doc_file.file_id))
    doc_file.download(filename)
    model = rs.model(filename)
    if isinstance(model.error, str):
      update.message.reply_text(str(model.error)) 
      return
    context.user_data['model'] = model
    update.message.reply_text('Done! You can now ask questions from your training set.')

def main() -> None:
    """Starts the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("YOUR_API_TOKEN_HERE")

    # Gets the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answers in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("train_faq", train_faq))

    # on non command i.e message - sends a reply message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))
    
    # on loading a document - starts the process of data reading and training a model
    dispatcher.add_handler(MessageHandler(Filters.document, train_custom))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
