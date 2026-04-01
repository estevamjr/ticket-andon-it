from flask import request
from flask_restful import Resource, Api
from app.models.user import User
from app.extensions import db
from app.utils.httpResponses import success_200, success_201, error_400, error_401, error_409, error_500
from app.services.log import LogService 
from sqlalchemy.exc import OperationalError
from flask_jwt_extended import create_access_token
from app.schemas.ticket import UserSchema

def initializeAuthRoutes(api: Api):
    api.add_resource(UserRegister, '/api/auth/register')
    api.add_resource(UserLogin, '/api/auth/login')

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            LogService.create_log(
                "USER_REGISTER_ERROR", 
                "Missing username or password", 
                user_id=None
            )
            return error_400('Missing username or password')

        username = data['username']
        password = data['password']

        try:
            if User.query.filter_by(username=username).first():
                LogService.create_log(
                    "USER_REGISTER_ERROR", 
                    f"User {username} already exists", 
                    user_id=None
                )
                return error_409(f'User {username} already exists')

            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            db.session.refresh(new_user) 
            
            user_schema = UserSchema()
            user_data = user_schema.dump(new_user)

            LogService.create_log(
                "USER_REGISTER_SUCCESS", 
                f"User {username} created successfully", 
                user_id=new_user.id
            )
            return success_201(user_data)

        except OperationalError as e:
            db.session.rollback()
            LogService.create_log(
                "USER_REGISTER_ERROR", 
                f"Database schema error: {e}", 
                user_id=None
            )
            return error_500('Database schema mismatch. Have you updated the User model?')
        except Exception as e:
            db.session.rollback()
            LogService.create_log(
                "USER_REGISTER_ERROR", 
                f"Error creating user {username}: {e}", 
                user_id=None
            )
            return error_500(f'An internal error occurred: {str(e)}')

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return error_400('Missing username or password')

        username = data['username']
        password = data['password']

        try:
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                access_token = create_access_token(identity=user.id)
                
                LogService.create_log(
                    "USER_LOGIN_SUCCESS", 
                    f"User '{username}' logged in.", user_id=user.id
                )
                
                return success_200({
                    'access_token': access_token,
                    'user': user.to_json() 
                })
            
            LogService.create_log(
                "USER_LOGIN_ERROR", 
                f"Invalid credentials for user '{username}'", 
                user_id=None
            )
            return error_401('Invalid credentials')

        except OperationalError as e:
            db.session.rollback()
            LogService.create_log(
                "USER_LOGIN_ERROR", f"Database schema error: {e}", 
                user_id=None
            )
            return error_500('Database schema mismatch. Have you updated the User model?')
        except Exception as e:
            LogService.create_log(
                "USER_LOGIN_ERROR", 
                f"Error during login for user {username}: {e}", 
                user_id=None
            )
            return error_500('An internal error occurred')