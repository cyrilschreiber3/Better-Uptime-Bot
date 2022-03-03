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


def mailParser(sender, content):
    status = None
    monitor = None
    checkedURL = None
    cause = None
    startTime = None
    endTime = None
    length = None
    incidentURL = None

# Status parser
    stat = sender.split()[2]
    status = stat[:-1]

    print(status)

# Content parser
    soup = BeautifulSoup(content, "html.parser")

    # link
    incident_buttons = soup.find_all("a", class_="es-button")
    orgLink = incident_buttons[0]['href']
    pattern = r"Fincidents%252F(.*?)%2"
    incidentID = re.search(pattern, orgLink).group(1)
    incidentURL = f"https://betteruptime.com/team/{teamID}/incidents/{incidentID}"
    print(incidentURL)

    # details
    incident_info_values = soup.find_all("span", class_="incident-info-value")
    monitor = incident_info_values[0].text
    checkedURL = incident_info_values[1].text
    cause = incident_info_values[2].text
    startTime = incident_info_values[3].text
    if status == "RESOLVED":
        endTime = incident_info_values[4].text[1:-1]
        length = incident_info_values[5].text

    print(f" ---------------- \n{monitor} \n ---------------- \n{checkedURL} \n ---------------- \n{cause} \n ---------------- \n{startTime} \n ---------------- \n{endTime} \n ---------------- \n{length}")

    # imap.SetFlag(i,bUid,"\Seen",1)


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

for i in reversed(unreadMails):

    # Download the email by sequence number.
    # email is a CkEmail
    email = imap.FetchSingle(i, bUid)
    if (imap.get_LastMethodSuccess() != True):
        print(imap.lastErrorText())
        sys.exit()
    print(i)
    mailParser(email.ck_from(), email.body())

    # print(str(i) + ": " + email.ck_from())
    # print("    " + email.subject())
    # print("    " + email.body())
    # print("    " + str(seen))
    # print("-")

#  Disconnect from the IMAP server.
success = imap.Disconnect()

print("Success.")
