#!/usr/bin/python3
#
# Fetch customer events over a long time horizon; navigate paginated result set.
# 
# Usage: leverages Will Roever's Velocloud client from https://code.vmware.com/sd-wan samples
#

import os
import vco47 #replace with file to set VCO credentials as env variables 'VC_USERNAME' AND 'VC_PASSWORD'
from datetime import datetime, timedelta
from client import *

VCO_HOSTNAME = 'vcoXXX-XXXXX.velocloud.net' #Replace with actual VCO URL
INTERVAL_START = datetime.now() - timedelta(hours=24)

def datetime_to_epoch_ms(dtm):
    return int(dtm.timestamp()) * 1000

def main():

    client = VcoRequestManager(VCO_HOSTNAME)
    client.authenticate(os.environ['VC_USERNAME'], os.environ['VC_PASSWORD'], is_operator=os.environ.get('VC_OPERATOR', False))

    events = []

    result = client.call_api('event/getEnterpriseEvents', {
        'interval': {
            'start': datetime_to_epoch_ms(INTERVAL_START)},
        'filter': {
            'rules': [
                {    
                    'field': 'event',
                    'op': 'is',
                    'values': ["EDIT_PROFILE"]}]}
    })
    events += result['data']

    print('Found %d total configuration changes' % len(events))

    for event in events:
        #Print change events with errors and print time, user that made the change, and error message
        if 'system error' in event['detail']:
            print("""
Time: %s
Username: %s
VCO returned error: %s""" % (event['eventTime'], event['enterpriseUsername'], event['detail']))
        #Print new module additions
        elif 'new module' in event['message']:
            module = json.loads(event['detail'])
            modulenamestart = event['message'].find('module') + 7
            
            print("""
Time: %s
Username: %s
Scope: %s
Edge name: %s
User created new configuration module %s
Module config: %s""" % (event['eventTime'], event['enterpriseUsername'], event['message'], event['edgeName'], event['message'][modulenamestart:], json.dumps(module, sort_keys=True, indent=4)))
        
        #Print changes w/change time, user that made the change, affected profile or edge
        else:
            diffstart = event['detail'].find('"diff":') + 7
            diffend = event['detail'].find(',"change":')
            diffsection = json.loads(event['detail'][diffstart:diffend])

            print("""
Time: %s
Username: %s
Scope: %s
Edge name: %s
Changes:""" % (event['eventTime'], event['enterpriseUsername'], event['message'], event['edgeName']))
            print(json.dumps(diffsection, sort_keys=True, indent=4))

if __name__ == '__main__':
    main()