# Farm_Bot

* Inventory system that keeps track of current parts, equipment, supplier, and locations.
* Emails users if inventory gets low.
* Built in protection from bot spamming/brute forcing.
* Ability to store Images of parts.


# Deployment

* Install all requirements of program in requirements.txt.
* You will need to configure system with your database url, a bot email, and a secure account creation code.


# Notes

* Currently the system does not do data analysis on breakdowns. As the system gets used more by my client and incurs failures I will be coming back to this to implement logistic regression to predict breakdowns.
* Currently the system will ban IP addresses that generate more than 20 failed attempts per mintue. They will be banned for 10 mintues. If an IP generates more than 500 failed attempts in a week they are permanently banned.
* System will optimize database weekly in order to improve call responsiveness.
* System is implemented to take advantage of a local memcache instance. It will still run without an instance present.
