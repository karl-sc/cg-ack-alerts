#!/usr/bin/env python
PROGRAM_NAME = "cg-ack-alerts.py"
PROGRAM_DESCRIPTION = """
CloudGenix Alert Acknowledgment script
---------------------------------------

This script will indiscriminately acknowledge all un-acknowledged alerts present on a users system.
    
Authentication:
    This script will attempt to authenticate with the CloudGenix controller
    software using an Auth Token or through interactive authentication.
    The authentication selection process happens in the following order:
        1) Auth Token defined via program arguments (--token or -t)
        2) File containing the auth token via program arguments (--authtokenfile or -f)
        3) Environment variable X_AUTH_TOKENgit add README.md
        4) Environment variable AUTH_TOKEN
        5) Interactive Authentication via terminal

Acknowledgement Limit:
    With the command line argument --limit or -l a user may defing the max number of alerts to ack.
    This will set the maximum number of unacknowledged events to acknowledge. The script will
    only acknowledge alerts in blocks of 100 per API request. The script will continue to 
    iterate until it has attempted to acknowledge the user defined maximum. By default
    there is no limit to how many alerts will be acknowledged and this script will loop
    until all alerts have been acknowledged.

"""
import cloudgenix
import os
import sys
import argparse
import cloudgenix_idname
from fuzzywuzzy import fuzz


CLIARGS = {}
cgx_session = cloudgenix.API()              #Instantiate a new CG API Session for AUTH

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=PROGRAM_DESCRIPTION
            )
    parser.add_argument('--token', '-t', metavar='"MYTOKEN"', type=str, 
                    help='specify an authtoken to use for CloudGenix authentication')
    parser.add_argument('--authtokenfile', '-f', metavar='"MYTOKENFILE.TXT"', type=str, 
                    help='a file containing the authtoken')
    parser.add_argument('--limit', '-l', metavar='NUMBER_OF_EVENTS', type=int, default=0,
                    help='The max number of events to ack. Default 0 (UNLIMITED)')
    args = parser.parse_args()
    CLIARGS.update(vars(args)) ##ASSIGN ARGUMENTS to our DICT
    

def authenticate():
    print("AUTHENTICATING...")
    user_email = None
    user_password = None
    
    ##First attempt to use an AuthTOKEN if defined
    if CLIARGS['token']:                    #Check if AuthToken is in the CLI ARG
        CLOUDGENIX_AUTH_TOKEN = CLIARGS['token']
        print("    ","Authenticating using Auth-Token in from CLI ARGS")
    elif CLIARGS['authtokenfile']:          #Next: Check if an AuthToken file is used
        tokenfile = open(CLIARGS['authtokenfile'])
        CLOUDGENIX_AUTH_TOKEN = tokenfile.read().strip()
        print("    ","Authenticating using Auth-token from file",CLIARGS['authtokenfile'])
    elif "X_AUTH_TOKEN" in os.environ:              #Next: Check if an AuthToken is defined in the OS as X_AUTH_TOKEN
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
        print("    ","Authenticating using environment variable X_AUTH_TOKEN")
    elif "AUTH_TOKEN" in os.environ:                #Next: Check if an AuthToken is defined in the OS as AUTH_TOKEN
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
        print("    ","Authenticating using environment variable AUTH_TOKEN")
    else:                                           #Next: If we are not using an AUTH TOKEN, set it to NULL        
        CLOUDGENIX_AUTH_TOKEN = None
        print("    ","Authenticating using interactive login")
    ##ATTEMPT AUTHENTICATION
    if CLOUDGENIX_AUTH_TOKEN:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("    ","ERROR: AUTH_TOKEN login failure, please check token.")
            sys.exit()
    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None            
    print("    ","SUCCESS: Authentication Complete")

def go():
    resp = cgx_session.get.tenants()
    if resp.cgx_status:
        tenant_name = resp.cgx_content.get("name", None)
    else:
        logout()
        print("ERROR: API Call failure when enumerating TENANT Name! Exiting!")
        sys.exit((vars(resp)))

    idname =  cloudgenix_idname.CloudGenixIDName(cgx_session)

    if CLIARGS['limit'] == 0:
        print("CONFIRMATION: This will acknowledge ALL events for",tenant_name)
    else:
        print("CONFIRMATION: This will acknowledge",CLIARGS['limit'],"events for",tenant_name)
    input_response = ""
    while(input_response != "yes") and (input_response != "no"):
        input_response = str(input("Please enter YES or NO: ")).lower()

    if(input_response == 'no'):
        logout()
        sys.exit("ERROR: Cancelling due to user response")
    
    limit = CLIARGS['limit']
    if limit == 0:
        limit = 999999  #Hidden Maximum is 100k entries
    ack_count = 0
    while (limit >= 100): #ONLY ACK 100 events at a time
        event_request_query = '{"limit":{"count":100,"sort_on":"time","sort_order":"descending"},"query":{"type":["alarm"]},"view":{"summary":false},"severity":[],"priority":[],"acknowledged":false,"suppressed":false}'
        resp = cgx_session.post.events_query(event_request_query)
        if resp.cgx_status:     
            event_list = resp.cgx_content.get("items", None) #EVENT_LIST contains an list of all returned events
            if (len(event_list) == 0):
                limit = 100
            for event in event_list:                            #Loop through each EVENT in the EVENT_LIST
                ack_count += 1
                acknowledged_event = event                      #Create a copy of the EVENT which is called ACKNOWLEDGED_EVENT
                acknowledged_event["acknowledged"] = "true"     #Set the copy of the event to have the ACKNOWLEDGED attribute set to TRUE!
                clrresp = cgx_session.put.events(event['id'],acknowledged_event)    #PUT the copy of the ACKNOWLEDGED_EVENT into the event queue to ACKNOWLEDGE the EVENT!
                print("    ",ack_count,": Cleared Event ID:", event['id'])         #PRINT some Debug information
        else:
            print("ERROR: API Error")
            logout()
            sys.exit(resp)
        limit = limit - 100

    event_request_query = '{"limit":{"count":'+ str(limit) +',"sort_on":"time","sort_order":"descending"},"query":{"type":["alarm"]},"view":{"summary":false},"severity":[],"priority":[],"acknowledged":false,"suppressed":false}'
    resp = cgx_session.post.events_query(event_request_query)
    if resp.cgx_status:
        event_list = resp.cgx_content.get("items", None)    #EVENT_LIST contains an list of all returned events
        for event in event_list:                            #Loop through each EVENT in the EVENT_LIST
            ack_count += 1
            acknowledged_event = event                      #Create a copy of the EVENT which is called ACKNOWLEDGED_EVENT
            acknowledged_event["acknowledged"] = "true"     #Set the copy of the event to have the ACKNOWLEDGED attribute set to TRUE!
            clrresp = cgx_session.put.events(event['id'],acknowledged_event)    #PUT the copy of the ACKNOWLEDGED_EVENT into the event queue to ACKNOWLEDGE the EVENT!
            print("    ",ack_count,": Cleared Event ID:", event['id'])         #PRINT some Debug information
            
    
    if (ack_count == 0):
        print("ERROR: No unacknowledged alerts were found")
    else:
        print("SUCCESS: Acknowledged",ack_count,"event ID's.")
    
def logout():
    print("Logging out")
    cgx_session.get.logout()

if __name__ == "__main__":
    parse_arguments()
    authenticate()
    go()
    logout()
