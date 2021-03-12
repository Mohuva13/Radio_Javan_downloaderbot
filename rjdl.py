import re
from bs4 import BeautifulSoup
import urllib.request
from webbot import Browser

# input url

url = input("Send Radia Javan link : ")

#check url
url_check_regex = re.findall(r"(www\.radiojavan\.com/mp3s/mp3/)",url)
url_check_regex_app = re.findall(r"(rj\.app/m/)",url)
if url_check_regex_app != []:
    url = url
if url_check_regex != []:
    url = url
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
    print(soup)