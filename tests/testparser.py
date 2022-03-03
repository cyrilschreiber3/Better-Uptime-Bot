import os
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
mail = open(r"../mail-samples/mail-resolved-raw.html")
sender = '"Better Uptime RESOLVED" <alerts@alerts.betteruptime.com>'

load_dotenv()
teamID = os.getenv("BETTERUPTIME_TEAMID")

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

    incident_info_labels = soup.find_all("strong", class_="incident-info-key")
    
    if incident_info_labels[0].text == "Monitor:":
        incident_nature = "monitor"
    elif incident_info_labels[0].text == "Heartbeat:":
        incident_nature = "heartbeat"

    # print(f" ---------------- \n{monitor} \n ---------------- \n{checkedURL} \n ---------------- \n{cause} \n ---------------- \n{startTime} \n ---------------- \n{endTime} \n ---------------- \n{length}")

    # imap.SetFlag(i,bUid,"\Seen",1)

mailParser(sender, mail.read())