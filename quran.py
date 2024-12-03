import requests



def getSurah(tafsir, sura):
    url_sura = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{sura}.json"
    
    try:
        if sura <= 114:
            
            r = requests.get(url_sura)
            r.raise_for_status()  # Raise an error for HTTP issues
            res = r.json()
            
            # Initialize an empty string to store the formatted text
            formatted_text = ""

            # Extract and format each verse
            for verse_num in res['chapter']:
                formatted_text += f"{verse_num['text']}({verse_num['chapter']}:{verse_num['verse']})."
            return formatted_text
        
        else:
            return "The surah number exceeded the total number of surahs in the Qur'an(114)"
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return 'Unknown issue'
    except ValueError:
        print("Invalid JSON response")
        return 'Unknown issue'

if __name__ == '__main__':
    tafsir = 'uzb-muhammadsodikmu'
    sura = 45
    result = getSurah(tafsir, sura)
    
    if result:
        print(result)
