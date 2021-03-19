import re
from bs4 import BeautifulSoup
from webbot import Browser
import wget
import os
import urllib.request
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
    context.bot.send_photo(chat_id=chat_id, photo=open('./radiojavan.png', 'rb'), caption=f'سلام {first_name} {last_name} \n\nلینک آهنگ یا موزیک ویدیو را از اپلیکیشن یا وب سایت رادیو جوان بفرستید.')


#input url
def input_url(update: Update, context:CallbackContext):
    while True:
        chat_id = update.message.chat_id
        # input url

        url = update.message.text

        # --------------------
        # check url
        url_check_regex = re.findall(r"(www\.radiojavan\.com/mp3s/mp3/)", url)
        url_check_regex_app = re.findall(r"(rj\.app/m/)", url)
        url_check_regex_podcast_app = re.findall(r"rj\.app/p/", url)
        url_check_regex_podcast = re.findall(r"www\.radiojavan\.com/podcasts/podcast/", url)
        url_check_regex_video = re.findall(r"www\.radiojavan\.com/videos/video/", url)
        url_check_regex_video_app = re.findall(r"rj\.app/v/", url)
        url_check_regex_playlist = re.findall(r"www\.radiojavan\.com/playlists/playlist/", url)
        url_check_regex_playlist_app = re.findall(r"rj\.app/pm/", url)
        list_url = [
            url_check_regex,
            url_check_regex_app,
            url_check_regex_podcast,
            url_check_regex_podcast_app,
            url_check_regex_video,
            url_check_regex_video_app,
            url_check_regex_playlist,
            url_check_regex_playlist_app
        ]
        what_is_link_type = ""
        count = 0
        for check_url_link_list in list_url:
            if str(check_url_link_list) != "[]" :
                url = url
                what_is_link_type = check_url_link_list
            else:
                count += 1
        res = ""


        if count == 6:
            context.bot.send_chat_action(chat_id, ChatAction.TYPING)
            context.bot.send_message(chat_id=chat_id, text="لینک اشتباه است. \n\n لطفا لینک آهنگ یا موزیک ویدیوی مورد نظر را از رادیو جوان بفرستید.")
            res = "inv"
            break

        # try to download
        files_url = {
            "music": "media/mp3/mp3-256/",
            "podcast": "media/podcast/mp3-192/",
            "video_lq": "media/music_video/lq/",
            "video_hd": "media/music_video/hd/",
            "video_hq": "media/music_video/hq/",
            "video_4k": "media/music_video/4k/"
        }
        regex_music_and_video = {
            "music": "RJ\.currentMP3Perm\ =\ \'(.*)\'\;",
            "video": "RJ\.videoPermlink\ =\ \'(.*)\'\;"
        }
        def download_file_rj(music_or_video, file_type, regex_file, ch_actions):
            context.bot.send_message(chat_id=chat_id, text="کمی صبر کنید...")
            if res != "inv":
                web = Browser()
                web.go_to(url)
                s = web.get_page_source()
                web.close_current_tab()
                soup = BeautifulSoup(s, 'html.parser')
                # finde mp3 link
                file_name = str(re.findall(fr"{regex_file}", str(soup)))
                file_name = file_name.replace("['", "")
                file_name = file_name.replace("']", "")
                file_url = f"https://host2.rj-mw1.com/{file_type}{file_name}.mp{music_or_video}"
                req = urllib.request.Request(file_url)
                with urllib.request.urlopen(req) as response:
                    the_file_url_page = str(response.read())
                if the_file_url_page != "b'Not found'":
                    wget.download(file_url, f'{file_name}.mp{music_or_video}')
                else:
                    try:
                        os.remove(f"{file_name}.mp{music_or_video}")
                    except:
                        pass
                    file_url = f"https://host1.rj-mw1.com/{file_type}{file_name}.mp{music_or_video}"
                    wget.download(file_url, f'{file_name}.mp{music_or_video}')
                file_caption = str(file_name) #name fixed
                file_caption = file_caption.replace("-"," ")
                if str(file_name) == "[]":
                    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
                    context.bot.send_message(chat_id=chat_id, text="لینک اشتباه است. \n\n لطفا لینک آهنگ یا موزیک ویدیوی مورد نظر را از رادیو جوان بفرستید.")
                else:
                    if ch_actions == "music":
                        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
                        context.bot.send_audio(chat_id=chat_id, audio=open(f"./{file_name}.mp{music_or_video}", "rb"), caption=f"{file_caption}")
                    elif ch_actions == "video":
                        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_VIDEO)
                        context.bot.send_video(chat_id=chat_id, video=open(f"./{file_name}.mp{music_or_video}", "rb"), caption=f"{file_caption}")

                if os.path.exists(f"{file_name}.mp{music_or_video}"):
                    os.remove(f"{file_name}.mp{music_or_video}")
        if what_is_link_type == url_check_regex_podcast:
            context.bot.send_message(chat_id=chat_id, text="به دلیل محدودیت ارسال فایل های حجم بالا توسط ربات ها از سمت تلگرام ، امکان ارسال پادکست وجود ندارد...")
        elif what_is_link_type == url_check_regex_podcast_app:
            context.bot.send_message(chat_id=chat_id, text="به دلیل محدودیت ارسال فایل های حجم بالا توسط ربات ها از سمت تلگرام ، امکان ارسال پادکست وجود ندارد...")
        elif what_is_link_type == url_check_regex:
            download_file_rj("3",files_url["music"],regex_music_and_video["music"], "music")
        elif what_is_link_type == url_check_regex_app:
            download_file_rj("3",files_url["music"],regex_music_and_video["music"], "music")
        elif what_is_link_type == url_check_regex_playlist:
            web = Browser()
            web.go_to(url)
            play_list_source_page = web.get_page_source()
            web.close_current_tab()
            soup_playlist = BeautifulSoup(play_list_source_page, "html.parser")
            list_artists_playlist = soup_playlist.findAll("span", {"class": "artist"})
            list_songs_playlist = soup_playlist.findAll("span", {"class": "song"})
            playlist_count = 0
            for artists in list_artists_playlist:
                re_artists = re.findall(r"(?=>).*(?=<)", str(artists))
                re_songs = re.findall(r"(?=>).*(?=<)", str(list_songs_playlist[playlist_count]))
                url = f"www.radiojavan.com/mp3s/mp3/{re_artists[0]}-{re_songs[0]}"
                playlist_count += 1
                url = url.replace(" ", "-")
                url = url.replace("['>", "")
                url = url.replace("']", "")
                url = url.replace(">", "")
                download_file_rj("3", files_url["music"], regex_music_and_video["music"], "music")

        elif what_is_link_type == url_check_regex_playlist_app:
            web = Browser()
            web.go_to(url)
            play_list_source_page = web.get_page_source()
            web.close_current_tab()
            soup_playlist = BeautifulSoup(play_list_source_page, "html.parser")
            list_artists_playlist = soup_playlist.findAll("span", {"class": "artist"})
            list_songs_playlist = soup_playlist.findAll("span", {"class": "song"})
            playlist_count = 0
            for artists in list_artists_playlist:
                re_artists = re.findall(r"(?=>).*(?=<)", str(artists))
                re_songs = re.findall(r"(?=>).*(?=<)", str(list_songs_playlist[playlist_count]))
                url = f"www.radiojavan.com/mp3s/mp3/{re_artists[0]}-{re_songs[0]}"
                playlist_count += 1
                url = url.replace(" ", "-")
                url = url.replace("['>", "")
                url = url.replace("']", "")
                url = url.replace(">", "")
                download_file_rj("3", files_url["music"], regex_music_and_video["music"], "music")
        elif what_is_link_type == url_check_regex_video_app:
            try:
                context.bot.send_message(chat_id=chat_id, text="متاسفانه به دلیل محدودیت حجم آپلود فایل توسط ربات ها از سمت تلگرام ، موزیک ویدیو فقط با کیفیت 480p LQ برایتان آپلود خواهد شد . \n\n منتظر دریافت موزیک ویدیو باشید...")
                download_file_rj("4", files_url["video_lq"], regex_music_and_video["video"], "video")
            except:
                pass
        elif what_is_link_type == url_check_regex_video:
            try:
                context.bot.send_message(chat_id=chat_id, text="متاسفانه به دلیل محدودیت حجم آپلود فایل توسط ربات ها از سمت تلگرام ، موزیک ویدیو فقط با کیفیت 480p LQ برایتان آپلود خواهد شد .\n\n منتظر دریافت موزیک ویدیو باشید...")
                download_file_rj("4", files_url["video_lq"], regex_music_and_video["video"], "video")
            except:
                pass
        context.bot.send_message(chat_id=chat_id, text=":)")
        break


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

