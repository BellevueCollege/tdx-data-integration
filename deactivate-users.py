# This script pulls recently separated users (employees) from the db and changes them to inactive in TeamDynamix
import pymssql
import datetime
import argparse
import logging
import tdapi

import config

from newuser import NewUser

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO) #set logging format

'''
#
# WELCOME TO THE FUNCTIONS SECTION
#
'''
# get a user by username
def get_user_by_username(username):
    user_list = td_conn.json_request_roller(method='post',
                            url_stem='people/search',
                            data={'UserName':username})
    user = None
    if len(user_list) != 1:
        print 'Did not return a valid user for username: ' + username
    else:
        user = user_list[0]   #get first/only item

    #print "User uid: " + str(user['UID'])

    return user

# get a user by username
def deactivate_user(user_uid):
    try:
        de_response = td_conn.request(method='put',
                        url_stem='people/{}/isactive?status=false'.format(user_uid)
                )
    except Exception as e:
        print "Error deactivating user: " + user_uid
    
'''
#
# END OF THE FUNCTIONS SECTION
# PEACE BE WITH YOU
#
'''

try:

    # create TDX connection
    td_conn = tdapi.TDConnection(BEID=config.tdx_web_services_beid,
                                WebServicesKey=config.tdx_web_services_key,
                                sandbox=True,
                                url_root=config.tdx_web_api_root)
    tdapi.TD_CONNECTION = td_conn

    # connect to database
    with pymssql.connect(server=config.server,user=config.user,password=config.password,database=config.database) as conn:
        with conn.cursor(as_dict=True) as cursor:

            # execute query
            cursor.execute('SELECT * FROM vw_RecentlySeparatedEmployees')

            # process the data
            for row in cursor:

                # use api to get user by username
                de_username = row['Username']
                de_user = get_user_by_username(de_username)

                # call api to deactivate user by the uid
                if de_user is not None:
                    de_response = deactivate_user(de_user["UID"])
                    print "User deactivated: " + de_user['FirstName'] + " " + de_user['LastName']

except Exception as e:
    logger.exception("Error: " + str(e))