from .settings import *

# remove 'haystack' from INSTALLED_APPS
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "haystack"]
print("INSTALLED_APPS", INSTALLED_APPS)
