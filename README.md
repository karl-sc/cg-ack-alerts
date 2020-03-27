# cg-ack-alerts
CloudGenix Alert Acknowledgment script
---------------------------------------

cg-ack-alerts.py

USAGE:
---------------------------------------
  -h, --help
        show this help message and exit
  
  --token "MYTOKEN", -t "MYTOKEN"
        specify an authtoken to use for CloudGenix authentication
  
  --authtokenfile "MYTOKENFILE.TXT", -f "MYTOKENFILE.TXT"
         a file containing the authtoken
         
  --limit NUMBER_OF_EVENTS, -l NUMBER_OF_EVENTS
        The max number of events to ack. Default 0 (UNLIMITED)
        
  --site-name site_name, -s site_name
                        (OPTIONAL) Specify a site to clear events for

Additional Info
---------------------------------------
This script will indiscriminately acknowledge all un-acknowledged alerts present on a users system.

Site Filtering
---------------------------------------
As an option an administrator may choose to only acknowledge select alerts relating to a specific
site. If this is the case an administrator may choose to leverage the optional parameter -s "sitename"
to only acknowledge events related to one site. Fuzzy matching will be used to pick the correct site.
    E.G.:   cg-ack-alerts.py -s "new york"
The above example could match the site named "New York Branch 1"
 
Max Limit
---------------------------------------
A maxmum number of alerts to acknowledge may be set using the LIMIT parameter. It is recommended that this
be set to a low number for testing purposes to ensure the correct tenant is set.

The script will confirm with you prior to acknowledging the alerts.=

Authentication:
---------------------------------------
    This script will attempt to authenticate with the CloudGenix controller
    software using an Auth Token or through interactive authentication.
    The authentication selection process happens in the following order:
        1) Auth Token defined via program arguments (--token or -t)
        2) File containing the auth token via program arguments (--authtokenfile or -f)
        3) Environment variable X_AUTH_TOKEN
        4) Environment variable AUTH_TOKEN
        5) Interactive Authentication via terminal

Acknowledgement Limit:
---------------------------------------
    With the command line argument --limit or -l a user may defing the max number of alerts to ack.
    This will set the maximum number of unacknowledged events to acknowledge. The script will
    only acknowledge alerts in blocks of 100 per API request. The script will continue to 
    iterate until it has attempted to acknowledge the user defined maximum. By default
    there is no limit to how many alerts will be acknowledged and this script will loop
    until all alerts have been acknowledged.

