import os
from imapclient import IMAPClient
from dotenv import load_dotenv
load_dotenv()
mailUser = os.getenv("MAILUSER")
mailPWD = os.getenv("MAILPWD")

# context manager ensures the session is cleaned up
with IMAPClient(host="imap.mail.me.com") as client:
    client.login(mailUser, mailPWD)
    client.select_folder('Better Uptime Alerts')

    # search criteria are passed in a straightforward way
    # (nesting is supported)
    messages = client.search(['NOT', 'DELETED'])

    # fetch selectors are passed as a simple list of strings.
    response = client.fetch(messages, ['FLAGS', 'RFC822.SIZE'])

    # `response` is keyed by message id and contains parsed,
    # converted response items.
    for message_id, data in response.items():
        print('{id}: {size} bytes, flags={flags}'.format(
            id=message_id,
            size=data[b'RFC822.SIZE'],
            flags=data[b'FLAGS']))