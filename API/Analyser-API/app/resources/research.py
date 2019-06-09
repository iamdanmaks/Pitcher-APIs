from flask_restful import Resource
from app import db
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from app.models import (User, Research, ResearchKeyword, 
    ResearchModule, ConductedResearch, SearchTrends, Analyzer, 
    UserResearchPermission, likes, subscriptions)
from app.resources.request_parser import (research_filters, 
    create_research, subscriptions_likes_parser)


def get_paginated_list(results, url, start, limit):
    start = int(start)
    limit = int(limit)
    count = len(results)
    if count < start or limit < 0:
        abort(404)
    
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj


class MyResearch(Resource):
    @jwt_required
    def post(self):
        data = create_research.parse_args()
        
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        try:
            new_research = Research()
            new_research.topic = data.get('topic')
            new_research.description = data.get('description')

            for word in data.get('keywords'):
                new_keyword = ResearchKeyword(
                    keyword=word, 
                    researchId=new_research.id
                )
                new_research.keywords.append(new_keyword)
                db.session.add(new_keyword)
            
            print('\n\n\n',data.get('modules'),'\n\n\n')
            for module in data.get('modules'):
                new_module = ResearchModule(
                    module=module,
                    researchId=new_research.id
                )
                new_research.modules.append(new_module)
                db.session.add(new_module)
            
            new_research.updateInterval = data.get('update_interval')
            new_research.type_of_research = data.get('isPublic')
            new_research.analysers = data.get('analysers')
            new_research.appId = data.get('app_id')
            new_research.appName = data.get('app_name')
            new_research.appDev = data.get('app_dev')

            if 'search' in data.get('modules'):
                new_search = SearchTrends(id=new_research.id)
                new_search.query = ' '.join(data.get('keywords')[:5])
                new_research.search.append(new_search)
                db.session.add(new_search)

            user_res = UserResearchPermission(
                userId=current_user.id,
                researchId=new_research.id,
                permission=True
            )
            
            user_res.researches.append(new_research)
            current_user.my_researches.append(user_res)
            current_user.owners.append(new_research)
            
            db.session.add(new_research)
            db.session.commit()
        
        except Exception as e:
            return {
                'response': False,
                'message': 'Internal server error'
            }, 500

        return {
            'response': True,
            'id': new_research.id,
            'message': 'Research {} was created'.format(new_research.topic)
        }

    def get(self):
        from app import db
        from flask import request
        from sqlalchemy import desc

        research = Research.find_by_id(int(request.args.get('res_id')))
        owner = User.find_by_id(research.ownerId)

        try:
            last = db.session.query(
                        ConductedResearch.date
                    ).filter(
                        ConductedResearch.researchId == research.id
                    ).order_by(
                        desc(ConductedResearch.date)
                    ).first()[0]
        except:
            last = research.creationDate.strftime('%d.%m.%Y')

        return {
                'id': research.id,
                'topic': research.topic,
                'description': research.description,
                'creation': research.creationDate.strftime('%d.%m.%Y'),
                'last_update': last,
                'views': research.views,
                'owner': {
                    'id': owner.id,
                    'username': owner.username,
                    'fullname': owner.fullname
                },
                'keywords': [x[0] for x in db.session.query(ResearchKeyword.keyword).filter(
                    ResearchKeyword.researchId == research.id
                ).all()],
                'active_modules': [x[0] for x in db.session.query(ResearchModule.module).filter(
                    ResearchModule.researchId == research.id
                ).all()],
                'likes': len(db.session.query(likes).filter(likes.c.research_id == research.id).all()),
                'subscriptions': len(db.session.query(subscriptions).filter(
                    subscriptions.c.research_id == research.id
                ).all())
            }
        
    @jwt_required
    def put(self):
        from flask import request
        from sqlalchemy import and_
        from requests import get
        from json import loads

        res_id = int(request.args.get('id'))
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        permissions = db.session.query(UserResearchPermission).filter(
            and_(UserResearchPermission.userId == current_user.id,
                UserResearchPermission.researchId == res_id)
        ).first()

        if permissions is None:
            return {
                "message": "You don't have permission to edit this research"
            }, 400
        
        response = get('http://localhost:5000/ml/api/v1.0/update/{}'.format(res_id)).content
        print(response)
        response = loads(response)
        
        if response['done'] == False:
            return {
                "message": "Internal server error"
            }, 500

        current_res = Research.find_by_id(res_id)
        itters = ConductedResearch.query.filter_by(researchId=res_id).all()
        print(itters[-1].id)

        current_res.conducted.append(itters[-1])
        db.session.add(itters[-1])
        db.session.commit()

        return {
            "message": "updated"
        }


