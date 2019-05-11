from flask_restful import Resource
from app import db
from app.models import User, Research, ConductedResearch
from app.resources.request_parser import research_filters


class CreateResearch(Resource):
    def post(self):
        pass


class SearchResearches(Resource):
    def get(self):
        data = research_filters.parse_args()

        return {}
