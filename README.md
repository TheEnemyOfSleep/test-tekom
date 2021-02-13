# test-tekom

Non optimised simple class-based script which allow send error message to email using smtp handler and telegram handler.

# Instalation

install requirements.txt:
- python-dotenv==0.15.0
- requests==2.25.1
- pyTelegramBotAPI==3.7.6

# Usage

Before are start script you need set some important things:
- set smtp and telegram variables like:
```env
EMAIL_LOGIN="myemail@example.com"
SECRET_PASSWORD="foobar1234"
EMAIL_FROM_ADDRES="script@example.com"
EMAIL_TO_ADDRES="firstemail@example.com secondemail@example.com thirdemail@example.com"

TELEGRAM_TOKEN="mytoken"
TELEGRAM_CHANNEL_ID=-1234567891234
```
- use terminal and tags if you need define resourses:

where -f, --file - json file of resourses similar with argumet -d --data

-i --interval interval of repeating default value is 18000 sec = 5 hours
```bash
python main.py -f fixture.json -i 10
or
python main.py -d https://github.com/ https://www.jenkins.io/ https://gitlab.com/ http://www.google.com/nothere
```