class MyResearches(Resource):
    @jwt_required
    def get(self):
        from flask import request
        from sqlalchemy import desc
        keyword = request.args.get('keyword')

        current_username = get_jwt_identity()['username']
        print(current_username)
        current_user = User.find_by_username(current_username)

        data = {}
        result = []
        
        from datetime import datetime, timedelta

        try:
            data['start_date'] = datetime.strptime(request.args.get('start_date'), '%d.%m.%Y')
        except:
            pass

        try:
            data['end_date'] = datetime.strptime(request.args.get('end_date'), '%d.%m.%Y') + timedelta(days=1)
        except:
            pass
        
        try:
            data['modules'] = set(request.args.get('modules').split(','))
        except:
            pass

        def to_json(x):
            from app import db
            return {
                'id': x.id,
                'topic': x.topic,
                'description': x.description,
                'creation': x.creationDate.strftime('%d.%m.%Y'),
                'views': x.views,
                'likes': len(db.session.query(likes).filter(likes.c.research_id == x.id).all())
            }

        if request.args.get('sort_way') is None or request.args.get('sort_way') == 'creation':
            result = Research.query.whooshee_search(
                keyword).order_by(
                    desc(Research.creationDate)).all()[::-1]
        
        elif request.args.get('sort_way') == 'last_update':
            from app import db
            result = Research.query.whooshee_search(
                keyword).all()
            result = sorted(
                result,
                key=lambda x: db.session.query(
                        ConductedResearch.date
                    ).filter(
                        ConductedResearch.researchId == x.id
                    ).order_by(
                        desc(ConductedResearch.date)
                    ).first(),
                reverse=True
            )

        elif request.args.get('sort_way') == 'views':
            result = Research.query.whooshee_search(
                keyword).order_by(
                    Research.views.desc()).all()
            result = sorted(
                result, 
                key=lambda x: x.views, 
                reverse=True
            )
        
        elif request.args.get('sort_way') == 'popularity':
            from app import db
            result = Research.query.whooshee_search(
                keyword).all()
            result = sorted (
                result, 
                key=lambda x: len(db.session.query(likes).filter(likes.c.research_id == x.id).all()), 
                reverse=True
            )

        elif request.args.get('sort_way') == 'subscribers':
            from app import db
            result = Research.query.whooshee_search(
                keyword).all()
            result = sorted (
                result, 
                key=lambda x: len(db.session.query(subscriptions).filter(subscriptions.c.research_id == x.id).all()), 
                reverse=True
            )

        from app import db
        my_res_ids = db.session.query(UserResearchPermission.researchId).filter(
            UserResearchPermission.userId == current_user.id
        ).all()
        result = [x for x in result if x.id in [i[0] for i in my_res_ids]]

        if data.get('end_date') is not None:
            result = [x for x in result if x.creationDate <= data.get('end_date')]

        if data.get('start_date') is not None:
            result = [x for x in result if x.creationDate >= data.get('start_date')]
        
        if data.get('modules') is not None:
            def get_modules(x):
                return [res.module for res in ResearchModule.query.filter_by(researchId=x.id).all()]
            
            result = [x for x in result if data.get('modules').issubset(get_modules(x))]

        if request.args.get('analyser') is not None:
            result = [x for x in result if x.algos == request.args.get('analyser')]

        return get_paginated_list(
            list(map(lambda x: to_json(x), result)), 
            '/research/my', 
            start=request.args.get('start', 1), 
            limit=request.args.get('limit', 20)
        )


