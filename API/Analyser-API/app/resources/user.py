from flask_restful import Resource
from flask_jwt_extended import (create_access_token, create_refresh_token, 
    jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from app.resources.request_parser import (reg_parser, login_parser, 
    followers_parser, update_user_parser)
from app.models import User, RevokedTokenModel

'''
    Осталось сделать:
        1. Добавить валидацию
        2. Запретить некоторые функции не админам
        3. Добавить подписки -> хз
        4. Добавить автоматизированую оплату -> хз
'''

class UserRegistration(Resource):
    def post(self):
        data = reg_parser.parse_args()
        
        if User.find_by_username(data['username']):
            return {
              'response': False,
              'message': 'User {} already exists'. format(data['username'])
            }
        
        new_user = User()

        new_user.set_password(data['password'])
        if int(data['userType']) == 0:
            fullname = data.get('fullname')
            
            if fullname is None:
                return {
                    'response': False, 
                    'message': 'Wrong credentials for ordinary user'
                }, 500
            
            else:
                new_user.fullname = fullname
            
            new_user.isCompany = False
        
        elif int(data['userType']) == 1:
            fullname = data.get('fullname')
            
            if fullname is None:
                return {
                    'response': False, 
                    'message': 'Wrong credentials for ordinary user'
                }, 500
            
            else:
                new_user.fullname = fullname
            
            try:
                comp = data.get('company_name')
                
                if comp is None:
                    return {
                        'response': False, 
                        'message': 'No company name for employed user'
                    }, 500
                
                company = User.query.filter_by(username=comp).first()

                if company is None or company.isCompany is False:
                    print(company)
                    return {
                        'response': False,
                        'message': '{} company does not exist'.format(comp)
                    }, 500
                
                new_user.isCompany = False
                company.follow(new_user)
            except:
                pass

        else:
            fullname = data.get('fullname')
            
            if fullname is not None:
                return {
                    'response': False, 
                    'message': 'Wrong credentials for company user'
                }, 500
            
            else:
                new_user.fullname = data.get('company_name')
            
            new_user.isCompany = True

        new_user.email = data['email']
        new_user.username = data['username']

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'response': True,
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        except:
            return {
                'response': False, 
                'message': 'Something went wrong'
            }, 500


class UserLogin(Resource):
    def post(self):
        data = login_parser.parse_args()
        current_user = User.find_by_email(data['user'])
        
        if not current_user:
            return {
                'response': False,
                'message': 'User {} doesn\'t exist'.format(data['username'])
            }
        
        if current_user.check_password(data['user_password']):
            access_token = create_access_token(identity = data['user'])
            refresh_token = create_refresh_token(identity = data['user'])
            return {
                'response': True,
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        
        else:
            return {
                'response': False,
                'message': 'Wrong credentials'
            }


class OAuthAuthorize(Resource):
    def get(self):
        from flask import request
        provider = request.args.get('provider')

        from app.oauth import OAuthSignIn
        oauth = OAuthSignIn.get_provider(provider)
        return oauth.authorize()


class OAuthFacebookCallback(Resource):
    def get(self):
        from flask import request
        provider = request.args.get('provider')
        
        from app.oauth import OAuthSignIn
        oauth = OAuthSignIn.get_provider(provider)
        social_id, email, fullname, username = oauth.callback()
        
        if social_id is None:
            return {
                'response': False,
                'message': 'Something is wrong with Facebook API.'
            }, 500
        
        user = User.query.filter_by(socialId=social_id).first()
        
        if not user:
            user = User(
                socialId=social_id, 
                username=username, 
                email=email,
                fullname=fullname
            )
            user.save_to_db()
        
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)

        return {
            'response': True,
            'message': 'Logged in as {}.'.format(user.username),
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class OAuthGoogleCallback(Resource):
    def get(self):
        from flask import request
        provider = request.args.get('provider')
        
        from app.oauth import OAuthSignIn
        from app import db

        oauth = OAuthSignIn.get_provider(provider)
        social_id, email, fullname = oauth.callback()
        username = fullname.split(' ')[0] + str(db.session.query(User).count())

        user = User.query.filter_by(socialId=social_id).first()

        if not user:
            user = User(
                socialId=social_id, 
                username=username, 
                email=email,
                fullname=fullname
            )
            user.save_to_db()
        
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)

        return {
            'response': True,
            'message': 'Logged in as {}.'.format(user.username),
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class UserChange(Resource):
    @jwt_required
    def put(self):
        current_username = get_jwt_identity()
        current_user = User.find_by_username(current_username)
        
        if current_user is not None:
            data = update_user_parser.parse_args()

            try:
                current_user.username = data['username']
            except KeyError:
                pass
            
            try:
                current_user.fullname = data['fullname']
            except KeyError:
                pass

            try:
                current_user.bio = data['bio']
            except KeyError:
                pass
        
            try:
                from flask import request
                from PIL import Image

                file = request.files['avatar']
                file.save('app/static/{}.jpg'.format(current_username))
                
                image = Image.open('app/static/{}.jpg'.foramt(current_username))
                image.save('app/static/{}.jpg'.foramt(current_username), 'JPEG', dpi=[300, 300], quality=40)

                current_user.avatar_ = 'app/static/{}.jpg'.foramt(current_username)
            except KeyError:
                pass

        else:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 500

        return {
            'response': True,
            'message': 'User {} was updated'.format(current_username)
        }
    
    @jwt_required
    def delete(self):
        current_username = get_jwt_identity()
        current_user = User.find_by_username(current_username)
        
        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 500

        current_user.del_from_db()

        return {
            'response': True,
            'message': 'User {} was deleted'.format(current_username)
        }


class Followers(Resource):
    @jwt_required
    def post(self):
        current_username = get_jwt_identity()
        current_user = User.find_by_username(current_username)

        data = followers_parser.parse_args()
        worker_name = data.get('worker_name')
        worker = User.find_by_username(worker_name)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 500
        
        if worker is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(worker_name)
            }, 500
        
        if current_user.isCompany is False:
            return {
                'response': False,
                'message': 'User {} is not a company'.format(current_username)
            }, 500
        
        if worker.isCompany:
            return {
                'response': False,
                'message': 'User {} has to be a person, but not a company.'.format(worker_name)
            }, 500
        
        if current_user.follow(worker):
            db.session.commit()

        return {
            'response': True,
            'message': '{} works for {} from this moment'.format(worker_name, current_username)
        }

    
    @jwt_required
    def delete(self):
        current_username = get_jwt_identity()
        current_user = User.find_by_username(current_username)

        data = followers_parser.parse_args()
        worker_name = data.get('worker_name')
        worker = User.find_by_username(worker_name)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 500
        
        if worker is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(worker_name)
            }, 500
        
        if current_user.isCompany is False:
            return {
                'response': False,
                'message': 'User {} is not a company'.format(current_username)
            }, 500
        
        if worker.isCompany:
            return {
                'response': False,
                'message': 'User {} has to be a person, but not a company.'.format(worker_name)
            }, 500
        
        if current_user.unfollow(worker):
            db.session.commit()

        return {
            'response': True,
            'message': '{} stopped working for {}'.format(worker_name, current_username)
        }
    
    @jwt_required
    def get(self):
        current_username = get_jwt_identity()
        current_user = User.find_by_username(current_username)

        if current_user is None:
            return {
                'response': False,
                'message': 'User {} does not exist'.format(current_username)
            }, 500
        
        return User.return_followed()

      
class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
      
      
class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
      
      
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
      
      
class AllUsers(Resource):
    def get(self):
        return User.return_all()
    
    def delete(self):
        return User.delete_all()
      
      
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }
