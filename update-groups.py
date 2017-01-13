#!python
"""
Code to set the membership of a TeamDynamix group to the values
from a TeamDynamix people search.
"""

import argparse
import logging

import tdapi
from tdapi.group import TDGroup
from tdapi.person import TDPerson
import config                    # Read config file

# Set log level.
logger = logging.basicConfig(level=logging.INFO)

class SetgroupException(Exception): pass
class SetgroupConfigurationException(SetgroupException): pass

class SetgroupConfiguration(object):
    """
    Reads read configuration into local object
    """
    def __init__(self):
        # FIXME validate config file
        #self.config = config
        self._validate_args()

    def _validate_args(self):
        if config.tdx_web_services_beid is None:
            raise SetgroupConfigurationException("tdx_web_services_beid not specified in config file.")
        if config.tdx_web_services_key is None:
            raise SetgroupConfigurationException("tdx_web_services_key not specified in config file.")
        if config.tdx_web_use_sandbox is None:
            raise SetgroupConfigurationException("tdx_web_use_sandbox not specified in config file.")
        if config.groups_to_sync is None:
            raise SetgroupConfigurationException("groups_to_sync not specified in config file.")
        for group_obj in config.groups_to_sync:
            if not group_obj.has_key('name'):
                raise SetgroupConfigurationException("A group in groups_to_sync config does not have a name attribute.")
            if not group_obj.has_key('match_on'):
                raise SetgroupConfigurationException("A group in groups_to_sync config does not have a match_on key/value set.")

    def BEID(self): return config.tdx_web_services_beid
    def WebServicesKey(self): return config.tdx_web_services_key
    def WebAPIRoot(self): return config.tdx_web_api_root
    def UseSandbox(self): return config.tdx_web_use_sandbox

    def td_conn(self):
        """
        Creates a TeamDynamix connection using the BEID and WebServicesKey
        properties from the config file.
        """
        return tdapi.TDConnection(BEID=self.BEID(),
                                WebServicesKey=self.WebServicesKey(),
                                sandbox=self.UseSandbox(),
                                url_root=self.WebAPIRoot())

    def groups(self):
        """
        Returns the raw groups section of the configuration file.
        """
        return config.groups_to_sync


if __name__ == '__main__':

    #set config
    gconfig = SetgroupConfiguration()

    #create TDX connection
    logging.debug("Connecting to TeamDynamix")
    td_conn = gconfig.td_conn()
    tdapi.TD_CONNECTION = td_conn
    
    #loops through groups to sync and process each one
    logging.debug("Parsing through groups set in config file")
    for group in gconfig.groups():
        group_name = group['name']
        match_on = group['match_on']
        
        # Part #1: Find group & get members
        logging.debug("Looking for group %s", group_name)
        td_groups = TDGroup.objects.search({'NameLike': group_name})
        if len(td_groups) != 1:
            raise Exception("Could not find exactly one match for {}".format(group_name))

        td_group = td_groups[0]
        td_group_id = td_group.get('ID')
        logging.debug("Found group %s (%s)", group_name, td_group_id)

        logging.debug("Getting group members...")

        # FIXME check this to make sure there's not a limit (e.g. 1000 results max)
        td_group_members = td_group.members()
                                
        # Part #2: Find people matching criteria
        logging.debug("Searching for users...")
        # TODO consider expanding match_on to do a client-side search
        # after fetching all users.
        matching_people = TDPerson.objects.search(match_on)

        # Part #3: figure out the differences
        groupmember_set = set(td_group_members)
        people_set = set(matching_people)
        logging.debug("Have %s group members and %s people matches",
                      len(groupmember_set), len(people_set))
        
        logging.debug("Figuring out what needs to change")
        # a.difference(b) means stuff in a not b
        #   ergo: group members not in the people search results:
        people_to_remove = groupmember_set.difference(people_set)

        #   and people search results not in group:
        people_to_add = people_set.difference(groupmember_set)

        logging.info("Found %s people to remove and %s people to add to group %s.",
                     len(people_to_remove),
                     len(people_to_add),
                     group_name)

        # Part #4: add people who weren't in the group:
        logging.debug("Now adding people")
        for person in people_to_add:
            logging.debug("Adding %s", person)
            # TODO test this to see what happens if you call it twice.
            person.add_group_by_id(td_group_id)

        # Part #5: remove people who shouldn't be in the group:
        logging.debug("Now removing people")
        print "Remove {}".format(people_to_remove)
        for person in people_to_remove:
            logging.debug("Removing %s", person)
            # TODO make this more resilient? e.g. if person has
            # already been removed from group?
            person.del_group_by_id(td_group_id)

    logging.info("Done syncing groups!")