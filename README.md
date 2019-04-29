# Pitcher-APIs
Бэкенд Pitcher состоит из трёх серверов. Scraper-API отвечает за сбор информации с различных онлайн сервисов, таких как Play Store, Google Trends, Twitter, новостные порталы. ML-API проводит обработку естественного языка и даёт представление о мнении людей, основываясь на тексте.
 Ananlyser-API отвечает на запросы фрониенда и мобильного приложения.
 
 Analyser-API endpoints:
 1. http://localhost:5080/registration (метод POST)
    Принимает тело запроса селдующего формата: {
                                                 "username": "" (string), 
                                                 "password": "" (string), 
                                                 "isCompany": 0/1 (bool), 
                                                 "email": "" (string), 
                                                 "fullname": "" (string)
                                                }
