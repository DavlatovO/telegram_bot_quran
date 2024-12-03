import requests

sura=78
oyat=39
tafsir='uzb-muhammadsodikmu'





def getOyat(tafsir,sura,oyat):
    try:

        url_oyat1=f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{sura}.json"
        url_oyat2=f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{sura}/{oyat}.json"
        r1 = requests.get(url_oyat1)
        res1 = r1.json()
        
        total_verses = len(res1['chapter'])
        
        if oyat>total_verses:
            return "The verse number you input exceeded the total number of verses in this chapter. Please try again"
        else:
            r2 = requests.get(url_oyat2)
            res2 = r2.json()
            chapters = f"{res2['chapter']}:{res2['verse']} - "
            ayah = f"{res2['text']}"
            return chapters + ayah
    except:
        return 'Invalid input format. Use a single number (e.g. 78) or a colon-separated format (e.g., 78:8).'        
    
if __name__ == '__main__':
    print(getOyat(tafsir,sura,oyat))


