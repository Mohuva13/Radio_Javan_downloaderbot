import re
from bs4 import BeautifulSoup
from webbot import Browser
import wget
import os
import requests
#telegram-bot libraries
import logging
from telegram import Update
from telegram.chataction import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


#bot commands
#start bot command
def start_handler(update: Update, context:CallbackContext):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    if first_name == None :
        first_name = " "
    if last_name == None :
        last_name = " "
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_photo(chat_id=chat_id, photo=open('./radiojavan.png', 'rb'), caption=f'سلام {first_name} {last_name} \n\nلینک آهنگ را از اپلیکیشن یا وب سایت رادیو جوان بفرستید.')


#input url
def input_url(update: Update, context:CallbackContext):
    chat_id = update.message.chat_id
    # input url

    url = update.message.text

    # --------------------
    # check url
    url_check_regex = re.findall(r"(www\.radiojavan\.com/mp3s/mp3/)", url)
    url_check_regex_app = re.findall(r"(rj\.app/m/)", url)
    if url_check_regex_app != []:
        url = url
    if url_check_regex != []:
        url = url
    res = ""
    if url_check_regex_app == [] and url_check_regex == []:
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=chat_id, text="لینک اشتباه است لطفا لینک آهنگ مورد نظر را از رادیو جوان بفرستید.")
        res = "inv"
    # try to download
    if res != "inv":
        web = Browser()
        web.go_to(url)
        s = web.get_page_source()
        web.close_current_tab()
        soup = BeautifulSoup(s, 'html.parser')
        # finde mp3 link
        mp3_name = str(re.findall(r"RJ\.currentMP3Perm\ =\ \'(.*)\'\;", str(soup)))
        mp3_name = mp3_name.replace("['", "")
        mp3_name = mp3_name.replace("']", "")
        mp3_url = f"https://host2.rj-mw1.com/media/mp3/mp3-256/{mp3_name}.mp3"

    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)

    mp3_url_check = requests.get(mp3_url)
    mp3_url_check = str(mp3_url_check)
    if mp3_url_check != "<Response [200]>":
        wget.download(mp3_url, f'{mp3_name}.mp3')
    else:
        try:
            os.remove(f"{mp3_name}.mp3")
        except:
            pass
        mp3_url = f"https://host1.rj-mw1.com/media/mp3/mp3-256/{mp3_name}.mp3"
        wget.download(mp3_url, f'{mp3_name}.mp3')

    audio_caption = str(mp3_name) #name fixed
    audio_caption = audio_caption.replace("-"," ")
    context.bot.send_audio(chat_id=chat_id, audio=open(f"./{mp3_name}.mp3", "rb"), caption=f"{audio_caption}")
    if os.path.exists(f"{mp3_name}.mp3"):
        os.remove(f"{mp3_name}.mp3")


def main():
    updater = Updater("1673620291:AAFTg-Dzs6857hA8e1ymHkvk_1vf_HFlvDg")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start_handler))
    #Download music
    dispatcher.add_handler(MessageHandler(Filters.text, input_url))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

