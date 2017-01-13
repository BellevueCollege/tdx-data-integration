import json

class NewUser():

    def __init__(self):
        self.usertype = 1   #User
        self.applications = ['TDKnowledgeBase', 'TDRequests', 'TDTicketRequests']
        self.timezone = 6   #Pacific
        self.organization = 'Bellevue College'

    def dictify(self):
        data = {}
        data['TypeID'] = self.usertype
        data['Username'] = self.username
        data['AuthenticationUserName'] = self.authusername
        data['SecurityRoleID'] = self.securityrole
        data['FirstName'] = self.firstname
        data['LastName'] = self.lastname
        data['Company'] = self.organization
        data['Title'] = self.title
        data['DefaultAccountID'] = self.accountid
        data['ExternalID'] = self.orgid
        data['IsEmployee'] = self.isemployee
        data['PrimaryEmail'] = self.primaryemail
        data['AlertEmail'] = self.alertemail
        data['WorkPhone'] = self.workphone
        if self.workpostal is not None:
            data['WorkZip'] = self.workpostal
        data['TZID'] = self.timezone
        data['Applications'] = self.applications
        data['Attributes'] = self.attributes
        data['WorkAddress'] = self.workaddress
        data['ReportsToUID'] = self.reportsto

        return data