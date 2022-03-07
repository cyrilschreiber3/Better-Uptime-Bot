import os
import sys
import ssl
from imap_tools import MailBox, AND, OR, NOT
from dotenv import load_dotenv

load_dotenv()
mailUser = os.getenv("MAILUSER")
mailPWD = os.getenv("MAILPWD")

# get list of email subjects from INBOX folder - equivalent verbose version
ssl_context = ssl.create_default_context()
imap = MailBox('imap.mail.me.com')
print("w")
try:
    imap.login(mailUser, mailPWD, initial_folder='Better Uptime Alerts')
except:
    print("error")
    print(sys.exc_info()[0])
    sys.exit()
else:
    print("success")

print(type(imap.box))

try:
    messages = imap.fetch(AND(seen=False))
except:
    print(sys.exc_info()[0])
    sys.exit()
else:
    print("success")
    for msg in messages:
        print(msg.from_values)


imap.logout()

