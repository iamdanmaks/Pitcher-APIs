from requests import get
from json import loads
from app.functions import generate_sentiment_score
from app import db


def update_play_store(conducted_research, clf, app_id='', app_name='', app_dev=''):
    from app.models import PlayStoreResearch, PlayStoreReview, Analyzer

    result = PlayStoreResearch(id=conducted_research.id)

    if app_id is not '':
        data = loads(get('http://localhost:8000/scraper/api/v1.0/data/play_store?id={}'.format(
            app_id)).content)
    
    elif app_name is not '' and app_dev is not '':
        data = loads(get('http://localhost:8000/scraper/api/v1.0/data/play_store?app_name={}&developer={}'.format(
            app_name, app_dev)).content)
        
    result.maxReviews = data['results']['scores']['reviews']
    result.downloads = data['results']['scores']['installs']
    result.averageRating = data['results']['scores']['score']
    result.rateOneCount = data['results']['scores']['histogram']['1']
    result.rateTwoCount = data['results']['scores']['histogram']['2']
    result.rateThreeCount = data['results']['scores']['histogram']['3']
    result.rateFourCount = data['results']['scores']['histogram']['4']
    result.rateFiveCount = data['results']['scores']['histogram']['5']
    
    for rev in data['results']['reviews']:
        try:
            review = PlayStoreReview(id=rev['id'], rate=rev['score'], 
                text=rev['text'], 
                sentimentScore=generate_sentiment_score(rev['text'], analyzer_name=clf))
            result.reviews.append(review)
            db.session.add(review)
        
        except:
            continue

    return result


def update_twitter(conducted_research, clf, keywords):
    pass


def update_news(conducted_research, clf, search_query, preffered_language):
    from app.models import NewsResearch, NewsArticle

    result = NewsResearch(id=conducted_research.id)
    
    try:
        data = loads(get(
            'http://localhost:8000/scraper/api/v1.0/data/news_and_blogs?topic={}&lang={}'.format(
                search_query, preffered_language
            )
        ).content)
    except:
        return object()

    count = 0
    pos_count = 0
    neg_count = 0
    
    for article in data['results']:
        try:
            artcl = NewsArticle(
                link=article['link'], 
                source=article['source'], 
                text=article['text'], 
                title=article['title']
            )
            result.news_list.append(artcl)
            db.session.add(artcl)
        
        except:
            continue

    result.amount = count
    result.pos_count_general = pos_count
    result.neg_count_general = neg_count

    return result


def update_trends(res_id, clf, query, lang, reg):
    from app.models import SearchTrends, DayInterest, RelatedTopic, TopQuery, RisingQuery
    
    search = SearchTrends()
    search.id = res_id

    try:
        data = loads(get('http://localhost:8000/scraper/api/v1.0/data/trends?topic={}&lang={}&reg={}'.format(query, lang, reg)).content)
    except:
        return object()
    
    search.query = query

    from datetime import datetime

    for qdate, qinterest in loads(data['result']['interest'])[query].items():
        try:
            day = DayInterest(
                date=datetime.fromtimestamp(int(qdate) / 1000),
                interest = int(qinterest) 
            )
            search.days.append(day)
            db.session.add(day)
        
        except:
            continue

    temp = loads(data['result']['related_topics'])
    
    for ind in range(len(temp['title'])):
        day_ex = db.session.query(RelatedTopic).filter(
            db.and_(
                RelatedTopic.search_id == search.id, 
                RelatedTopic.topic == temp['title'][str(ind)]
            )
        ).first()
        
        if day_ex is None:
            try:
                day = RelatedTopic(
                    topic=temp['title'][str(ind)],
                    value=int(temp['value'][str(ind)]),
                    sentiment=generate_sentiment_score(
                        temp['title'][str(ind)],
                        clf
                    )
                )
                search.related.append(day)
                db.session.add(day)

            except:
                continue
            
        else:
            day_ex.value = int(temp['value'][str(ind)])

    temp = loads(data['result']['top_queries'])
    
    for ind in range(len(temp['value'])):
        top_ex = db.session.query(TopQuery).filter(
            db.and_(
                TopQuery.search_id == search.id, 
                TopQuery.query == temp['query'][str(ind)]
            )
        ).first()
        
        if top_ex is None:
            try:
                top = TopQuery(
                    query=temp['query'][str(ind)],
                    value=int(temp['value'][str(ind)]),
                    sentiment=generate_sentiment_score(
                        temp['query'][str(ind)],
                        clf
                    )
                )
                search.top.append(top)
                db.session.add(top)

            except:
                continue
            
        else:
            top_ex.value = int(temp['value'][str(ind)])
    
    temp = loads(data['result']['rising_queries'])
    
    for ind in range(len(temp['value'])):
        rise_ex = db.session.query(RisingQuery).filter(
            db.and_(
                RisingQuery.search_id == search.id, 
                RisingQuery.query == temp['query'][str(ind)]
            )
        ).first()
        
        if rise_ex is None:
            try:
                rise = RisingQuery(
                    query=temp['query'][str(ind)],
                    value=int(temp['value'][str(ind)]),
                    sentiment=generate_sentiment_score(
                        temp['query'][str(ind)],
                        clf
                    )
                )
                search.rising.append(rise)
                db.session.add(rise)

            except:
                continue
            
        else:
            rise_ex.value = int(temp['value'][str(ind)])

    return search
