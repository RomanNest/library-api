# LIBRARY SERVICE API 

## About project
This is the Library Service project API platform for managing the library. It allows users to borrow and return books, makes online payments via Stripe, send Telegram notification via library bot about each borrowing and payment. 

## Technologies that implemented in this project:
1. **Django REST Framework** - for managing API views;
2. **PostgreSQL** - as the main database;
3. **Stripe**: for payment transactions;
4. **Telegram bot** for informing about each borrowing and payment through a Telegram chat;
5. **Celery**: for checking if a payment session has expired and for monitoring overdue borrowings;
6. **Redis**: as the Celery broker;
7. **Docker Compose** - for developing the microservices;
8. **Swagger & Redoc** - for API documentation.

## The main features:
* JWT authentication;
* Admin panel /admin/;
* CRUD functionality for books(for library staff);
* Create and return borrowings;
* Check borrowings for overdue;
* Filter for all instances;
* Automatically update inventory while creating or returning borrowings;
* Telegram notifications about creating or returning borrowings;
* Fine system for overdue borrowings.

## How to run:
### Using Docker

- Clone the repository: https://github.com/RomanNest/library-api.git
- Navigate to the project directory: 
```bash
cd social_media_api
```
- Copy .env.sample to .env and fill all required data
- Build and run Docker container:
``` bash
docker-compose up --build
```
- Create admin user (optional):
``` bash
docker-compose exec -ti social_media python manage.py createsuperuser
```
- Access the API endpoints via: http://localhost:8001

### Using GitHub

- - Clone the repository: https://github.com/RomanNest/library-api.git
- Navigate to the project directory: 
```bash
cd social_media_api
```
- Install the Python dependencies:
```bash
pip instal -r requirements.txt
```
- Apply database migrations:
```bash
python manage.py migrate
```
- Run the development server:
```bash
python manage.py runserver
```
- Access the API endpoints via: http://localhost:8000

### Get Telegram notification
- Create bot using BotFather and get token as TELEGRAM_BOT_TOKEN;
- Create a chat in Telegram to send notifications there and add a bot to this chat;
- Using https://t.me/getmyid_bot find out the chat_id as TELEGRAM_CHAT_ID.

## Contribution
I welcome contributions to improve the Library API Service. Feel free to submit bug reports, feature requests, or pull requests to rom.puh@gmail.com
