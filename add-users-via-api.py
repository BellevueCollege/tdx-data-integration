import pymssql
import datetime
import argparse
import logging
#import tdapi

import config

from modules.newuser import NewUser
from modules.tdx import TDX

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO) #set logging format

try:

    tdx = TDX()

    # get default security role info
    secrole = tdx.get_default_security_role()
    secroleid = secrole['ID']

    #get employee group info
    emp_group = tdx.get_group_by_name(config.tdx_group_name_employee)
    emp_groupid = emp_group['ID']

    #get employee acct/dept id
    emp_acct = tdx.get_account_by_name(config.tdx_acct_name_employee)
    emp_acct_id = emp_acct['ID']

    #get student acct/dept id
    stu_acct = tdx.get_account_by_name(config.tdx_acct_name_student)
    stu_acct_id = stu_acct['ID']

    #get people custom attributes
    people_attrs = tdx.get_custom_attributes_for_people()

    # connect to database
    with pymssql.connect(server=config.server,user=config.user,password=config.password,database=config.database) as conn:
        with conn.cursor(as_dict=True) as cursor:

            # execute query
            cursor.execute('exec dbo.usp_SELECT_NewUsers')

            # process the data
            for row in cursor:

                user = NewUser()
                user.username = row['Username']
                user.firstname = row['First Name']
                user.lastname = row['Last Name']
                user.primaryemail = row['Primary Email']
                user.alertemail = row['Alert Email']
                user.title = row['Title']
                user.orgid = row['Organizational ID']
                user.workphone = row['Work Phone']

                # Quirk alert: Work postal despite no longer being required in an import file is still 
                # required when adding a user via the API. So we must set this for both students and employees.
                user.workpostal = row['Work Postal Code']

                user.authusername = row['Authentication Username']
                user.securityrole = secroleid
                user.workaddress = row['Work Address']
                user.reportsto = None

                if row['Is Employee'] == 'T':
                    #set employee-specific items
                    user.isemployee = True

                     #get reports to user
                    if row['Reports To Username']:
                        rep_user = tdx.get_user_by_username(row['Reports To Username'])
                        if rep_user is not None:
                            user.reportsto = rep_user['UID']
                    user.accountid = emp_acct_id

                else:
                    user.isemployee = False
                    user.accountid = stu_acct_id

                user.attributes = tdx.build_custom_attributes_for_user(people_attrs, row["Is Student"], row["Department ID"])
                logger.info('Processing user ' + user.primaryemail)

                #print user.attributes
                
                try:    
                    result = tdx.add_user(user)

                    #for k,v in result.iteritems():
                    #    print k,v
                    
                    #print "New user UID: " + result['UID']
                    uid = result['UID']

                    if user.isemployee:
                        tdx.add_user_to_group(uid, emp_groupid)
                except Exception as e:
                    #log this user error but don't bomb out other user additions
                    logger.exception("Error adding user {}: ".format(user.primaryemail) + str(e))
                
except Exception as e:
    logger.exception("Error: " + str(e))