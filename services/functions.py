import requests

def getOyat(tafsir, surah, ayah):
    try:
        # Base URLs for Arabic text and translation
        arabic_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/ara-quranuthmanienc/{surah}/{ayah}.json"
        check_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{surah}.json"
        translation_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{surah}/{ayah}.json"

        # Fetch Arabic verse
        arabic_response = requests.get(arabic_url)
        arabic_response.raise_for_status()
        arabic_data = arabic_response.json()

        # Fetch translation
        translation_response = requests.get(translation_url)
        translation_response.raise_for_status()
        translation_data = translation_response.json()

        #Check
        check_response = requests.get(check_url)
        check_response.raise_for_status()
        check_data = check_response.json()

        total_verses = len(check_data['chapter'])
        if ayah>total_verses:
            return "The verse number you input exceeded the total number of verses in this chapter. Please try again"
        else:

            # Combine Arabic and translation
            chapter_verse = f"{arabic_data['chapter']}:{arabic_data['verse']}"
            arabic_text = arabic_data['text']
            translation_text = translation_data['text']

            # Return formatted result
            return f"""📖 <b>{arabic_text}</b> ({chapter_verse})\n\n<i>{translation_text}<b>({chapter_verse})</b>.</i>"""

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"
    except KeyError:
        return "Invalid surah or ayah number. Please check your input and try again."
    except Exception as e:
        return f"An unexpected error occurred: {e}"




# Function to fetch Surah data
def getSurah(tafsir, surah):
    base_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{surah}.json"
    compulsory_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/ara-quranuthmanienc/{surah}.json"
    
    try:
        # Ensure the surah number is valid
        if surah < 1 or surah > 114:
            return None, "The Surah number must be between 1 and 114."

        # Fetch translation data
        translation_response = requests.get(base_url)
        translation_response.raise_for_status()
        translation_data = translation_response.json()

        # Fetch Arabic verses
        arabic_response = requests.get(compulsory_url)
        arabic_response.raise_for_status()
        arabic_data = arabic_response.json()

        # Combine Arabic and translated verses
        verses = []
        for arabic_verse, translation_verse in zip(arabic_data["chapter"], translation_data["chapter"]):
            verse_text = (
               f"📖 <b>{arabic_verse['text']}</b> <b>({arabic_verse['chapter']}:{arabic_verse['verse']})</b>\n\n\n"
               f"       <i>{translation_verse['text']}</i> <b>({translation_verse['chapter']}:{translation_verse['verse']}).</b>\n"
            )
            verses.append(verse_text)

        return verses, None

    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data: {e}"
    except KeyError:
        return None, "Invalid response format from the API."


# Example Usage
if __name__ == '__main__':
    tafsir = "uzb-muhammadsodikmu"
    surah = 105  # Surah Al-Fil
    ayah = 5
    print(getOyat(tafsir, surah, ayah))








































# check_response = requests.get(check_url)
#         check_response.raise_for_status()
#         check_data = check_response.json()


# import requests

# sura=78
# oyat=39
# tafsir='uzb-muhammadsodikmu'





# def getOyat(tafsir,surah,oyat):
#     try:

#         base_url=f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{surah}.json"
#         url_oyat2=f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{surah}/{oyat}.json"
#         compulsory_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/ara-kingfahadquranc/{surah}/{oyat}.json"
   
#         # Fetch translation data
#         translation_response = requests.get(base_url)
#         translation_response.raise_for_status()
#         translation_data = translation_response.json()

#          # Fetch Arabic verses
#         arabic_response = requests.get(compulsory_url)
#         arabic_response.raise_for_status()
#         arabic_data = arabic_response.json()
        
#         total_verses = len(translation_data['chapter'])
        
#         if oyat>total_verses:
#             return "The verse number you input exceeded the total number of verses in this chapter. Please try again"
#         else:
#             r2 = requests.get(url_oyat2)
#             res2 = r2.json()
#             chapters = f"{res2['chapter']}:{res2['verse']} - "
#             ayah = f"{res2['text']}"
#             return chapters + ayah
#     except:
#         return 'Invalid input format. Use a single number (e.g. 78) or a colon-separated format (e.g., 78:8).'        
    
# if __name__ == '__main__':
#     print(getOyat(tafsir,sura,oyat))


