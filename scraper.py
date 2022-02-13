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
    time.sleep(0.5)
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

def remove_spaces(s):
    q = s.replace(" ","")
    return q.replace("\n","")

# input is a dictionary of character:myanimelist_character_page_url
def get_va_character_dict(all_characters_url):
    va_character_dict = {}
    r = rate_limited_request(all_characters_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    character_tables = soup.find_all("table", {"class":"js-anime-character-table"})
    """ Find the character, VA, and language. We filter for only Japanese"""
    for table in character_tables:
        character = table.findChildren("h3", {"class":"h3_character_name"})[0].contents[0]
        va_table = table.findChildren("tr", {"class":"js-anime-character-va-lang"})

        for va_table_element in va_table:
            va = va_table_element.findChildren("a")[0].contents[0]
            lang = va_table_element.findChildren("div", {"class":"spaceit_pad js-anime-character-language"})[0].contents[0]
            lang = remove_spaces(lang)
            if lang == "Japanese" or lang == "japanese":
                va_character_dict[va]=character
    return va_character_dict

def va_char_dict_by_anime_name(anime_name):
    url = get_character_webpage(anime_name)
    return get_va_character_dict(url)

def format_name(name):
    if "," in name:
        [lastname, firstname] = name.split(", ")
        return firstname + " " + lastname
    return name

def show_character_overlaps(va_char_dict1, va_char_dict2):
    overlaps = []
    for va in va_char_dict1:
        if va in va_char_dict2:
            character1 = va_char_dict1[va]
            character2 = va_char_dict2[va]
            overlaps.append((va, character1, character2))
            name1 = format_name(character1)
            name2 = format_name(character2)
            print(name1, "and", name2, "(voiced by", va, ")")
    if overlaps == []:
        print("There are no characters who share a voice!")
    return overlaps

print("Enter a first anime")
a1 = input()
print("Enter a second anime")
a2 = input()
print()

print("Getting VAs for", a1)
s1 = va_char_dict_by_anime_name(a1)
print("Getting VAs for", a2)
s2 = va_char_dict_by_anime_name(a2)

print()
print("Characters with the same voice:")
show_character_overlaps(s1, s2)
