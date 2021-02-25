import os
import logging
import logging.handlers
import telebot
import telegram_bot.sync_telegram_bot as sync_bot
from typing import Any, Union
from dotenv import load_dotenv

"""
Used decision from that url

http://mynthon.net/howto/-/python/python%20-%20logging.SMTPHandler-how-to-use-email-smtp-server.txt
"""

load_dotenv()

# Custom handlers
class TlsSMTPHandler(logging.handlers.SMTPHandler):

    def emit(self, record) -> bool:
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
    def __init__(self, token: str = None, channel_id: int = None) -> None:
        super().__init__()
        self.token = token
        self.channel_id = channel_id
    
    def check_constant(self, var_name: str, value: Any, const: Any) -> None:
        if value:
            setattr(self, var_name, value)
        elif const:
            setattr(self, var_name, const)

    def emit(self, record) -> None:
        try:
            msg = self.format(record)
            bot = telebot.TeleBot(self.token)
            bot.send_message(self.channel_id, msg, disable_web_page_preview=True)
        except:
            self.handleError(record)