class UsersResearches(Resource):
    def get(self):
        from flask import request
        from sqlalchemy import desc
        keyword = request.args.get('keyword')

        data = {}
        result = []

        current_user = User.find_by_id(int(request.args.get('user_id')))

        from datetime import datetime, timedelta

        try:
            data['start_date'] = datetime.strptime(request.args.get('start_date'), '%d.%m.%Y')
        except:
            pass

        try:
            data['end_date'] = datetime.strptime(request.args.get('end_date'), '%d.%m.%Y') + timedelta(days=1)
        except:
            pass
        
        try:
            data['modules'] = set(request.args.get('modules').split(','))
        except:
            pass

        def to_json(x):
            from app import db
            return {
                'id': x.id,
                'topic': x.topic,
                'description': x.description,
                'creation': x.creationDate.strftime('%d.%m.%Y'),
                'views': x.views,
                'likes': len(db.session.query(likes).filter(likes.c.research_id == x.id).all())
            }

        if keyword is None or len(keyword) < 3:
            result = Research.query.all()
        else:
            if request.args.get('sort_way') is None or request.args.get('sort_way') == 'creation':
                result = Research.query.whooshee_search(
                    keyword).order_by(
                        desc(Research.creationDate)).all()[::-1]
            
            elif request.args.get('sort_way') == 'last_update':
                from app import db
                result = Research.query.whooshee_search(
                    keyword).all()
                result = sorted(
                    result,
                    key=lambda x: db.session.query(
                            ConductedResearch.date
                        ).filter(
                            ConductedResearch.researchId == x.id
                        ).order_by(
                            desc(ConductedResearch.date)
                        ).first(),
                    reverse=True
                )

            elif request.args.get('sort_way') == 'views':
                result = Research.query.whooshee_search(
                    keyword).order_by(
                        Research.views.desc()).all()
                result = sorted(
                    result, 
                    key=lambda x: x.views, 
                    reverse=True
                )
            
            elif request.args.get('sort_way') == 'popularity':
                from app import db
                result = Research.query.whooshee_search(
                    keyword).all()
                result = sorted (
                    result, 
                    key=lambda x: len(db.session.query(likes).filter(likes.c.research_id == x.id).all()), 
                    reverse=True
                )

            elif request.args.get('sort_way') == 'subscribers':
                from app import db
                result = Research.query.whooshee_search(
                    keyword).all()
                result = sorted (
                    result, 
                    key=lambda x: len(db.session.query(subscriptions).filter(subscriptions.c.research_id == x.id).all()), 
                    reverse=True
                )

        from app import db
        my_res_ids = db.session.query(UserResearchPermission.researchId).filter(
            UserResearchPermission.userId == current_user.id
        ).all()
        result = [x for x in result if x.id in [i[0] for i in my_res_ids]]

        if data.get('end_date') is not None:
            result = [x for x in result if x.creationDate <= data.get('end_date')]

        if data.get('start_date') is not None:
            result = [x for x in result if x.creationDate >= data.get('start_date')]
        
        if data.get('modules') is not None:
            def get_modules(x):
                return [res.module for res in ResearchModule.query.filter_by(researchId=x.id).all()]
            
            result = [x for x in result if data.get('modules').issubset(get_modules(x))]

        if request.args.get('analyser') is not None:
            result = [x for x in result if x.algos == request.args.get('analyser')]

        return get_paginated_list(
            list(map(lambda x: to_json(x), result)), 
            '/user/researches', 
            start=request.args.get('start', 1), 
            limit=request.args.get('limit', 20)
        )


