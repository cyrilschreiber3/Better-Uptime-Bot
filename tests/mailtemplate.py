import sys
import os
import chilkat
from dotenv import load_dotenv

load_dotenv()
mailUser = os.getenv("MAILUSER")
mailPWD = os.getenv("MAILPWD")


#  This example assumes Chilkat Imap to have been previously unlocked.
#  See Unlock Imap for sample code.

imap = chilkat.CkImap()

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
bUid = False
for i in range(1,(n)-1):

    #  Download the email by sequence number.
    # email is a CkEmail
    email = imap.FetchSingle(i,bUid)
    if (imap.get_LastMethodSuccess() != True):
        print(imap.lastErrorText())
        sys.exit()

    print(str(i) + ": " + email.ck_from())
    print("    " + email.subject())
    print("-")

#  Disconnect from the IMAP server.
success = imap.Disconnect()

print("Success.")

#  Sample output:

#  	1: iCloud <noreply@email.apple.com>
#  	    Welcome to iCloud Mail.
#  	-
#  	2: "Chilkat Software" <support@chilkatsoft.com>
#  	    This is a test
#  	-
#  	Success.