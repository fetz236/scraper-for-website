#Python program to scrape website
#and save quotes from website
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import List

def main():
    url = "https://www.cfcunderwriting.com"
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    '''
    Checks all potential external links present in the website.
    External links ususally stem from CSS, JS files, Image Files, Video Tags, Audio Tags and Font tags

    Although the home page does not have external links in forms of audio and video, a check is still completed
    '''
    css_files = soup.find_all("link", rel="stylesheet")
    js_files = soup.find_all("script", src=True)
    img_files = soup.find_all("img", src=True)
    video_tags = soup.find_all("video", src=True)
    audio_tags = soup.find_all("audio", src=True)
    font_tags = soup.find_all("style", text=re.compile("@font-face"))

    check_urls = getCssUrls(css_files) + getJsUrls(js_files) + getImgUrls(img_files) \
        + getVideoUrls(video_tags) + getAudioUrls(audio_tags) + getFontUrls(font_tags)

    #Get and save external URLs
    getExternalUrls(check_urls)

    link_tags = soup.find_all("a")
    link_urls = []
    for link in link_tags:
        link_urls.append(link.get("href"))

    privacy_policy = getPrivacyPolicy(link_urls)

    if len(privacy_policy) > 0:
        savePrivacyPolicy(url, privacy_policy)
        
    

#Gets all urls of linked CSS Files
def getCssUrls(css_files) -> List[str]:
    css_urls = []
    for css in css_files:
        css_urls.append(css.get("href"))
    return css_urls


#Gets all urls of linked JS files
def getJsUrls(js_files) -> List[str]:
    js_urls = []
    for js in js_files:
        js_urls.append(js.get("src"))
    return js_urls

#Gets all urls of linked img files
def getImgUrls(img_files) -> List[str]:
    img_urls = []
    for img in img_files:
        img_urls.append(img.get("src"))
    return img_urls

#Gets all urls of linked video files
def getVideoUrls(video_tags) -> List[str]:
    vid_urls = []
    for img in video_tags:
        vid_urls.append(img.get("src"))
    return vid_urls

#Gets all urls of linked audio files
def getAudioUrls(audio_tags) -> List[str]:
    aud_urls = []
    for img in audio_tags:
        aud_urls.append(img.get("src"))
    return aud_urls

#Gets all urls of linked Font files 
def getFontUrls(font_tags) -> List[str]:
    font_urls = []
    for font in font_tags:
        #Uses regex to find Externally linked websites
        font_url = re.search(r"url\((.+?)\)", font.text).group(1)
        font_urls.append(font_url)
    return font_urls

#Uses basic checks to ensure its not hosted on the website and is externally sourced
def getExternalUrls(check_urls) -> None:
    external_urls =[]
    for url in check_urls:
        if not url.startswith("http://cfcunderwriting.com") and not url.startswith("/"):
            external_urls.append(url)
    
    with open("external_urls.json", "w") as f:
        json.dump(external_urls, f)

def getPrivacyPolicy(link_urls) -> str:
    for link in link_urls:
        link_text = link if link else ""
        #Checks to see if both privacy and policy are in the link text variable 

        '''
        It might make more sense to add all potential links in a list and then try to use some algorithm that predicts
        which link is most likely the privacy policy
        '''

        if "privacy" in link_text and "policy" in link_text:
            privacy_policy_url = link_text
            return privacy_policy_url
    #Returns an empty string in the case that no privacy policy is found
    return ""


#Pass the URL and privacy policy parameters to calculate and save each word to a JSON
def savePrivacyPolicy(url, privacy_policy) -> None:

    #Retrieve page using soup
    privacy_url = url+privacy_policy
    privacy_response = requests.get(privacy_url)
    privacy_soup = BeautifulSoup(privacy_response.text,"html.parser")

    #Get all text from the page and format it to remove punctuation
    all = privacy_soup.get_text()
    formatted_text = " ".join(all.split())
    word_list = formatted_text.split(" ")
    word_count = {}
    for word in word_list:
        #Case in-sensitive
        word = word.lower()
        #Regex to remove punctuation
        word = re.sub(r'[^\w\s]', '', word)
        count = word_count.get(word, 0) + 1
        word_count.update({word: count})

    with open("word_count.json", "w") as f:
        json.dump(word_count, f)
    
main()