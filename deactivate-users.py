# This script pulls recently separated users (employees) from the db and changes them to inactive in TeamDynamix
import pymssql
import datetime
import argparse
import logging

import config

from modules.tdx import TDX

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO) #set logging format

try:

    # instantiate TDX model
    tdx = TDX()

    # connect to database
    with pymssql.connect(server=config.server,user=config.user,password=config.password,database=config.database) as conn:
        with conn.cursor(as_dict=True) as cursor:

            # execute query
            cursor.execute('SELECT * FROM vw_RecentlySeparatedEmployees')

            # process the data
            for row in cursor:

                # use api to get user by username
                de_username = row['Username']
                de_user = tdx.get_user_by_username(de_username)

                # call api to deactivate user by the uid
                if de_user is not None:
                    de_response = tdx.deactivate_user(de_user["UID"])
                    logger.info("User deactivated: " + de_user['FirstName'] + " " + de_user['LastName'])

except Exception as e:
    logger.exception("Error: " + str(e))