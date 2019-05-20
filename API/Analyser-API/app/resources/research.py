from flask_restful import Resource
from app import db
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from app.models import (User, Research, ResearchKeyword, 
    ResearchModule, ConductedResearch, SearchTrends, Analyzer, 
    UserResearchPermission, likes, subscriptions)
from app.resources.request_parser import (research_filters, 
    create_research, subscriptions_likes_parser)


class MyResearch(Resource):
    @jwt_required
    def post(self):
        data = create_research.parse_args()
        
        current_username = get_jwt_identity()
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
                'likes': len(db.session.query(likes).filter(likes.c.research_id == x.id).all()),
                'subscriptions': len(db.session.query(subscriptions).filter(
                    subscriptions.c.research_id == research.id
                ).all())
            }
        
    def put(self):
        pass


class MyResearches(Resource):
    @jwt_required
    def get(self):
        from flask import request
        from sqlalchemy import desc
        keyword = request.args.get('keyword')

        current_username = get_jwt_identity()
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

        return {
            'response': True,
            'results': list(map(lambda x: to_json(x), result))
        }


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

        return {
            'response': True,
            'results': list(map(lambda x: to_json(x), result))
        }


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
                'likes': len(db.session.query(subscriptions).filter(subscriptions.c.research_id == x.id).all())
            }

        if request.args.get('sort_way') is None or request.args.get('sort_way') == 'creation':
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

        return {
            'response': True,
            'results': list(map(lambda x: to_json(x), result))
        }


class ResearchSubscription(Resource):
    @jwt_required
    def post(self):
        current_username = get_jwt_identity()
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
        current_username = get_jwt_identity()
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
        current_username = get_jwt_identity()
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
        current_username = get_jwt_identity()
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
        current_username = get_jwt_identity()
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
        current_username = get_jwt_identity()
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
        res = Research.find_by_id(request.args.get('research_id'))

        return {

        }
    
    def put(self):
        pass


class ResearchTwitter(Resource):
    def get(self):
        from flask import request
        res = Research.find_by_id(request.args.get('research_id'))

        return {

        }
    
    def put(self):
        pass


class ResearchNews(Resource):
    def get(self):
        from flask import request
        res = Research.find_by_id(request.args.get('research_id'))

        return {

        }
    
    def put(self):
        pass


class ResearchSearch(Resource):
    def get(self):
        from flask import request
        res = Research.find_by_id(request.args.get('research_id'))

        return {

        }
    
    def put(self):
        pass
