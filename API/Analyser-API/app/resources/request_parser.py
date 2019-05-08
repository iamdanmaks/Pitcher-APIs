from flask_restful import reqparse

reg_parser = reqparse.RequestParser()
reg_parser.add_argument('password', type=str, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('email', type=str, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('userType', type=int, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('username', type=str, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('fullname', type=str)
reg_parser.add_argument('company_name', type=str)

login_parser = reqparse.RequestParser()
login_parser.add_argument('user', type=str, help = 'This field cannot be blank', required = True)
login_parser.add_argument('user_password', type=str, help = 'This field cannot be blank', required = True)

update_user_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str)
login_parser.add_argument('fullname', type=str)
login_parser.add_argument('bio', type=str)

followers_parser = reqparse.RequestParser()
followers_parser.add_argument('username', help='This field cannot be blank', required=True)
