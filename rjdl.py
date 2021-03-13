import re
from bs4 import BeautifulSoup
from webbot import Browser
import wget

# input url

url = input("Send Radia Javan link : ")

#check url
url_check_regex = re.findall(r"(www\.radiojavan\.com/mp3s/mp3/)",url)
url_check_regex_app = re.findall(r"(rj\.app/m/)",url)
if url_check_regex_app != []:
    url = url
if url_check_regex != []:
    url = url
res = ""
if url_check_regex_app == [] and url_check_regex == []:
    print("Invalid url")
    res = "inv"
#try to download
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


wget.download(mp3_url, f'{mp3_name}.mp3')