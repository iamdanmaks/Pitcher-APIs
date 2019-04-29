def clean_text(text):
    import re
    from bs4 import BeautifulSoup
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    

    #decoding HTML elements in text
    bs = BeautifulSoup(text, 'lxml')
    text = bs.get_text()
    #replacing URLs which start with https, http or www 
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', text)
    #replacing usernames
    text = re.sub('@[^\s]+','',text)
    #replacing of hashtags
    text = re.sub(r'#([^\s]+)', r'\1', text)
    #rewriting of repeating words
    text = text.strip('\'"')
    rpt_regex = re.compile(r"(.)\1{1,}", re.IGNORECASE)
    text = rpt_regex.sub(r"\1\1", text)
    #decoding and replacing of UTF-8 special chars
    text.replace(u"\ufffd", " ? ")
    #deleting repeating spaces
    text = re.sub('[\s]{2,}', ' ', text)
    #tokenizing
    tokens = text.split()
    #deleting tokens with length less than 2
    tokens = [word for word in tokens if len(word) > 2]
    #joining the string
    text = ' '.join(tokens).strip()
    return text


def replace_parenth(arr):
       return [text.replace(')', '[)}\]]').replace('(', '[({\[]')
               for text in arr]
    

def regex_join(arr):
    return '(' + '|'.join( arr ) + ')'


def get_polyglot_sentiment(text):
    text = clean_text(text)

    from polyglot.text import Text as T
    text = T(text)

    try:
        return text.polarity
    except:
        from polyglot.downloader import downloader
        downloader.download("sentiment2.{}".format(text.language.code))
        return text.polarity


def get_vader_sentiment(text):
    from polyglot.detect import Detector

    if Detector(text).language.code == 'en':
        text = clean_text(text)
        
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        return SentimentIntensityAnalyzer().polarity_scores(text)['compound']

    else:
        return float('inf')


def generate_sentiment_score(text, analyzer_name):
    sentiment = 0
    
    if analyzer_name == 'vader':
        sentiment = get_vader_sentiment(text)
    else:
        sentiment = get_polyglot_sentiment(text)

    return (((sentiment + 1) * 10) / 2)
