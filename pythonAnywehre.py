import sys

# add your project directory to the sys.path
project_home = u'/home/hblazier/Zippys-on-Kam'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
# see https://plot.ly/dash/deployment
from Zippys_on_Kam import app
application = app.server