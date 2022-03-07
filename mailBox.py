import sys
import os
import re
from imap_tools import MailBox, AND
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
mailUser = os.getenv("MAILUSER")
mailPWD = os.getenv("MAILPWD")



def fetchemails():

    print("Connecting to the IMAP server...", end=" ", flush=True)
    try:
        imap = MailBox('imap.mail.me.com')
    except:
        print("Error")
        print(sys.exc_info()[0])
        sys.exit()
    else:
        print("Success !")

    print("Logging in...", end=" ", flush=True)
    try:
        imap.login(mailUser, mailPWD, initial_folder='Better Uptime Alerts')
    except:
        print("Error")
        print(sys.exc_info()[0])
        sys.exit()
    else:
        print("Success")

    print("Fetching unread emails...", end=" ", flush=True)
    unreadMails = []
    try:
        messages = imap.fetch(AND(seen=False))
    except:
        print(sys.exc_info()[0])
        sys.exit()
    else:
        print("Done")
        for msg in messages:
            unreadMails.append([msg.from_values.name, msg.html])

    print(f"Found {len(unreadMails)} unread email(s)")

    #  Disconnect from the IMAP server.
    print("Disconnecting from the server...", end=" ", flush=True)
    try:
        imap.logout()
    except:
        print("Error")
        print(sys.exc_info()[0])
        sys.exit()
    else:
        print("Success !")

    return unreadMails
