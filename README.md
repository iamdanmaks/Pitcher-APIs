# Pitcher APIs
Бэкенд Pitcher состоит из трёх серверов. Scraper-API отвечает за сбор информации с различных онлайн сервисов, таких как Play Store, Google Trends, Twitter, новостные порталы. ML-API проводит обработку естественного языка и даёт представление о мнении людей, основываясь на тексте. Ananlyser-API отвечает на запросы фронтенда и мобильного приложения.

Analyser-API endpoints:

1. [http://localhost:5080/registration](http://localhost:5080/registration) (метод **POST**). 
    Принимает тело запроса следующего формата: 
    ```json
    {
         "username": "", 
         "password": "", 
         "isCompany": true/false, 
         "email": "", 
         "fullname": "" 
    }
    ```

    Возвращает, если всё правильно:
    ```json
    {
        "response": true,
        "message": "User <> was created",
        "access_token": "",
        "refresh_token": ""
    }
    ```
    
    Возвращает, если уже существует:
    ```json
    {
        "response": false,
        "message": "User <> already exists"
    }
    ```

    Если, ошибка на стороне сервера:
    ```json
    {
        "response": false, 
        "message": "Something went wrong"
    }
    ```

2. [http://localhost:5080/](http://localhost:5080/registration)login (метод **POST**). 
    Принимает тело запроса следующего формата: 
    ```json
    {
         "user": "" (string), 
         "user_password": "" (string)
    }
    ```

    Возвращает, если всё правильно:
    ```json
    {
        "response": true,
        "message": "Logged in as <>",
        "access_token": "",
        "refresh_token": ""
    }
    ```

    Возвращает, если не существует:
    ```json
    {

          "response": false,
          "message": "User <> doesn\'t exist"

    }
    ```
    
    Если, ошибка на стороне сервера:
    ```json
    {
        "response": false, 
        "message": "Something went wrong"
    }
    ```
    
3. [http://localhost:5080](http://localhost:5080/registration)/logout/access (метод: **POST**)
    Нужно передать в хэдере запроса access token.
4. [http://localhost:5080](http://localhost:5080/registration)/logout/refresh (метод: **POST**)
    Нужно передать в хэдере запроса refresh token.
5. [http://localhost:5080](http://localhost:5080/registration)/token/refresh (метод: **POST**)
    Нужно передать в хэдере запроса refresh token.
6. [http://localhost:5080](http://localhost:5080/registration)/users (метод: **GET**)
    Возвращает краткую информацию по всем пользователям.
7. [http://localhost:5080](http://localhost:5080/registration)/users (метод: **DELETE**)
    Удаляет всех пользователей.

