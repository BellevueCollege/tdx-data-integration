# Library of useful TDX-related functions
import tdapi
import newuser
import config
import logging

class TDX():

    def __init__(self):
        self.td_conn = tdapi.TDConnection(BEID=config.tdx_web_services_beid,
                                WebServicesKey=config.tdx_web_services_key,
                                sandbox=config.tdx_web_use_sandbox,
                                url_root=config.tdx_web_api_root)
        tdapi.TD_CONNECTION = self.td_conn
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO) #set logging format

    
    # get a user by username
    def get_user_by_username(self, username):
        
        user = None
        try:
            user_list = self.td_conn.json_request_roller(method='post',
                                    url_stem='people/search',
                                    data={'UserName':username})
                                    
            if len(user_list) != 1:
                self.logger.warn('Did not return a valid user for username: ' + username)
            else:
                user = user_list[0]   #get first/only item
        except Exception as e:
            self.logger.exception("Error retrieving user by username.")

        #print "Reports to user uid: " + str(user['UID'])
        return user
    
    # deactivate a user by uid
    def deactivate_user(self, user_uid):
        try:
            de_response = self.td_conn.request(method='put',
                            url_stem='people/{}/isactive?status=false'.format(user_uid)
                    )
            return de_response
        except Exception as e:
            self.logger.exception("Error deactivating user: " + user_uid)
    
    # get acct/dept by name
    def get_account_by_name(self, acct_name):
        acct_list = self.td_conn.json_request_roller(method='post',
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
    def get_default_security_role(self):
        secrole_list = self.td_conn.json_request_roller(method='post',
                                url_stem='securityroles/search',
                                data={'NameLike':config.tdx_default_securityrole_name})
        secrole = None
        if len(secrole_list) != 1:
            raise Exception('Invalid default security role search. NameLike: ' + config.tdx_default_securityrole_name)
        else:
            secrole = secrole_list[0]   #get first/only item

        #print "Security role ID: " + secrole['ID']

        return secrole

    # get group info by the group name
    def get_group_by_name(self, group_name):

        group_list = self.td_conn.json_request_roller(method='post',
                                url_stem='groups/search',
                                data={'NameLike':group_name, 'IsActive': True})

        group = None
        if len(group_list) != 1:
            if len(group_list) == 0:
                raise Exception('No groups with name: ' + group_name)
            else:
                raise Exception('Multiple groups with the same/similar name. Name: ' + group_name)
        else:
            group = group_list[0]   #get first/only item

        #print "Group ID: " + str(group['ID'])

        return group

    # add user to group by uid
    def add_user_to_group(self, user_uid, group_id):

        try:
            grp_response = self.td_conn.request(method='put',
                            url_stem='people/{}/groups/{}'.format(user_uid, group_id)
                            )
            return grp_response
        except Exception as e:
            self.logger.exception("Error adding user to group: " + str(e))
            raise

    # get custom person attributes
    def get_custom_attributes_for_people(self):

        attrs_json = self.td_conn.json_request_roller(method='get',
                    url_stem='attributes/custom?componentId={}'.format(config.tdx_component_id_person)
                    )
        
        return attrs_json

    # set custom attribute values for specific user
    def build_custom_attributes_for_user(self, attrs, user_isstudent, user_dept):
        
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

    # add user to TDX
    def add_user(self, user):
        try:
            result = self.td_conn.json_request(method='post',
                            url_stem='people',
                            data=user.dictify())
            return result
        except Exception as e:
            self.logger.exception("Error adding user with add_user: " + str(e))
            raise
    
    # upload import file
    def upload_file(self, file_name):
        try:
            # create file handle (read, binary)
            xlsx_fh = open(file_name, 'rb')

            # create file data object
            files = {file_name: (file_name,
                                    xlsx_fh,
                                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )}

            # send file to api endpoint
            self.td_conn.files_request(method='post',
                    url_stem='people/import',
                    files=files)

        except Exception as e:
            self.logger.exeption("Error in upload_file: " + str(e))
            raise
