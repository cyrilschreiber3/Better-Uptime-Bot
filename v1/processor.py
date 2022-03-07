import os
import sqlite3
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
teamID = os.getenv("BETTERUPTIME_TEAMID")


def dumpInDatabase(data, state):
    print("Setting up the database...", end=" ", flush=True)
    db = sqlite3.connect("emails.db")  # Connect to database
    db.row_factory = sqlite3.Row  # Select row formating
    cursor = db.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts
                (id INTEGER, nature VARCHAR(20), monitor VARCHAR(45), checkedURL VARCHAR(45), cause VARCHAR(100), startDate VARCHAR(45), link VARCHAR(150), resolved_id INTEGER, message_id INTEGER, PRIMARY KEY (id AUTOINCREMENT), FOREIGN KEY ("resolved_id") REFERENCES resolutions(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS resolutions 
        (id INTEGER, monitor VARCHAR(45), checkedURL VARCHAR(45), cause VARCHAR(100), startDate VARCHAR(45), endDate VARCHAR(45), length VARCHAR(45), link VARCHAR(150), PRIMARY KEY (id))''')
    print("Done")

    def alertEvent(data):  # When event is an alert
        # Setup variables and SQL query
        incidentURL_col = data[0]
        monitor_col = data[1]
        checkedURL_col = data[2]
        cause_col = data[3]
        startTime_col = data[4]
        nature_col = data[8]
        query = f"INSERT INTO alerts (nature, monitor,checkedURL,cause,startDate,link) VALUES ('{nature_col}','{monitor_col}','{checkedURL_col}','{cause_col}','{startTime_col}','{incidentURL_col}');"

        print("Adding alert to database...", end=" ", flush=True)
        # Check if event is already in database
        cursor.execute("SELECT * FROM alerts")
        results = cursor.fetchall()
        exists = False
        for row in results:
            if incidentURL_col == row[6]:
                exists = True
                print("Aborted ! Alert already exists in database")

        if not exists:  # if not, add it to database
            cursor.execute(query)
            db.commit()
            print("Success !")
            print(f"\x1B[3m{str(cursor.rowcount)} row(s) affected\x1B[0m")

    def resolvedEvent(data):  # When event is a resolution
        # Setup variables and SQL insert query
        incidentURL_col = data[0]
        monitor_col = data[1]
        checkedURL_col = data[2]
        cause_col = data[3]
        startTime_col = data[4]
        endTime_col = data[5]
        length_col = data[6]
        insertQuery = f"INSERT INTO resolutions (monitor,checkedURL,cause,startDate,endDate,length,link) VALUES ('{monitor_col}','{checkedURL_col}','{cause_col}','{startTime_col}','{endTime_col}','{length_col}','{incidentURL_col}');"

        print("Adding alert to database...", end=" ", flush=True)
        # Check if event is already in database
        cursor.execute("SELECT * FROM resolutions")
        results_resolutions = cursor.fetchall()
        exists = False
        for row in results_resolutions:
            if incidentURL_col == row[7]:
                exists = True
                print("Aborted, alert already exists in database")

        if not exists:  # if not, add it to database
            cursor.execute(insertQuery)
            db.commit()
            print("Success !")
            print(f"\x1B[3m{str(cursor.rowcount)} row(s) affected\x1B[0m")

            print("Adding resolution event ID to alert event...", end=" ", flush=True)
            # Add resolution event id to alert event
            cursor.execute(f"SELECT * FROM resolutions WHERE link IS '{incidentURL_col}'")
            results_resolutions = cursor.fetchone()
            updateQuery = f"UPDATE alerts SET resolved_id = '{results_resolutions[0]}' WHERE link = '{incidentURL_col}'"
            cursor.execute(updateQuery)
            db.commit()
            print("Success !")
            print(f"\x1B[3m{str(cursor.rowcount)} row(s) affected\x1B[0m")

    if state == "ALERT":  # If event is an alert
        print("Event is an alert")
        alertEvent(data)
    elif state == "RESOLVED":  # else if event is a resolution
        print("Event is a resolution")
        resolvedEvent(data)


def mailParser(sender, content):
    print("Parsing data...", end=" ", flush=True)
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


# Content parser
    soup = BeautifulSoup(content, "html.parser")

    # link
    incident_buttons = soup.find_all("a", class_="es-button")
    orgLink = incident_buttons[0]['href']
    pattern = r"Fincidents%252F(.*?)%2"
    incidentID = re.search(pattern, orgLink).group(1)
    incidentURL = f"https://betteruptime.com/team/{teamID}/incidents/{incidentID}"

    # details
    incident_info_values = soup.find_all("span", class_="incident-info-value")
    incident_info_labels = soup.find_all("strong", class_="incident-info-key")

    monitor = incident_info_values[0].text
    cause = incident_info_values[1].text
    startTime = incident_info_values[2].text
    if status == "RESOLVED":
        endTime = incident_info_values[3].text[1:-1]
        length = incident_info_values[4].text
        if incident_info_labels[0].text == "Monitor:":
            endTime = incident_info_values[4].text[1:-1]
            length = incident_info_values[5].text

    if incident_info_labels[0].text == "Monitor:":
        checkedURL = incident_info_values[1].text
        cause = incident_info_values[2].text
        startTime = incident_info_values[3].text
        incident_nature = "monitor"
    elif incident_info_labels[0].text == "Heartbeat:":
        incident_nature = "heartbeat"

    betterEndTime = str(endTime).replace("\n", " ")

    data = [incidentURL, monitor, checkedURL,
            cause, startTime, betterEndTime, length, status, incident_nature]

    print("Done")
    return data
