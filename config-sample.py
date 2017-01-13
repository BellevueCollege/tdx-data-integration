server = '' #db server/instance
user = ''   #db user
password = ''   #db password
database = ''   #database to connect to

#file type options
filetype_add = 'add'
filetype_update = 'update'

#user type options
usertype_employee = 'employee'
usertype_student = 'student'

# TeamDynamix web services config
tdx_web_api_root = ''
tdx_web_services_beid = ''
tdx_web_services_key = ''
tdx_web_use_sandbox = True

#static variables
tdx_default_securityrole_name = ''  #Default security role for users
tdx_group_name_employee = ''        #Group name for employees group in TDX
tdx_acct_name_employee = ''         #Default acct/dept name for employees
tdx_acct_name_student = ''          #Default acct/dept name for students
tdx_component_id_person = 31        #Component ID for TDX person module
tdx_customattr_isstudent_name = ''  #Name of Is Student custom attribute
tdx_customattr_deptid_name = ''     #Name of Department ID custom attribute

#user splits
user_splits_student = ['A-Ca-c*', 'D-Id-i', 'J-Lj-l', 'M-Qm-q', 'R-Sr-s', 'T-Zt-z'] #splits student pulls into digestible chunks

#groups info for groups that should be synced in update-groups.py
groups_to_sync = []                 #TDX groups to add/remove people to/from based on a TDX field