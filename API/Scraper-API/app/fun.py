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
    
    try:
        score_gen = results['score'] * results['reviews']

        four_percent = int(hist[1]['style'][hist[1]['style'].find(' ') + 1 : -1]) / 100
        three_percent = int(hist[2]['style'][hist[2]['style'].find(' ') + 1 : -1]) / 100
        two_percent = int(hist[3]['style'][hist[3]['style'].find(' ') + 1 : -1]) / 100
        one_percent = int(hist[4]['style'][hist[4]['style'].find(' ') + 1 : -1]) / 100

        five_count = score_gen / (1 + four_percent + three_percent + two_percent + one_percent)

        results['histogram']['1'] = int(one_percent * five_count)
        
        results['histogram']['2'] = int((two_percent * five_count) / 2)
        
        results['histogram']['3'] = int((three_percent * five_count) / 3)
        
        results['histogram']['4'] = int((four_percent * five_count) / 4)
        
        results['histogram']['5'] = int(five_count / 5)

        results['reviews'] = results['histogram']['1'] + results['histogram']['2'] + results['histogram']['3']
        results['reviews'] += results['histogram']['4'] + results['histogram']['5']
    
    except Exception as e:
        print('\n\n\n',e,'\n\n\n')
        results['histogram'] = 'score is too low or there is too small number of reviews'

    return results
