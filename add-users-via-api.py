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
    
    user = None
    try:
        user_list = td_conn.json_request_roller(method='post',
                                url_stem='people/search',
                                data={'UserName':username})
                                
        if len(user_list) != 1:
            print 'Did not return a valid user for username: ' + username
        else:
            user = user_list[0]   #get first/only item
    except Exception as e:
        logger.exception("Error retrieving user by username.")

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

    #print "Group ID: " + str(group['ID'])

    return group

# add user to group by uid
def add_user_to_group(user_uid, group_id):

    grp_response = td_conn.request(method='put',
                    url_stem='people/{}/groups/{}'.format(user_uid, group_id)
                    )
    return grp_response

# get custom person attributes
def get_custom_attributes_for_people():

    attrs_json = td_conn.json_request_roller(method='get',
                url_stem='attributes/custom?componentId={}'.format(config.tdx_component_id_person)
                )
    
    return attrs_json

# set custom attribute values for specific user
def get_custom_attributes_for_user(attrs, user_isstudent, user_dept):
    
    custom_attrs = []

    # get Is Student attribute info from custom attributes list
    isstudent_item = [d for d in attrs if d["Name"] == config.tdx_customattr_isstudent_name][0]

    if isstudent_item is not None:
        attr_id = isstudent_item["ID"]
        choices = isstudent_item["Choices"]
        value = [e for e in choices if e["Name"] == user_isstudent][0]

        #add 
        custom_attrs.append({ 'ID' : attr_id, 'Value' : value["ID"] })
        #print value["ID"]

    # get Department ID attribute info from custom attributes list
    if user_dept is not None and user_dept:
        dept_item = [d for d in attrs if d["Name"] == config.tdx_customattr_deptid_name][0]

        if dept_item is not None:
            attr_id = dept_item["ID"]
            custom_attrs.append({ 'ID' : attr_id, 'Value' : user_dept })
    
    #return generated custom attributes list
    return custom_attrs

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
                                sandbox=config.tdx_web_use_sandbox,
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

    #get people custom attributes
    people_attrs = get_custom_attributes_for_people()

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
                        rep_user = get_user_by_username(row['Reports To Username'])
                        if rep_user is not None:
                            user.reportsto = rep_user['ID']
                    user.accountid = emp_acct_id

                else:
                    user.isemployee = False
                    user.accountid = stu_acct_id

                user.attributes = get_custom_attributes_for_user(people_attrs, row["Is Student"], row["Department ID"])
                print 'Processing user ' + user.primaryemail
                #print user.attributes
                
                try:    
                    result = td_conn.json_request(method='post',
                                            url_stem='people',
                                            data=user.dictify())

                    #for k,v in result.iteritems():
                    #    print k,v
                    
                    #print "New user UID: " + result['UID']
                    uid = result['UID']

                    if user.isemployee:
                        add_user_to_group(uid, emp_groupid)
                except Exception as e:
                    #log this user error but don't bomb out other user additions
                    logger.exception("Error adding user {}: ".format(user.primaryemail) + str(e))
                
except Exception as e:
    logger.exception("Error: " + str(e))