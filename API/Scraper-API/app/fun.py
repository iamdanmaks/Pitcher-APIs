def parse_tweets(topic, min_number):
    from twitterscraper import query_tweets

    response = query_tweets(topic, min_number)
    response = [tweet.__dict__ for tweet in response]

    for tweet in response:
        tweet['timestamp'] = tweet['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        tweet.pop('html', None)
    
    return response


def scrape_play_store_without_id(app_name, developer):
    import play_scraper
    response = play_scraper.search(app_name, page=10)
    
    for apps in response:
        if apps['developer'] == developer:
                return scrape_play_store_with_id(apps['app_id'])
    
    return None


def clean_play_store_review(response):
    response.pop('userName', None)
    response.pop('userImage', None)
    response.pop('date', None)
    response.pop('url', None)
    response.pop('userName', None)
    response.pop('title', None)
    response.pop('replyDate', None)
    response.pop('replyText', None)

    return response


def scrape_play_store_with_id(id):
    from requests import get
    from bs4 import BeautifulSoup

    results = {}
    html = BeautifulSoup(get('https://play.google.com/store/apps/details?id={}'.format(id)).content,
     'html.parser')
    hist = html.findAll('span', {'class': 'L2o20d'})

    results['score'] = float(html.find('div', {'class': 'BHMmbe'}).get_text())
    
    results['installs'] = html.find_all('div', 
        {'class': 'hAyfc'})[2].get_text().replace('Installs', '')
    
    results['reviews'] = int(html.find(
        'span', {'class': 'AYi5wd TBRnV'}).get_text().replace(',', ''))
    
    results['histogram'] = {}
    results['histogram']['1'] = int(
        hist[4]['title'].replace('&nbsp;', '').replace(',', ''))
    
    results['histogram']['2'] = int(
        hist[3]['title'].replace('&nbsp;', '').replace(',', ''))
    
    results['histogram']['3'] = int(
        hist[2]['title'].replace('&nbsp;', '').replace(',', ''))
    
    results['histogram']['4'] = int(
        hist[1]['title'].replace('&nbsp;', '').replace(',', ''))
    
    results['histogram']['5'] = int(
        hist[0]['title'].replace('&nbsp;', '').replace(',', ''))
    
    return results
