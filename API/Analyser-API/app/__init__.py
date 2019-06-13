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
import paypalrestsdk


app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object(Config)
login = LoginManager(app)
jwt = JWTManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
whooshee = Whooshee()
whooshee.init_app(app)

paypalrestsdk.configure({
  "mode": 'sandbox',
  "client_id": app.config['PAYPAL_CREDENTIALS']['id'],
  "client_secret": app.config['PAYPAL_CREDENTIALS']['secret'] 
  })


@app.before_first_request
def init_plans():
    from paypalrestsdk import BillingPlan

    pro_plan = BillingPlan({
        "name": "Pro subscription plan",
        "description": "Gives you private researches, ability to scrape Play store and many other features",
        "type": "INFINITE",
        "payment_definitions": [{
            "name": "Pro Plan",
            "type": "REGULAR",
            "frequency_interval": "1",
            "frequency": "MONTH",
            "amount": {
                "currency": "USD",
                "value": "1"
            }
        }],
        "merchant_preferences": {
            "auto_bill_amount": "yes",
            "cancel_url": "http://localhost:5080/payment/pro/cancel",
            "initial_fail_amount_action": "continue",
            "max_fail_attempts": "0",
            "return_url": "http://localhost:5080/payment/pro/execute",
            "setup_fee": {
                "currency": "USD",
                "value": "1"
            }
        }
    })

    if pro_plan.create():
        print("Billing Plan [%s] created successfully (pro)" % pro_plan.id)

        if pro_plan.activate():
            pro_plan = BillingPlan.find(pro_plan.id)
            print("Billing Plan [%s] state changed to %s (pro)" % (pro_plan.id, pro_plan.state))
            app.config['PRO'] = pro_plan.id
        
        else:
            print(pro_plan.error)
        
    else:
        print(pro_plan.error)

    premium_plan = BillingPlan({
        "name": "Premium subscription plan",
        "description": "Subscription which lets you work without any limitations",
        "type": "INFINITE",
        "payment_definitions": [{
            "name": "Pro Plan",
            "type": "REGULAR",
            "frequency_interval": "1",
            "frequency": "MONTH",
            "amount": {
                "currency": "USD",
                "value": "2"
            }
        }],
        "merchant_preferences": {
            "auto_bill_amount": "yes",
            "cancel_url": "http://localhost:5080/payment/premium/cancel",
            "initial_fail_amount_action": "continue",
            "max_fail_attempts": "0",
            "return_url": "http://localhost:5080/payment/premium/execute",
            "setup_fee": {
                "currency": "USD",
                "value": "1"
            }
        }
    })

    if premium_plan.create():
        print("Billing Plan [%s] created successfully (premium)" % premium_plan.id)

        if premium_plan.activate():
            premium_plan = BillingPlan.find(premium_plan.id)
            print("Billing Plan [%s] state changed to %s (premium)" % (premium_plan.id, premium_plan.state))
            app.config['PREMIUM'] = premium_plan.id
        
        else:
            print(premium_plan.error)
        
    else:
        print(premium_plan.error)


from app import routes, models
from app.resources import user, research


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(user.UserRegistration, '/registration')
api.add_resource(user.UserLogin, '/login')
api.add_resource(user.UserInfo, '/user/info')
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
api.add_resource(research.ResearchSearch, '/research/trends')
api.add_resource(research.ResearchPlayStore, '/research/play_store')
api.add_resource(research.ResearchTwitter, '/research/twitter')
api.add_resource(research.ResearchNews, '/research/news')
api.add_resource(user.InitPayment, '/subscribe')
api.add_resource(user.ExecuteProPayment, '/payment/pro/execute')
api.add_resource(user.ExecutePremiumPayment, '/payment/premium/execute')
api.add_resource(research.ResearchList, '/research/list')
api.add_resource(research.SignedInResearches, '/research/current')
