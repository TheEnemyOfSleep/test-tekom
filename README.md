# test-tekom

If you read this, then is not script anymore. This is bad optimized application.

Non optimised simple class-based app which allow send error message to email using smtp handler and telegram handler.

# Instalation

install requirements.txt:
- python-dotenv==0.15.0
- requests==2.25.1
- pyTelegramBotAPI==3.7.6

# Usage

Before are start script you need set some important things:
- set smtp and telegram variables like:
```env
# EMAIL variables
EMAIL_LOGIN="myemail@example.com"
SECRET_PASSWORD="foobar1234"
EMAIL_FROM_ADDRES="script@example.com"
EMAIL_TO_ADDRES="firstemail@example.com secondemail@example.com thirdemail@example.com"

# Telegram
TELEGRAM_TOKEN="mytoken"
TELEGRAM_CHANNEL_ID=-1234567891234
```
- use terminal and tags if you need define resourses:

where -f/--file - json file of resourses similar with argumet -d/--data

-i/--interval interval of repeating default value is 18000 sec = 5 hours
```bash
# Simple command with set interval and file of resourses
python main.py -f fixture.json -i 10

# Command with set interval and data with resourses
python main.py -d https://github.com/ https://www.jenkins.io/ https://gitlab.com/ http://www.google.com/nothere

# Command with default interval file with resourses and set directly argument for telegram on windows
python main.py -f fixture.json --telegram '{\\\"token\\\": \\\"mytoken\\\",\\\"channel_id\\\": -1234556789123}'

# Command with default interval file with resourses and set directly argument for telegram on linux
python main.py -f fixture.json --telegram '{"token": "mytoken","channel_id": -1234556789123}'
```
# Extensions

Add all requirements arguments for working with extension (telegram, smtp):
+ SMTP email arguments:
    * dotenv:
        + required:
            + MAIL_HOST
            + MAIL_PORT
            + EMAIL_LOGIN
            + SECRET_PASSWORD
            + EMAIL_FROM_ADDRES
            + EMAIL_TO_ADDRES
        + optional:
            + EMAIL_SUBJECT (default: 'Ошибка в скрипте, ресурс недоступен!')
    * json string:
        + required:
            + mailhost
            + email_login
            + email_password
            + fromaddr
            + toaddrs
        + optional:
            + subject (default: 'Ошибка в скрипте, ресурс недоступен!')
+ telegram arguments:
    * dotenv:
        + required:
            + TELEGRAM_TOKEN
            + TELEGRAM_CHANNEL_ID
    * json string:
        + required:
            + token
            + channel_id

or use cfg.json file for full configurating script:
```json
{
    "version": 1,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] - %(url)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard"            
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "script.log",
            "formatter": "standard"
        },
        "telegram": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "handlers.TelegramHandler",
            "token": "your telegram bot token",
            "channel_id": "telegram chat id"
        },
        "smtp": {
            "level": "ERROR",
            "formatter": "standard",
            "class": "handlers.TlsSMTPHandler",
            "mailhost": ["smtp.yandex.com", 465],
            "fromaddr": "bot@email",
            "toaddrs": "your@email",
            "credentials": ["smtp username", "smtp password"],
            "subject": "Some subject"
        }
    },
    "loggers": {
        "root": {
            "handlers": [
                "telegram",
                "smtp"
            ],
            "level": "DEBUG"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}
```
