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
            review = PlayStoreReview(
                id=rev['id'],
                playStoreResearchId=result.id, 
                rate=rev['score'], 
                text=rev['text'], 
                sentimentScore=generate_sentiment_score(rev['text'], analyzer_name=clf)
            )
            result.reviews.append(review)
            db.session.add(review)
        
        except:
            continue

    return result


def update_twitter(conducted_research, clf, keywords):
    from app.models import TwitterResearch, Tweet
    from datetime import datetime


    result = TwitterResearch(id=conducted_research.id)

    try:
        data = loads(get(
            'http://localhost:8000/scraper/api/v1.0/data/twitter?topic={0}&min={1}'.format(
                keywords, 201
            )
        ).content)
    except Exception as e:
        print(e)
        return {}
    
    count = 0
    pos_count = 0
    neg_count = 0
    
    new_d = []
    for x in data['tweets']:
        if x not in new_d:
            new_d.append(x)
    
    data['tweets'] = new_d

    for tweet in data['tweets']:
        try:
            temp = generate_sentiment_score(tweet['text'], analyzer_name=clf)
            twt = Tweet(
                id=tweet['id'],
                twitterResearchId=result.id,
                text=tweet['text'],
                authorUserName=tweet['user'],
                authorFullName=tweet['fullname'],
                source=tweet['url'],
                timestamp=datetime.strptime(tweet['timestamp'], '%Y-%m-%d %H:%M:%S'),
                sentimentScore=temp
            )
            result.tweets.append(twt)
            db.session.add(twt)

            if temp > 6.0:
                pos_count += 1
            elif temp < 4.0:
                neg_count += 1
            count += 1

        except Exception as e:
            print(e)
    
    result.pos_count = pos_count
    result.neg_count = neg_count
    result.tweetsCount = count

    return result


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
        return {}

    count = 0
    pos_count = 0
    neg_count = 0
    
    for article in data['results']:
        try:
            temp = generate_sentiment_score(article['text'], analyzer_name=clf)
            artcl = NewsArticle(
                link=article['link'], 
                news_id=result.id,
                text=article['text'], 
                title=article['title'],
                sentimentScore=temp,
                source=article['source']['href'] + '||' + article['source']['title']
            )
            result.news_list.append(artcl)
            db.session.add(artcl)
        
            if temp > 6.0:
                pos_count += 1
            elif temp < 4.0:
                neg_count += 1
            count += 1

        except Exception as e:
            print(e)

    result.amount = count
    result.pos_count_general = pos_count
    result.neg_count_general = neg_count

    return result


def update_trends(res_id, clf, query, lang, reg):
    from app.models import SearchTrends, DayInterest, RelatedTopic, TopQuery, RisingQuery, CountryInterest
    
    print('\n\n\n',res_id,'\n\n\n')

    search = db.session.query(SearchTrends).filter(SearchTrends.id == res_id).first()
    #search = SearchTrends.query.filter_by(id=res_id).first()

    try:
        data = loads(get('http://localhost:8000/scraper/api/v1.0/data/trends?topic={}&lang={}&reg={}'.format(query, lang, reg)).content)
    except:
        return {}
    
    search.query = query

    for q in search.days:
        db.session.delete(q)
        search.days.remove(q)
    
    for q in search.related:
        db.session.delete(q)
        search.related.remove(q)
    
    for q in search.top:
        db.session.delete(q)
        search.top.remove(q)
    
    for q in search.rising:
        db.session.delete(q)
        search.rising.remove(q)

    for q in search.countries:
        db.session.delete(q)
        search.rising.remove(q)

    print(data['result']['countries'])
    for countries, interests in data['result']['countries'].items():
        try:
            cntr = CountryInterest(
                country=countries,
                interest=interests,
                search_id=search.id
            )
            search.countries.append(cntr)
            db.session.add(cntr)

        except Exception as e:
            print(e)

    from datetime import datetime

    for qdate, qinterest in loads(data['result']['interest'])[query].items():
        try:
            day = DayInterest(
                date=datetime.fromtimestamp(int(qdate) / 1000),
                interest = int(qinterest),
                search_id=search.id 
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
                    ),
                    search_id=search.id
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
                    ),
                    search_id=search.id
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
                    ),
                    search_id=search.id
                )
                search.rising.append(rise)
                db.session.add(rise)

            except:
                continue
            
        else:
            rise_ex.value = int(temp['value'][str(ind)])
    
    db.session.commit()
