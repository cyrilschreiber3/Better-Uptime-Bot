import sys
import os
import re
import chilkat
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
teamID = os.getenv("BETTERUPTIME_TEAMID")
mailUser = os.getenv("MAILUSER")
mailPWD = os.getenv("MAILPWD")

imap = chilkat.CkImap()
# imap.put_PeekMode(True)  # Prevents the mail from being set to seen.


def fetchemails():
    #  Connect to the iCloud IMAP Mail Server
    print("Connecting to the IMAP server...", end=" ", flush=True)
    imap.put_Ssl(True)
    imap.put_Port(993)
    success = imap.Connect("imap.mail.me.com")
    if (success != True):
        print("")
        print(imap.lastErrorText())
        sys.exit()
    else:
        print("Success !")

    #  The username is usually the name part of your iCloud email address
    #  (for example, emilyparker, not emilyparker@icloud.com).
    print("Logging in...", end=" ", flush=True)
    success = imap.Login(mailUser, mailPWD)
    if (success != True):
        print("")
        print(imap.lastErrorText())
        sys.exit()
    else:
        print("Success !")

    #  Select an IMAP folder/mailbox
    print("Selecting alerts folder...", end=" ", flush=True)
    success = imap.SelectMailbox("Better Uptime Alerts")
    if (success != True):
        print("")
        print(imap.lastErrorText())
        sys.exit()
    else:
        print("Success !")

    #  Once the folder/mailbox is selected, the NumMessages property
    #  will contain the number of emails in the mailbox.
    #  Loop from 1 to NumMessages to fetch each email by sequence number.

    print("Fetching undread email IDs...", end=" ", flush=True)
    n = imap.get_NumMessages()
    unreadMails = []
    bUid = False
    for i in range(1, (n)-1):
        index = i
        flags = imap.fetchFlags(i, bUid)
        if (imap.get_LastMethodSuccess() != True):
            print("")
            print(imap.lastErrorText())
            sys.exit()
        if flags != "\Seen":
            unreadMails.append(index)
    print("Done")
    print(f"Found {len(unreadMails)} unread email(s)")

    print("Fetching undread emails data...", end=" ", flush=True)
    mailData = []
    for i in unreadMails:

        # Download the email by sequence number.
        # email is a CkEmail
        email = imap.FetchSingle(i, bUid)
        if (imap.get_LastMethodSuccess() != True):
            print("")
            print(imap.lastErrorText())
            sys.exit()

        mailData.append([email.ck_from(), email.body()])
    print("Done")

    #  Disconnect from the IMAP server.
    print("Disconnecting from the server...", end=" ", flush=True)
    success = imap.Disconnect()
    if (success != True):
        print("")
        print(imap.lastErrorText())
        sys.exit()
    else:
        print("Success !")

    return mailData
