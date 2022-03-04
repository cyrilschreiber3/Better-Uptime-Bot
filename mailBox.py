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
imap.put_PeekMode(True)  # Prevents the mail from being set to seen.

def fetchemails():
    #  Connect to the iCloud IMAP Mail Server
    imap.put_Ssl(True)
    imap.put_Port(993)
    success = imap.Connect("imap.mail.me.com")
    if (success != True):
        print(imap.lastErrorText())
        sys.exit()

    #  The username is usually the name part of your iCloud email address
    #  (for example, emilyparker, not emilyparker@icloud.com).
    success = imap.Login(mailUser,mailPWD)
    if (success != True):
        print(imap.lastErrorText())
        sys.exit()

    #  Select an IMAP folder/mailbox
    success = imap.SelectMailbox("Better Uptime Alerts")
    if (success != True):
        print(imap.lastErrorText())
        sys.exit()

    #  Once the folder/mailbox is selected, the NumMessages property
    #  will contain the number of emails in the mailbox.
    #  Loop from 1 to NumMessages to fetch each email by sequence number.

    n = imap.get_NumMessages()
    unreadMails = []
    bUid = False
    for i in range(1, (n)-1):
        index = i
        flags = imap.fetchFlags(i, bUid)
        if (imap.get_LastMethodSuccess() != True):
            print(imap.lastErrorText())
            sys.exit()
        if flags != "\Seen":
            unreadMails.append(index)

    mailData = []
    for i in unreadMails:

        # Download the email by sequence number.
        # email is a CkEmail
        email = imap.FetchSingle(i, bUid)
        if (imap.get_LastMethodSuccess() != True):
            print(imap.lastErrorText())
            sys.exit()
        print(i)

        mailData.append([email.ck_from(), email.body()])
        # print(str(i) + ": " + email.ck_from())
        # print("    " + email.subject())
        # print("    " + email.body())
        # print("    " + str(seen))
        # print("-")

    #  Disconnect from the IMAP server.
    success = imap.Disconnect()

    print("Success.")
    return mailData