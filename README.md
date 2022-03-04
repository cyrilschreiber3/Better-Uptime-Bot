# Better Uptime Bot

[Better Uptime](https://betteruptime.com/) is a monitoring service for websites, cronjobs, etc.
It works great, but with the free version I can only receive notifications via emails which is anoying. Since I'm in the process of learning Python, I thought I might as well code something useful.

So here is the plan:
I connected the program to my email account, and when it receives a new mail from Better Uptime, it downloads that email, filters all the informarmations and store it in a database. Then a discord bot notifies me of the alert in a channel in my personnal server.

## 04/03/2022 - The bot works !

I connected all the different modules that I developed separately up until now and everything works !
Unfortunately, I couldn't use my first idea where I edit the original alert message into a resolution message, as I wouldn't be able to get notified again. So to work around that, the bot replies to the alert message with a separate resolution message and links it in the alert message (and changes the alert message color to orange).
As this is going to significantly add clutter in the discord channel, so I'm thinking of adding a function that checks for old, resolved alert messages, and delete them.

But first I want to implement a status feature. So when an incident is ongoing, the status of the bot changes to red (do not disturb) and a text under his name shows "Ongoing incident" or something like that.