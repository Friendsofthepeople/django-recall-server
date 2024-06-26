import os

apps = ["diaspora", "county", "pollingStation", "", "user"]

for app in apps:
    os.system(f"python manage.py startapp {app}")
