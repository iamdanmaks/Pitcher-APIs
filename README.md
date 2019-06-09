# Pitcher APIs
Бэкенд Pitcher состоит из трёх серверов. Scraper-API отвечает за сбор информации с различных онлайн сервисов, таких как Play Store, Google Trends, Twitter, новостные порталы. ML-API проводит обработку естественного языка и даёт представление о мнении людей, основываясь на тексте. Ananlyser-API отвечает на запросы фронтенда и мобильного приложения.

Analyser-API endpoints:

1. http://localhost:5080/registration (метод **POST**). 
    Принимает тело запроса следующего формата: 
    ```json
    {
         "username": "", 
         "password": "", 
         "email": "", 
         "fullname": "".
         "isCompany": true/false
    }
    ```
    
    company_name не обязателен. userType указывает кем является пользователь:
    
    0) пользователь-любитель, который работает с сервисом не от компании
    
    1) пользователь, устроенный в компанию
    
    2) пользователь-компания

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

2. http://localhost:5080/login (метод **POST**). 
    Принимает тело запроса следующего формата: 
    ```json
    {
         "user": "", //email
         "user_password": ""
    }
    ```
    user - email пользователя.
    
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
          "message": "User <> doesn't exist"

    }
    ```
    
    Если, ошибка на стороне сервера:
    ```json
    {
        "response": false, 
        "message": "Something went wrong"
    }
    ```
    
3. http://localhost:5080/logout/access (метод: **POST**)
    
    Добавляет токен в чёрный список.
    
    Нужно передать в хэдере запроса access token.
    
    Возвращает, если токен существует и не в чёрном списке:
    ```json
    {
        "response": true, 
        "message": "Access token has been revoked"
    }
    ```
    
    Если, ошибка на стороне сервера:
    ```json
    {
        "response": false, 
        "message": "Something went wrong"
    }
    ```
    
4. http://localhost:5080/logout/refresh (метод: **POST**)
    
    Добавляет токен обновления в чёрный список.
    
    Нужно передать в хэдере запроса refresh token.
    
    Возвращает, если токен существует и не в чёрном списке:
    ```json
    {
        "response": true, 
        "message": "Refresh token has been revoked"
    }
    ```
    
    Если, ошибка на стороне сервера:
    ```json
    {
        "response": false, 
        "message": "Something went wrong"
    }
    ```
    
5. http://localhost:5080/token/refresh (метод: **POST**)
    
    Нужно передать в хэдере запроса refresh token.
    ```json
    {
        "access_token": ""
    }
    ```
6. http://localhost:5080/users (метод: **GET**)
    
    Возвращает краткую информацию по всем пользователям.
    
    Возвращает если всё в порядке:
    ```json
    {
        "users": [
            {
                "username": "",
                "fullname": "",
                "isCompany": ""
            },...
        ]
    }
    ```
    
7. http://localhost:5080/users (метод: **DELETE**)
    
    Удаляет всех пользователей.
    
    Возвращает если всё в порядке:
    ```json
        "response": true,
        "message": "<> row(s) deleted"
    ```
    
    Если, ошибка на стороне сервера:
    ```json
    {
        "response": false, 
        "message": "Something went wrong"
    }
    ```

8. http://localhost:5080/oauth/login (метод **GET**)

    Инициирует логин через сторонние сервисы.
    
    Нужно передать аргумент provider, который указывает через какой сервис залогинить.
    
    Если логин через Google: http://localhost:5080/oauth/login?provider=google
    
    Если логин через Facebook: http://localhost:5080/oauth/login?provider=facebook

9. http://localhost:5080/oauth/facebook/callback?provider=facebook (метод **GET**)

    Получает данные с Facebook об аккаунте, с которого залогинились.
    
    1) Отправляешь **GET** запрос по этому URL;
    2) Тебя редиректит на вход в Facebook;
    3) После входа в Facebook создаётся новый пользователь или находится существующий;
    4) Перенаправление на /oauth_redirect?access_token=<>&refresh_token=<> на фронтенде.
    
10. http://localhost:5080/oauth/google/callback?provider=google (метод **GET**)

    Получает данные с Google об аккаунте, с которого залогинились.
    
    1) Отправляешь **GET** запрос по этому URL;
    2) Тебя редиректит на вход в Google;
    3) После входа в Facebook создаётся новый пользователь или находится существующий;
    4) Перенаправление на /oauth_redirect?access_token=<>&refresh_token=<> на фронтенде.
   
11. http://localhost:5080/update_or_delete_user (метод **DELETE**)

    В хедере нужно передать токен доступа. Удаляет аккаунт пользователя.
    
12. http://localhost:5080/update_or_delete_user (метод **PUT**)

    Редактирует аккаунт. Нужен токен доступа. Принимает на вход:
    
    ```json
    {
        "username": "",
        "fullname": "",
        "bio": ""
    }
    ```
    
    Все поля не обязательны. Также можно передавать файл с аватаркой пользователя.

13. Создание исследования (метод **POST**)

    Для создания исследования передай на http://localhost:5080/research/use следующий json:
    ```json
    {
        "topic": "", //обязательно
        "description": "", //необязательно
        "keywords": ["","","",...],
        "modules": ["search", "play_store", "news", "twitter"], //передавать только комбинации из этих вариантов
        "update_interval": "",
        "app_id": "",
        "app_name": "",
        "app_dev": "",
        "isPublic": true/false,
        "analysers": "vader"/"polyglot"
    }
    ```
    Возвращает:
    
    ```json
    {
        "response": true,
        "id": int,
        "message": "Research <> was created"
    }
    ```

14. Получение инфы об исследовании (метод **GET**)

    http://localhost:5080/research/use?res_id={}
    
    ```json
    {
        "id": int,
        "topic": "",
        "description": "",
        "creation": "",
        "last_update": "",
        "views": int,
        "owner": {
            "id": int,
            "username": "",
            "fullname": ""
        },
        "keywords": [],
        "active_modules": [],
        "likes": int,
        "subscriptions": int
    }
    ```
15. Поиск исследований (метод **GET**)

    Получаешь по ссылке, где все параметры необязательны кроме **keyword**: http://localhost:5080/research/search?keyword={}&sorting=creation/last_update/views/popularity/subscribers&start_date={dd.mm.YYYY}&end_date={dd.mm.YYYY}&analyser=vader/polyglot&isCompany=0/1&modules=play_store/search/twitter/news
    
    Чтобы использовать пагинацию передавайте ещё параметры start, limit. Если не передашь, то start = 1, limit = 20.
    
    Возвращает:
    
    ```json
        {
            "response": true,
            "results": [
                {
                    "id": int,
                    "topic": "",
                    "description": "",
                    "creation": "dd.mm.YYYY",
                    "views": int,
                    "likes": int,
                    "subscriptions": int
                },...
            ],
            "next": "link to next part of a list",
            "previous": "link to previous part of a list",
            "start": 1,
            "limit": 1,
            "count": 1
        }
    ```

16. Лайки (поставить, получить пролайканые нынешним пользователем, удалить лайк) (методы: **POST**, **GET**, **DELETE**)

    Ссылка: http://localhost:5080/research/like
    
  Для delete и post передай json: ```json {"research_id": int} ```.
  
  Тоже самое для подписок, но url меняется на http://localhost:5080/research/subscribe

**Информация по модулям получается по следующей ссылке: http://localhost:5080/research/{name_of_module}?res_id={}**

17. Информация про твиттер в исследовании (метод **GET**) (**имя модуля: twitter**)

    Будет возвращаться информация про популярность, настроение и самые используемые слова:
    
    ```json
    {
        "popularity_rate": {
                "YYYY-mm": 1
            },
        "sentiment": {
            "positive_percent": 33,
            "neutral_percent": 33,
            "negative_percent": 34
        },
        "frequent_words": [
            {
                "word": "",
                "rate": 1
            }
        ],
        "tweets": [
            {
                "url": "",
                "sentiment": 1
            }
        ]
    }
    ```

18. Информация про новости в исследовании (метод: **GET**) (**имя модуля: news**)

    ```json
    {
        "news": [
            {
                "source": "",
                "link": "",
                "title": ""
            }
        ],
        "words": ["","",""],
        "sentiment": {
            "positive_percent": 33,
            "negative_percent": 33,
            "neutral_percent": 34
        }
    }
    ```

19. Информация про Play store (метод: **GET**) (**имя модуля: play_store**)

    ```json
    {
        "hist":{
            "one": 1,
            "two": 1,
            "three": 1,
            "four": 1,
            "five": 1
        },
        "app_info": {
            "name": "",
            "rate": 4.5,
            "downloads": "10000+",
            "reviews": 1500,
            "not_clear_reviews": 500
        },
        "top_reviews": [
            {
                "rate": 4,
                "text": "",
                "sentiment": 1
            }
        ]
    }
    ```

20. Информация про поисковые тренды: (метод: **GET**) (**имя модуля: search**)

    ```json
    {
        "popularity":[
            {
                "date": "dd.mm.YYYY",
                "rate": 1
            }
        ],
        "countries": [
            {
                "country": "",
                "rate": 1
            }
        ],
        "related":[
            "query1",
            "query2"
        ]
    }
    ```
