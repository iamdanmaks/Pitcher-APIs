from flask import Flask
from flask_restful import Api
from flask_whooshee import Whooshee
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_optimize import FlaskOptimize
from flask_login import LoginManager
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
flask_optimize = FlaskOptimize()
Compress(app)
app.config.from_object(Config)
login = LoginManager(app)
jwt = JWTManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
whooshee = Whooshee()
whooshee.init_app(app)


from app import routes, models
from app.resources import user, research


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(user.UserRegistration, '/registration')
api.add_resource(user.UserLogin, '/login')
api.add_resource(user.OAuthAuthorize, '/oauth/login')
api.add_resource(user.OAuthFacebookCallback, '/oauth/facebook/callback')
api.add_resource(user.OAuthGoogleCallback, '/oauth/google/callback')
api.add_resource(user.UserChange, '/update_or_delete_user')
api.add_resource(user.Followers, '/followers')
api.add_resource(user.UserLogoutAccess, '/logout/access')
api.add_resource(user.UserLogoutRefresh, '/logout/refresh')
api.add_resource(user.TokenRefresh, '/token/refresh')
api.add_resource(user.AllUsers, '/users')
api.add_resource(user.SecretResource, '/search/users')
api.add_resource(research.MyResearch, '/research/use')
api.add_resource(research.ResearchSubscription, '/research/subscribe')
api.add_resource(research.ResearchLike, '/research/like')
api.add_resource(research.SearchResearches, '/research/search')
api.add_resource(research.ResearchViews, '/research/views')
api.add_resource(research.MyResearches, '/research/my')
api.add_resource(research.UsersResearches, '/user/researches')
api.add_resource(research.ResearchSearch, '/research/search')
api.add_resource(research.ResearchPlayStore, '/research/play_store')