class SearchResearches(Resource):
    def get(self):
        from flask import request
        from sqlalchemy import desc
        keyword = request.args.get('keyword')

        data = {}
        result = []
        
        from datetime import datetime, timedelta

        try:
            data['start_date'] = datetime.strptime(request.args.get('start_date'), '%d.%m.%Y')
        except:
            pass

        try:
            data['end_date'] = datetime.strptime(request.args.get('end_date'), '%d.%m.%Y') + timedelta(days=1)
        except:
            pass
        
        try:
            data['modules'] = set(request.args.get('modules').split(','))
        except:
            pass

        def to_json(x):
            from app import db
            return {
                'id': x.id,
                'topic': x.topic,
                'description': x.description,
                'creation': x.creationDate.strftime('%d.%m.%Y'),
                'views': x.views,
                'likes': len(db.session.query(likes).filter(likes.c.research_id == x.id).all()),
                'subscriptions': len(db.session.query(subscriptions).filter(subscriptions.c.research_id == x.id).all())
            }

        if keyword is None or keyword == '' or len(keyword) <= 3:
            result = Research.query.all()[::-1]

        elif request.args.get('sort_way') is None or request.args.get('sort_way') == 'creation':
            result = Research.query.whooshee_search(
                keyword).filter(Research.type_of_research == True).order_by(
                    desc(Research.creationDate)).all()[::-1]
        
        elif request.args.get('sort_way') == 'last_update':
            from app import db
            result = Research.query.whooshee_search(
                keyword).filter(Research.type_of_research == True).all()
            result = sorted(
                result,
                key=lambda x: db.session.query(
                        ConductedResearch.date
                    ).filter(
                        ConductedResearch.researchId == x.id
                    ).order_by(
                        desc(ConductedResearch.date)
                    ).first(),
                reverse=True
            )

        elif request.args.get('sort_way') == 'views':
            result = Research.query.whooshee_search(
                keyword).filter(Research.type_of_research == True).order_by(
                    Research.views.desc()).all()
            result = sorted(
                result, 
                key=lambda x: x.views, 
                reverse=True
            )
        
        elif request.args.get('sort_way') == 'popularity':
            from app import db
            result = Research.query.whooshee_search(
                keyword).filter(Research.type_of_research == True).all()
            result = sorted (
                result, 
                key=lambda x: len(db.session.query(likes).filter(likes.c.research_id == x.id).all()), 
                reverse=True
            )

        elif request.args.get('sort_way') == 'subscribers':
            from app import db
            result = Research.query.whooshee_search(
                keyword).filter(Research.type_of_research == True).all()
            result = sorted (
                result, 
                key=lambda x: len(db.session.query(subscriptions).filter(subscriptions.c.research_id == x.id).all()), 
                reverse=True
            )

        if data.get('end_date') is not None:
            result = [x for x in result if x.creationDate <= data.get('end_date')]

        if data.get('start_date') is not None:
            result = [x for x in result if x.creationDate >= data.get('start_date')]
        
        if data.get('modules') is not None:
            def get_modules(x):
                return [res.module for res in ResearchModule.query.filter_by(researchId=x.id).all()]
            
            result = [x for x in result if data.get('modules').issubset(get_modules(x))]

        if request.args.get('analyser') is not None:
            result = [x for x in result if x.algos == request.args.get('analyser')]

        if request.args.get('isCompany') is not None and int(request.args.get('isCompany')) == 1:
            result = [x for x in result if User.query.filter_by(id=x.ownerId).first().isCompany is True]
        
        elif request.args.get('isCompany') is not None and int(request.args.get('isCompany')) == 0:
            result = [x for x in result if User.query.filter_by(id=x.ownerId).first().isCompany is False]

        return get_paginated_list(
            list(map(lambda x: to_json(x), result)), 
            '/research/search', 
            start=request.args.get('start', 1), 
            limit=request.args.get('limit', 20)
        )


class ResearchSubscription(Resource):
    @jwt_required
    def post(self):
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        data = subscriptions_likes_parser.parse_args()
        res_id = data.get('research_id')
        res = Research.find_by_id(res_id)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 400
        
        if res is None:
            return {
                'response': False,
                'message': 'Research {} does not exist'.format(res.topic)
            }, 400
        
        if current_user.subscribe(res):
            from app import db
            db.session.commit()

        return {
            'response': True,
            'message': '{} is subscribed to {} from now.'.format(current_username, res.topic)
        }
    
    @jwt_required
    def delete(self):
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        data = subscriptions_likes_parser.parse_args()
        res_id = data.get('research_id')
        res = Research.find_by_id(res_id)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 400
        
        if res is None:
            return {
                'response': False,
                'message': 'Research {} does not exist'.format(res.topic)
            }, 400
        
        if current_user.unsubscribe(res):
            from app import db
            db.session.commit()

        return {
            'response': True,
            'message': '{} is not subscribed to {} from now.'.format(current_username, res.topic)
        }
    
    @jwt_required
    def get(self):
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 400
        
        return current_user.return_subscribed()


