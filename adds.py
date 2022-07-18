# addons functions
from newsapi import NewsApiClient
from datetime import date, timedelta
def get_news(ner_dict):
  answer = ''
  if "ORG" or "PRODUCT" or "PERSON" in ner_dict:
    try:
      phrase = ner_dict["ORG"]
    except:
      try:
        phrase = list(ner_dict.values())[0]
      except:
        return "Failed to extract the name of known company from your utterance."  
    newsapi = NewsApiClient(api_key='your_api_key')
    my_date = date.today() - timedelta(days = 30)
    articles = newsapi.get_everything(q=phrase,
                                  from_param = my_date.isoformat(),
                                  language="en",
                                  sort_by="relevancy",
                                  page_size = 3)
    for article in articles['articles']:
      answer = answer + article['publishedAt'] + '\n' + article['description'] + '\n' + article['url']+"\n\n"
  else:
    answer = "Failed to extract the name of known company from your utterance."
  return answer
