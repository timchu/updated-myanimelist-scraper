#Python program to scrape website 
#and save quotes from website
import requests
from bs4 import BeautifulSoup
import csv
import time
   
# print("Input an anime name")
# anime_name = input()

no_actor_string = "There is no actor!"

def rate_limited_request(search_URL):
    time.sleep(1)
    return requests.get(search_URL)

def get_character_webpage(anime_name):
    """Search for the Anime on MyAnimeList"""
    new_name =anime_name.replace(" ", "%20")
    url_prefix = "http://myanimelist.net/search/all?q="
    url_suffix = "&cat=all"
    search_URL = url_prefix + new_name + url_suffix

    """Extract the webpage the anime URL is in"""
    r = rate_limited_request(search_URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    info = soup.find("div", {"class":"title"})
    if info == []:
        print("We got rated limited")
    anime_page_url = info.a['href']
    print("We found the anime page:", anime_page_url)

    """Character page"""
    all_characters_url = anime_page_url + "/characters"
    return all_characters_url


def get_japanese_voice_actor(character_url_page):
    r = rate_limited_request(character_url_page)
    soup = BeautifulSoup(r.content, 'html5lib')
    actor_a_tags = soup.select("a[href*=https://myanimelist.net/people/]")[1::2]
    # Looking for the Japanese actor
    for actor_a_tag in actor_a_tags:
        actor_a_parent = actor_a_tag.parent
        language_td_tag = actor_a_parent.findChildren("div")[0]
        language = language_td_tag.findChildren("small")[0].contents[0]
        if language == "japanese" or language == "Japanese":
            return actor_a_tag.contents[0]
    return no_actor_string

# input is a dictionary of character:myanimelist_character_page_url
def get_character_url_dict(all_characters_url):
    r = rate_limited_request(all_characters_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    character_tags = soup.find_all("h3",{"class":"h3_character_name"})
    character_name_and_url = {}
    for ctag in character_tags:
        character_name_and_url[ctag.contents[0]] = ctag.parent['href']
    return(character_name_and_url)

def va_character_dict(char_page_url):
    va_char_dict = {}
    character_url_dict = get_character_url_dict(char_page_url)
    #print("Char url dict")
    #print(character_url_dict)
    for character in character_url_dict:
        url = character_url_dict[character]
        va = get_japanese_voice_actor(url)
        va_char_dict[va] = character
    #print("va_char_dict")
    #print(va_char_dict)
    return va_char_dict

def va_char_dict_by_anime_name(anime_name):
    url = get_character_webpage(anime_name)
    #print("URL")
    #print(url)
    return va_character_dict(url)

def format_name(name):
    if "," in name:
        [lastname, firstname] = name.split(", ")
        return firstname + " " + lastname
    return name

def show_character_overlaps(va_char_dict1, va_char_dict2):
    overlaps = []
    #print(va_char_dict1)
    #print(va_char_dict2)
    for va in va_char_dict1:
        if va == no_actor_string:
            continue
        if va in va_char_dict2:
            character1 = va_char_dict1[va]
            character2 = va_char_dict2[va]
            overlaps.append((va, character1, character2))
            name1 = format_name(character1)
            name2 = format_name(character2)
            print(name1, "and", name2, "have the same voice (", va, ")")
    if overlaps == []:
        print("There are no characters who share a voice!")
    return overlaps



#print( "This code takes as input two animes, searches on MyAnimeList for them, and figures out which characters across shows have the same (Japanese) voice.")
#print("\n Note: this code is slow by design (90 seconds to run). This prevents MyAnimeList from blocking the code.\n")

print("Enter a first anime")
a1 = input()
print("Enter a second anime")
a2 = input()
println()

print("Getting VAs for", a1)
s1 = va_char_dict_by_anime_name(a1)
print("Getting VAs for", a2)
s2 = va_char_dict_by_anime_name(a2)

println()
print("Characters with the same voice:")
show_character_overlaps(s1, s2)
