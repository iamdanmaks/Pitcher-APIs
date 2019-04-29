# Pitcher APIs
Бэкенд Pitcher состоит из трёх серверов. Scraper-API отвечает за сбор информации с различных онлайн сервисов, таких как Play Store, Google Trends, Twitter, новостные порталы. ML-API проводит обработку естественного языка и даёт представление о мнении людей, основываясь на тексте. Ananlyser-API отвечает на запросы фронтенда и мобильного приложения.

Analyser-API endpoints:

1. [http://localhost:5080/registration](http://localhost:5080/registration) (метод **POST**). 
    Принимает тело запроса следующего формата: 
    {
         "username": "" (string), 
         "password": "" (string), 
         "isCompany": 0/1 (bool), 
         "email": "" (string), 
         "fullname": "" (string) 
    }
    Возвращает, если всё правильно:
    {
        'response': True,
        'message': 'User <> was created',
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    Возвращает, если уже существует:
    {
        'response': False,
        'message': 'User <> already exists'
    }
    Если, ошибка на стороне сервера:
    {
        'response': False, 
         'message': 'Something went wrong'
    }
2. [http://localhost:5080/](http://localhost:5080/registration)login (метод **POST**). 
    Принимает тело запроса следующего формата: 
    {
         "user": "" (string), 
         "user_password": "" (string)
    }
    Возвращает, если всё правильно:
    {
        'response': True,
        'message': ‘Logged in as <>’,
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    Возвращает, если не существует:
    {

          'response': False,
          'message': 'User <> doesn\'t exist'

    }
    Если, ошибка на стороне сервера:
    {
        'response': False, 
         'message': 'Something went wrong'
    }
3. [http://localhost:5080](http://localhost:5080/registration)/logout/access (метод: **POST**)
    
1. [http://localhost:5080](http://localhost:5080/registration)/logout/refresh (метод: **POST**)
2. [http://localhost:5080](http://localhost:5080/registration)/token/refresh (метод: **POST**)
3. [http://localhost:5080](http://localhost:5080/registration)/users (метод: **GET**)
4. [http://localhost:5080](http://localhost:5080/registration)/users (метод: **DELETE**)

