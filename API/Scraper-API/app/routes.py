from sanic.response import json
from app import app
import os


STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static\\')
app.static('/static', STATIC_FOLDER)
app.static('/favicon.ico', os.path.join(STATIC_FOLDER, 'img', 'favicon.ico'))
print(STATIC_FOLDER)

@app.route("/scraper/api/v1.0/data/twitter")
async def twiter(request):
    try:
        topic = request.args['topic'][0]
        min_number = int(request.args['min'][0])
    except:
        return json({'response': False, 'message': 'arguments are missing', 'tweets': []})
    
    if topic is None or topic is '' or min_number is None or min_number is '':
        return json({'response': False, 'message': 'arguments have wrong format', 'tweets': []})

    from app.fun import parse_tweets
    
    return json({'response': True, 'message': 'done', 'tweets': parse_tweets(topic, min_number)})


@app.route('/scraper/api/v1.0/data/trends', methods=['GET'])
async def google_trends(request):
    if request.method == 'GET':
        topic = request.args.get('topic').split(',')
        lang = request.args.get('lang')
        region = request.args.get('reg')
    
    else:
        return json({'response': False, 'message': 'Wrong HTTP method', 'results': []})

    if topic is None or topic is '':
        return json({'response': False, 'message': 'Not enough arguments', 'results': []})

    from pytrends.request import TrendReq

    pytrends = TrendReq(hl='{}-{}'.format(lang, region), tz=360)
    pytrends.build_payload(topic)

    res = pytrends.interest_over_time()
    res.drop('isPartial', axis=1, inplace=True)

    rel_topics = pytrends.related_topics()[topic[0]]
    rel_topics.drop('mid', axis=1, inplace=True)

    rel_queries = pytrends.related_queries()[topic[0]]

    countries = pytrends.interest_by_region(resolution='COUNTRY')
    countries = countries[(countries.T != 0).any()]

    from json import loads

    countries = loads(countries.to_json())[topic[0]]

    return json({'message':'done', 'response': True, 'result': {'interest': res.to_json(), 'related_topics': rel_topics.to_json(), 
    'top_queries': rel_queries['top'].to_json(), 'rising_queries': rel_queries['rising'].to_json(), 'countries': countries}})


@app.route('/scraper/api/v1.0/data/play_store', methods=['GET'])
async def play_store(request):
    final_dict = {'response': False, 'message': 'arguments are missing', 'results': {}}

    try:
        app_name = request.args['app_name'][0]
        developer = request.args['developer'][0]

        if app_name is None or app_name == '' or developer is None or developer == '':
            final_dict['message'] = 'args have wrong format'
            return json(final_dict)
        
        from app.fun import scrape_play_store_without_id
        apps = scrape_play_store_without_id(app_name, developer)

        if apps is None:
            final_dict['message'] = 'no app found'
            return final_dict

        from app.fun import clear_play_store_review

        final_dict['response'] = True
        final_dict['message'] = 'done'
        final_dict['results']['scores'] = apps
        final_dict['results']['reviews'] = loads(get('https://still-plateau-10039.herokuapp.com/reviews?id={}'.format(apps['id'])).content)

        for review in final_dict['results']['reviews']:
            review = clean_play_store_review(review)

        return json(final_dict)
    
    except:
        try:
            id = request.args['id'][0]

            if id is None or id == '':
                final_dict['message'] = 'args have wrong format'
                return json(final_dict)

            from app.fun import scrape_play_store_with_id
            apps = scrape_play_store_with_id(id)

            if apps is None or apps is {}:
                final_dict['message'] = 'no app found'
                return json(final_dict)

            from app.fun import clean_play_store_review
            from requests import get
            from json import loads

            final_dict['response'] = True
            final_dict['message'] = 'done'
            final_dict['results']['scores'] = apps
            final_dict['results']['reviews'] = loads(get('https://still-plateau-10039.herokuapp.com/reviews?id={}'.format(id)).content)

            for review in final_dict['results']['reviews']:
                review = clean_play_store_review(review)

            return json(final_dict)
        except Exception as e:
            print('\n\n\n', e,'\n\n\n')
            final_dict['message'] = 'exception'
            return json(final_dict)


@app.route('/scraper/api/v1.0/data/news_and_blogs', methods=['GET'])
async def news(request):
    final_dict = {'response': False, 'message': 'arguments are missing', 'results': []}

    try:
        topic = request.args['topic'][0].split(' ')[0]
        print(topic)
        lang = request.args['lang'][0]
    except:
        return json(final_dict)

    if topic is None or topic is '' or lang is None or lang is '':
        final_dict['message'] = 'arguments have wrong format'
        return json(final_dict)

    from feedparser import parse
    from newspaper import Article

    feed = parse('https://news.google.com/rss/search?q={0}&hl=en-US&gl=US&ceid=US:en'.format(topic, lang))
    print(feed)
    for entry in feed.entries[:10]:
        print(entry)
        try:
            news = Article(entry.link)
            news.download()
            news.parse()
            print('done')
        except:
            continue
        
        final_dict['results'].append({'title': entry.title, 'link': entry.link, 'source': entry.source, 'text': news.text})

    final_dict['response'] = True
    final_dict['message'] = 'done'
    return json(final_dict)
