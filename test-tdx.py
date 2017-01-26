import unittest
import config
from modules.tdx import TDX

class TDXTestCase(unittest.TestCase):
    """Tests for TDX module functions"""

    def setUp(self):
        self.tdx = TDX()

    # Test of retrieving valid username (should be valid dictionary)
    def test_get_user_by_username_valid(self):

        username = 'test1@bellevuecollege.edu'
        self.assertIsInstance(self.tdx.get_user_by_username(username), dict, "Returned object is not a dict.")

    # Test of retrieving invalid username
    def test_get_user_by_username_fail(self):
        username = 'badusername@bellevuecollege.edu'    #invalid username
        self.assertIsNone(self.tdx.get_user_by_username(username), "Returned user is not None")

    # Test for 200 response to deactivating user
    def test_deactivate_user_valid(self):
        
        uid = '5df70efc-37d9-e611-80cd-000d3a13db68'    #valid uid for test4@bellevuecollege.edu user
        response = self.tdx.deactivate_user(uid)
        self.assertEqual(response.status_code, 200, "Deactivate user did not return valid response.")
    
    # Test failed deactivation of user
    def test_deactivate_user_fail(self):
    
        uid = 'xyz' #invalid UID
        response = self.tdx.deactivate_user(uid)
        #print response
        self.assertIsNone(response, "Returned something, which isn't what we want.")

    # Test get account by name with valid acct/dept name
    def test_get_account_by_name_valid(self):
        
        self.assertIsInstance(self.tdx.get_account_by_name(config.tdx_acct_name_employee), dict, "Returned account object is not a dict.")

    # Test get account by name - invalid acct/dept name
    def test_get_account_by_name_fail(self):
        
        self.assertRaises(Exception, self.tdx.get_account_by_name, 'Group that does not exist')

    # Test get default security role with valid role name
    def test_get_default_security_role_valid(self):

        self.assertIsInstance(self.tdx.get_default_security_role(), dict, "Returned role object is not a dict.")

    # Test get default security role with valid role name
    #def test_get_default_security_role_fail(self):
    #    self.assertRaises(Exception, self.tdx.get_default_security_role())

    # Test get group by name with valid group name
    def test_get_group_by_name_valid(self):

        self.assertIsInstance(self.tdx.get_group_by_name(config.tdx_group_name_employee), dict, "Returned group object is not a dict.")

    # Test get group by name with invalid group name
    def test_get_group_by_name_fail(self):

        self.assertRaises(Exception, self.tdx.get_group_by_name, 'Group name that does not exist')

    # Test add user to group with valid info
    def test_add_user_to_group_valid(self):

        uid = '5df70efc-37d9-e611-80cd-000d3a13db68'
        groupid = 5178
        response = self.tdx.add_user_to_group(uid, groupid)
        self.assertEqual(response.status_code, 200, "Add user to group did not return valid response.")
    
    # Test add user to group with invalid user
    def test_add_user_to_group_baduser(self):

        uid = 'xyz'     #invalid uid
        groupid = 5178  #valid group id

        self.assertRaises(Exception, self.tdx.add_user_to_group, uid, groupid)
    
    # Test add user to group with invalid group
    def test_add_user_to_group_badgroup(self):

        uid = '5df70efc-37d9-e611-80cd-000d3a13db68'    #valid uid for test4@bellevuecollege.edu
        groupid = 10000     #invalid group id

        self.assertRaises(Exception, self.tdx.add_user_to_group, uid, groupid)

    # Test getting custom attributes for people - successful
    def test_get_custom_attributes_for_people(self):

        self.assertIsInstance(self.tdx.get_custom_attributes_for_people(), list, "Returned custom attribute object is not a dict.")


if __name__ == '__main__':

    unittest.main()