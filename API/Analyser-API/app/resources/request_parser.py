from flask_restful import reqparse

reg_parser = reqparse.RequestParser()
reg_parser.add_argument('username', help = 'This field cannot be blank', required = True)
reg_parser.add_argument('password', help = 'This field cannot be blank', required = True)
reg_parser.add_argument('email', help = 'This field cannot be blank', required = True)
reg_parser.add_argument('isCompany', help = 'This field cannot be blank', required = True)
reg_parser.add_argument('fullname', help = 'This field cannot be blank', required = True)

login_parser = reqparse.RequestParser()
login_parser.add_argument('user', help = 'This field cannot be blank', required = True)
login_parser.add_argument('user_password', help = 'This field cannot be blank', required = True)
