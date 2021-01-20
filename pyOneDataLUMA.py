#!/usr/bin/env python3

import requests
import json

__author__    = "Giuseppe La Rocca"
__email__     = "giuseppe.larocca@egi.eu"
__version__   = "$Revision: 0.0.3"
__date__      = "$Date: 31/05/2020 10:48:27"
__copyright__ = "Copyright (c) 2020 EGI Foundation"
__license__   = "Apache Licence v2.0"

username="admin"
password="egi4P@NOSC_wp&"
url="onezone-panosc.egi.eu"

def get_details(username, password, endpoint):
    ''' Method to do REST calls '''
    curl = requests.get(url=endpoint, auth=(username, password))
    data = curl.json()
    return(data)

def main():

    groups = []
    spaces = []
    users = []
    luma_mapping = []
    storageId = ""
    storageName = ""

    # Pre-requisites: 
    # In order to define mappings, it is necessary to know the following information:
    # 1.) Storage name or storage Id
    # 2.) Users Id
    # 3.) Groups Id 

    # A.) Get the list of available storage spaces
    print("\n[.] Listing of available Storage Spaces in OneData: ")
    endpoint = "https://%s/api/v3/onezone/user/spaces" %url
    spaces_data = get_details(username, password, endpoint)
    for index in range(0, len(spaces_data['spaces'])):
        spaceID = (spaces_data['spaces'][index])
        endpoint = "https://%s/api/v3/onezone/user/spaces/%s" %(url, spaceID)
        space_details = get_details(username, password, endpoint)
        print("-> StorageID = %s; Name = %s" %(spaceID, space_details['name']))

        if (space_details['name'] == "CESNET-space"):
           storageId=spaceID
           storageName=space_details['name']

        guid=int(1001+index)
        
        if (space_details['name'] != "PaNOSC-WP6"):     
           dictionary = {
              index+1: {
                  "groupDetails": [{
                     "storageId": spaceID,
                     "storageName": space_details['name'],
                     "gid": guid
                  }]
              }
           }

           spaces.append(dictionary)
    #print (json.dumps(spaces, indent=3, sort_keys=False))

    # B.) Get effective groups and proper details
    endpoint = "https://%s/api/v3/onezone/user/effective_groups" %url
    groups_data = get_details(username, password, endpoint)

    print("\n[.] List of available User Groups in OneData: ")
    for index in range(0, len(groups_data['groups'])):
        guid=int(1001+index)
        storage_dictionary = []

        groupID = (groups_data['groups'][index])
        endpoint = "https://%s/api/v3/onezone/user/groups/%s" %(url, groupID)
        group_details = get_details(username, password, endpoint)
        print("-> GroupID = %s; Name = %s" %(groupID, group_details['name']))
       
        storage_dictionary = {
               "storageId": "68eb4419ef3e5c6a9f4269d1ee1fbcb4ch3eee",
               "storageName": storageName,
               "storageId": storageId,
               "gid": guid
        }

        dictionary = {
           index+1: { 
             "idp": "onedata",
             "groupId": groupID,
             "groupDetails": storage_dictionary
           }
        }

        groups.append(dictionary)
        #print (json.dumps(groups, indent=3, sort_keys=False))


    # C.) Get list of users and proper details
    endpoint = "https://%s/api/v3/onezone/users" %url
    data = get_details(username, password, endpoint)

    print("\n[.] Listing available users in OneData: ")
    for index in range(0, len(data['users'])):
        # Parsing the providers JSON object
        userID = (data['users'][index])

        # Get user's details
        endpoint = "https://%s/api/v3/onezone/users/%s" %(url, userID)
        details = get_details(username, password, endpoint)
        #print(details)
   
        #print("\n-> UserID = %s  " %userID)
        #print("-> Username = %s  " %details['username'])
        #print("-> Name = %s  " %details['name'])
        #print("-> FullName = %s  " %details['fullName'])
        #print("-> Login = %s  " %details['login'])
        #print("-> Emails = %s     " %details['emails'])
        #print("-> EmailList = %s     " %details['emailList'])
        #print("-> basicAuthEnabled = %s     " %details['basicAuthEnabled'])
        #print("-> Alias = %s     " %details['alias'])
        size = len(details['linkedAccounts'])
        #print("-> IdP = %s       " %details['linkedAccounts'][0]['idp'])
        #print("-> SubjectID = %s " %details['linkedAccounts'][size-1]['subjectId'])
        
        uid=int(1001+index)
        guid=int(1001+index)
        
        #dictionary = {   
        #  index: {
        #    "userDetails": {
        #       "linkedAccount": [{ 
        #           "userID": details['linkedAccounts'][size-1]['subjectId'],
        #           "idp": details['linkedAccounts'][0]['idp']
        #         }],
        #         "credentials": [{
        #            "storageId": storageId,
        #            "storageName": storageName,
        #            "type": "posix",
        #            "uid": uid,
        #            "guid": guid
        #         }]
        #    }
        #  }
        #}

        #dictionary = {
        #  index+1: {
        #    "userDetails": {
        #       "username": details['username'],
        #       "id": details['linkedAccounts'][size-1]['subjectId'],
        #       "name": details['name'],
        #       "login": details['login'],
        #       #"linkedAccounts": details['linkedAccounts'],
        #       "linkedAccounts": '',
        #       "fullname": details['fullName'],
        #       "emails": details['emails'],
        #       "emailList": details['emailList'],
        #       "basicAuthEnabled": details['basicAuthEnabled'],
        #       "alias": details['alias']
        #    },
        #    "credentials": [{
        #       "storageId": storageId,
        #       "storageName": storageName,
        #       "type": "posix",
        #       "uid": uid,
        #       "guid": guid
        #    }]
        #  }
        #}

        dictionary = {
                "onedataUser": {
                    "mappingScheme": "idpUser",
                    "idp": "eduTEAMS",  #replace with IdP identifier as configured in auth.config (Onezone)
                    "subjectId":  details['linkedAccounts'][size-1]['subjectId'],
                },
                "storageUser": {
                    "storageCredentials": {
                        "uid": uid, #replace with actual user UID on storage
                        "type": "posix"
                     }
                }
        }

       
        users.append(dictionary)
    #print (json.dumps(users, indent=3, sort_keys=False))

    # Prepare the final JSON file with the users' mapping for the LUMA service.
    luma_mapping.append({
      "_default": {},
      "users": users,
      "groups": groups,
      "spaces": spaces
    })
    
    print (json.dumps(luma_mapping, indent=3, sort_keys=False))


if __name__ == "__main__":
        main()

