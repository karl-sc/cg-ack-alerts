# cg-ack-alerts
CloudGenix Alert Acknowledgment script
---------------------------------------

This script will indiscriminately acknowledge all un-acknowledged alerts present on a users system.

Authentication:
    This script will attempt to authenticate with the CloudGenix controller
    software using an Auth Token or through interactive authentication.
    The authentication selection process happens in the following order:
        1) Auth Token defined via program arguments (--token or -t)
        2) File containing the auth token via program arguments (--authtokenfile or -f)
        3) Environment variable X_AUTH_TOKEN
        4) Environment variable AUTH_TOKEN
        5) Interactive Authentication via terminal

Acknowledgement Limit:
    With the command line argument --limit or -l a user may defing the max number of alerts to ack.
    This will set the maximum number of unacknowledged events to acknowledge. The script will
    only acknowledge alerts in blocks of 100 per API request. The script will continue to 
    iterate until it has attempted to acknowledge the user defined maximum. By default
    there is no limit to how many alerts will be acknowledged and this script will loop
    until all alerts have been acknowledged.

