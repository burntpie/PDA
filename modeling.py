from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from googlesearch import search
from bs4 import BeautifulSoup
import requests
# import time

class Article:
    def __init__(self, url, title, full_article, summarized_article, similarity_score) -> None:
        self.url = url
        self.title = title
        self.full_article = full_article
        self.summarized_article = summarized_article
        self.similarity_score = similarity_score

    def get(self):
        print(f"url: {self.url}")
        print(f"title: {self.title}")
        print(f"full_article: {self.full_article}")
        print(f"summarized_article: {self.summarized_article}")
        print(f"similarity_score: {self.similarity_score}")
        print()


summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")
similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def summarize(text):
    summary = summarizer(text, max_length=80, min_length=0, do_sample=False)

    return summary[0].get('summary_text')

def similarity_check(text1, text2):
    embedding_1= similarity_model.encode(text1, convert_to_tensor=True)
    embedding_2 = similarity_model.encode(text2, convert_to_tensor=True)

    res_tensor = util.pytorch_cos_sim(embedding_1, embedding_2)

    return res_tensor.item()

def misinformation_check(input_text, trusted_sources, article_count):
    if not trusted_sources:
        raise Exception("Error: Must include trusted sources")

    similarity_list = []
    article_list = []

    if len(input_text) > 50:
        text = summarize(input_text)
    else:
        text = input_text
    
    for source in trusted_sources:
        if source == "CNA":
            text += " site:channelnewsasia.com"
        elif source == "today":
            text += " site:todayonline.com"
        elif source == "gov.sg":
            text += " site:gov.sg"
        text += " OR"

    search_term = text[:-3]
    print(search_term)
    url_list = search(search_term, tld="co.in", num=article_count, stop=article_count, pause=2)

    headers = { 'accept':'*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7,la;q=0.6',
        'cache-control':'no-cache',
        'dnt':'1',
        'pragma':'no-cache',
        'referer':'https',
        'sec-fetch-mode':'no-cors',
        'sec-fetch-site':'cross-site',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }

    for url in url_list:
        page = requests.get(url, headers=headers)
        if page.status_code == 200:
            try:
                soup = BeautifulSoup(page.content, "lxml")
                res_soup = soup.find('main', class_='main-content')
                title = res_soup.article['title']
                elements = res_soup.find_all('p')
                full_article = ""
                for element in elements:
                    if element == None:
                        continue
                    full_article += " "
                    full_article += element.text.strip()
            except Exception as e:
                title = None
                full_article = None
                print(f"Scraping Error! - {e}")

            try:
                summarized_article = summarize(full_article)
            except Exception as e:
                summarized_article = None
                print(f"Summarizing Error! - {e}")

            try:
                similarity_score = similarity_check(input_text, full_article)
                similarity_list.append(similarity_score)
            except Exception as e:
                similarity_score = None
                print(f"Similarity Comparision Error! - {e}")

        else:
            print(f"Unable to retrieve page - Error Code {page.status_code}")
        
        article_list.append(Article(url, title, full_article, summarized_article, similarity_score))

        # time.sleep(1)

    try:
        true_score = round(sum(similarity_list) / len(similarity_list)*100, 2)
        print(f"The Input Text is likely to be {true_score}% true.")
    except Exception as e:
        true_score = None
        print(f"Score Error! list of scores: {similarity_list}")
        print(e)

    return article_list, search_term, true_score
        

# res_list = misinformation_check('monkeypox has killed millions in Singapore', ["CNA", "today"], 3)

# for article in res_list:
#     article.get()
