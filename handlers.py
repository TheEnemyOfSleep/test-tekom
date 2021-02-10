import os
import logging
import logging.handlers
import telebot
import telegram_bot.sync_telegram_bot as sync_bot
from typing import Any, Union
from dotenv import load_dotenv

"""
Used decision from that url

http://mynthon.net/howto/-/python/python%20-%20logging.SMTPHandler-how-to-use-gmail-smtp-server.txt
"""

load_dotenv()

# Define constants
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# Custom handlers
class TlsSMTPHandler(logging.handlers.SMTPHandler):

    def emit(self, record):
        """
        Emit a record.
 
        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            ",".join(self.toaddrs),
                            self.getSubject(record),
                            formatdate(), msg)
            if self.username:
                smtp.ehlo() # for tls add this line
                smtp.starttls() # for tls add this line
                smtp.ehlo() # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg.encode('utf-8').strip())
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class TelegramHandler(logging.Handler):
    """
    A handler class which allows send messages to
    telegram bot
    """
    def __init__(self, token: str = None, telegram_channel: int = None) -> None:
        super().__init__()
        if token:
            self.token = token
        else:
            self.token = TELEGRAM_CHANNEL_ID

        if telegram_channel:
            self.telegram_channel = telegram_channel
        else:
            self.telegram_channel = TELEGRAM_CHANNEL_ID
    
    def check_constant(self, var_name: str, value: Any, const: Any) -> None:
        if value:
            setattr(self, var_name, value)
        elif const:
            setattr(self, var_name, const)

    def emit(self, record) -> None:
        try:
            msg = self.format(record)
            bot = telebot.TeleBot(TELEGRAM_TOKEN)
            bot.send_message(self.telegram_channel, msg, disable_web_page_preview=True)
        except:
            self.handleError(record)