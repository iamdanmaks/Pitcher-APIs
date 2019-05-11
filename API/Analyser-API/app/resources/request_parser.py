from flask_restful import reqparse


reg_parser = reqparse.RequestParser()
reg_parser.add_argument('username', type=str, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('password', type=str, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('email', type=str, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('isCompany', type=bool, help = 'This field cannot be blank', required = True)
reg_parser.add_argument('fullname', type=str, help = 'This field cannot be blank', required = True)


login_parser = reqparse.RequestParser()
login_parser.add_argument('user', type=str, help = 'This field cannot be blank', required = True)
login_parser.add_argument('user_password', type=str, help = 'This field cannot be blank', required = True)


update_user_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str)
login_parser.add_argument('fullname', type=str)
login_parser.add_argument('bio', type=str)


followers_parser = reqparse.RequestParser()
followers_parser.add_argument('worker_id', type=int, help='This field cannot be blank', required=True)


research_filters = reqparse.RequestParser()
research_filters.add_argument('sort_way', type=list)


create_research = reqparse.RequestParser()
create_research.add_argument('topic', type=str, required=True, help='This field cannot be blank')
create_research.add_argument('description', type=str)
create_research.add_argument('keywords', type=str, required=True, help='This field cannot be blank')
create_research.add_argument('modules', type=str, required=True, help='This field cannot be blank')
create_research.add_argument('update_interval', type=str, required=True, help='This field cannot be blank')
create_research.add_argument('app_id', type=str)
create_research.add_argument('app_name', type=str)
create_research.add_argument('app_dev', type=str)
create_research.add_argument('type', type=bool, required=True, help='This field cannot be blank')
