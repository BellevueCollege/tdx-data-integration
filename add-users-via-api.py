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
# get acct/dept by name
def get_account_by_name(acct_name):
    acct_list = td_conn.json_request_roller(method='post',
                            url_stem='accounts/search',
                            data={'SearchText':acct_name})
    acct = None
    if len(acct_list) != 1:
        raise Exception('Acct/dept not found. SearchText: ' + acct_name)
    else:
        acct = acct_list[0]   #get first/only item

    #print "Acct id: " + str(acct['ID'])

    return acct

# get default security role info
def get_default_security_role():
    secrole_list = td_conn.json_request_roller(method='post',
                            url_stem='securityroles/search',
                            data={'NameLike':config.tdx_default_securityrole_name})
    secrole = None
    if len(secrole_list) != 1:
        raise Exception('Invalid default security role search. NameLike: ' + config.tdx_default_securityrole_name)
    else:
        secrole = secrole_list[0]   #get first/only item

    #print "Security role ID: " + secrole['ID']

    return secrole

# get a user by username
def get_user_by_username(username):
    try:
        user_list = td_conn.json_request_roller(method='post',
                                url_stem='people/search',
                                data={'UserName':username})
                                
        user = None
        if len(user_list) != 1:
            print 'Did not return a valid user for username: ' + username
        else:
            user = user_list[0]   #get first/only item
    except Exception as e:
    
    #print "Reports to user uid: " + str(user['UID'])
    return user

# get group info by the group name
def get_group_by_name(group_name):

    group_list = td_conn.json_request_roller(method='post',
                            url_stem='groups/search',
                            data={'NameLike':group_name, 'IsActive': True})

    group = None
    if len(group_list) > 1:
        raise Exception('Multiple groups with the same/similar name. Name: ' + group_name)
    else:
        group = group_list[0]   #get first/only item

    print "Group ID: " + str(group['ID'])

    return group

# add user to group by uid
def add_user_to_group(user_uid, group_id):

    grp_response = td_conn.request(method='put',
                    url_stem='people/{}/groups/{}'.format(user_uid, group_id)
                    )
    return grp_response
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

    # get default security role info
    secrole = get_default_security_role()
    secroleid = secrole['ID']

    #get employee group info
    emp_group = get_group_by_name(config.tdx_group_name_employee)
    emp_groupid = emp_group['ID']

    #get employee acct/dept id
    emp_acct = get_account_by_name(config.tdx_acct_name_employee)
    emp_acct_id = emp_acct['ID']

    #get student acct/dept id
    stu_acct = get_account_by_name(config.tdx_acct_name_student)
    stu_acct_id = stu_acct['ID']

    # connect to database
    with pymssql.connect(server=config.server,user=config.user,password=config.password,database=config.database) as conn:
        with conn.cursor(as_dict=True) as cursor:

            # execute query
            cursor.execute('SELECT * FROM vw_NewUsers')

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
                user.workpostal = row['Work Postal Code']
                user.authusername = row['Authentication Username']
                user.securityrole = secroleid
                user.workaddress = row['Work Address']

                if row['Is Employee'] == 'T':
                    #set employee-specific items
                    user.isemployee = True

                     #get reports to user
                    rep_user = get_user_by_username(row['Reports To Username'])
                    if rep_user is not None:
                        user.reportsto = rep_user['ID']
                    user.accountid = emp_acct_id
                    #set IsStudent
                    #set Department ID
                else:
                    user.isemployee = False
                    user.accountid = stu_acct_id
                    #set Is Student

                ''''
                user.attributes = [ { 'ID' : 25865, 'Value' : 60954 }, { 'ID' : 25858, 'Value' : '11115' } ]
                '''                  
                result = td_conn.json_request(method='post',
                                        url_stem='people',
                                        data=user.dictify())

                for k,v in result.iteritems():
                    print k,v
                
                print "New user UID: " + result['UID']
                uid = result['UID']

                if user.isemployee:
                    add_user_to_group(uid, emp_groupid)

except Exception as e:
    logger.exception("Error: " + str(e))