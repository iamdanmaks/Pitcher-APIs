from flask_restful import Resource
from app import db
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from app.models import (User, Research, ResearchKeyword, 
    ResearchModule, ConductedResearch, SearchTrends, Analyzer, 
    UserResearchPermission)
from app.resources.request_parser import research_filters, create_research


class CreateResearch(Resource):
    @jwt_required
    def post(self):
        data = create_research.parse_args()
        data['modules'] = data['modules'].split(' ')
        data['keywords'] = data['keywords'].split(' ')

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
            
            for module in data.get('modules'):
                new_module = ResearchModule(
                    module=module,
                    researchId=new_research.id
                )
                new_research.modules.append(new_module)
                db.session.add(new_module)
            
            new_research.updateInterval = data.get('update_interval')
            new_research.type_of_research = data.get('type')
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
            'message': 'Research {} was created'.format(new_research.topic)
        }


class SearchResearches(Resource):
    def get(self):
        data = research_filters.parse_args()

        return {}