class ResearchLike(Resource):
    @jwt_required
    def post(self):
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        data = subscriptions_likes_parser.parse_args()
        res_id = data.get('research_id')
        res = Research.find_by_id(res_id)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 400
        
        if res is None:
            return {
                'response': False,
                'message': 'Research {} does not exist'.format(res.topic)
            }, 400
        
        if current_user.like(res):
            from app import db
            db.session.commit()

        return {
            'response': True,
            'message': '{} liked {}'.format(current_username, res.topic)
        }
    
    @jwt_required
    def delete(self):
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        data = subscriptions_likes_parser.parse_args()
        res_id = data.get('research_id')
        res = Research.find_by_id(res_id)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 400
        
        if res is None:
            return {
                'response': False,
                'message': 'Research {} does not exist'.format(res.topic)
            }, 400
        
        if current_user.unlike(res):
            from app import db
            db.session.commit()

        return {
            'response': True,
            'message': '{} removed like froom {}'.format(current_username, res.topic)
        }
    
    @jwt_required
    def get(self):
        current_username = get_jwt_identity()['username']
        current_user = User.find_by_username(current_username)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 400
        
        return current_user.return_liked()


class ResearchViews(Resource):
    def post(self):
        data = subscriptions_likes_parser.parse_args()
        res_id = data.get('research_id')
        res = Research.find_by_id(res_id)

        if res is None:
            return {
                'response': False,
                'message': 'Research {} does not exist'.format(res.topic)
            }, 400

        res.views += 1
        from app import db
        db.session.commit()

        return {
            'response': True,
            'message': 'Research {} got {} views'.format(res.topic, res.views),
            'views': res.views
        }
    
    def get(self):
        from flask import request
        res_id = request.args.get('research_id')
        res = Research.find_by_id(res_id)

        if res is None:
            return {
                'response': False,
                'message': 'Research {} does not exist'.format(res.topic)
            }, 400
        
        return {
            'response': True,
            'message': 'Research {} got {} views'.format(res.topic, res.views),
            'views': res.views
        }


class ResearchPlayStore(Resource):
    def get(self):
        from flask import request
        res = Research.find_by_id(int(request.args.get('research_id')))
        
        def to_json(x):
            return {
                "rate": x.rate,
                "text": x.text,
                "sentiment": x.sentimentScore
            }

        try:
            from app.models import PlayStoreResearch, PlayStoreReview
            pl_res = PlayStoreResearch.query.filter_by(id=res.id).first()
            pl_reviews = PlayStoreReview.query.filter_by(playStoreResearchId=res.id).all()

            return {
                "hist": {
                    "one": pl_res.rateOneCount,
                    "two": pl_res.rateTwoCount,
                    "three": pl_res.rateThreeCount,
                    "four": pl_res.rateFourCount,
                    "five": pl_res.rateFiveCount
                },
                "app_info": {
                    "name": pl_res.name,
                    "rate": pl_res.averageRating,
                    "downloads": pl_res.downloads,
                    "reviews": pl_res.maxReviews,
                    "not_clear_reviews": pl_res.maxReviews - int(0.25 - pl_res.maxReviews)
                },
                "top_reviews": list(map(lambda x: to_json(x), list(pl_reviews)))
            }

        except:
            return {
                "message": "internal server error"
            }, 500


class ResearchTwitter(Resource):
    def get(self):
        try:
            from flask import request
            import pandas as pd
            res = Research.find_by_id(request.args.get('research_id'))
            itter = res.conducted[-1].twitter[0]

            tweets = itter.tweets

            tweets_dates = [t.timestamp.strftime("%d.%m.%Y") for t in tweets]
            timeline = pd.to_datetime(pd.Series(tweets_dates), format='%d.%m.%Y')
            timeline.index = timeline.dt.to_period('m')
            timeline = timeline.groupby(level=0).size()
            timeline = dict(zip(timeline.index.format(), timeline))

            sentiment = {
                'positive_percent': (itter.pos_count / itter.tweetsCount) * 100,
                'negative_percent': (itter.neg_count / itter.tweetsCount) * 100,
                'neutral_percent': ((itter.tweetsCount - itter.pos_count - itter.neg_count) / itter.tweetsCount) * 100
            }

            import nltk
            nltk.download("stopwords")

            from nltk.corpus import stopwords
            from string import punctuation

            stop_words = set(stopwords.words('english')).union(set(stopwords.words("russian")))
            text = ' '.join([t.text.lower() for t in tweets])

            wordscount = {}

            for word in text.split():
                if word not in stop_words or word not in ['the', 'a', 'an', 'and']:
                    if word not in wordcount:
                        wordscount[word] = 1
                    else:
                        wordscount[word] += 1

            from collections import Counter

            word_counter = Counter(wordcount).most_common(10)

            freq_words = []

            for w in word_counter:
                freq_words.append(
                    {
                        w[0]: w[1]
                    }
                )

            return {
                'popularity_rate': timeline,
                'sentiment': sentiment,
                'frequent_words': freq_words,
                'tweets': [{'url': t.source, 'sentiment': t.sentimentScore} for t in tweets]
            }
        
        except:
            return {
                "message": "Internal server error or no research"
            }


class ResearchNews(Resource):
    def get(self):
        from flask import request
        res = Research.find_by_id(request.args.get('research_id'))
        itter = res.conducted[-1].news[0]

        articles = itter.articles

        sentiment = {
            'positive_percent': (itter.pos_count / itter.amount) * 100,
            'negative_percent': (itter.neg_count / itter.amount) * 100,
            'neutral_percent': ((itter.amount - itter.pos_count - itter.neg_count) / itter.amount) * 100
        }

        news_art = [{
                'source': a.source.split('||')[0],
                'source_url': a.source.split('||')[1],
                'title': a.title,
                'url': a.link
            } for a in articles]

        import nltk
        nltk.download("stopwords")

        from nltk.corpus import stopwords
        from string import punctuation

        stop_words = set(stopwords.words('english')).union(set(stopwords.words("russian")))
        text = ' '.join([t.text.lower() for t in articles])

        wordscount = {}

        for word in text.split():
            if word not in stop_words or word not in ['the', 'a', 'an', 'and']:
                if word not in wordcount:
                    wordscount[word] = 1
                else:
                    wordscount[word] += 1

        from collections import Counter

        word_counter = [w[0] for w in Counter(wordcount).most_common(10)]

        return {
            'news': news_art,
            'words': word_counter,
            'sentiment': sentiment
        }


class ResearchSearch(Resource):
    def get(self):
        from datetime import datetime, timedelta
        from flask import request
        search = Research.find_by_id(request.args.get('research_id')).search[0]
        start = request.args.get('start')
        end = request.args.get('end')

        try:
            result = {
                'popularity': [],
                'countries': [],
                'related': []
            }

            for d in search.days:
                result['popularity'].append(
                    {
                        'date': d.date.strftime('%d.%m.%Y'),
                        'rate': d.interest
                    }
                )
            
            if start is not None:
                start = datetime.strptime(start, '%d.%m.%Y')
                result['popularity'] = [x for x in result['popularity'] if x.creationDate >= start]

            if end is None:
                end = datetime.strptime(end, '%d.%m.%Y') + timedelta(days=1)
                result['popularity'] = [x for x in result['popularity'] if x.creationDate <= start]

            for c in search.countries:
                result['countries'].append(
                    {
                        'country': c.country,
                        'rate': c.interest
                    }
                )

            for r in search.related:
                result['related'].append(r.topic)
        except:
            result = {
                "message": "Internal error or no instances in database"
            }

        return result
