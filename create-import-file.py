import pymssql
import datetime
import xlsxwriter
import argparse
import logging
import tdapi

import config

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO) #set logging format

'''
 Functions used in script
'''
# write worksheet headers
def write_sheet_headers(worksheet, headers):
    write_col = 0
    for header in headers:
        worksheet.write(0, write_col, header)
        write_col += 1
    return

# function to increment column number
def increment_column():
    global write_col
    write_col += 1
    return write_col
''' 
End functions used
'''

# Set argument info
parser = argparse.ArgumentParser()
parser.add_argument('--filetype', help='add or update. Default is update.')
parser.add_argument('--usertype', help='employee or student. Default is employee.')
args = parser.parse_args()

# Set import file type
file_type = config.filetype_update
if args.filetype is not None and args.filetype in [config.filetype_add, config.filetype_update]:
    file_type = args.filetype
else:
    logger.warn("Invalid filetype provided. Default value used.")

# Set file user type
user_type = config.usertype_employee
if args.usertype is not None and args.usertype in [config.usertype_employee, config.usertype_student]:
    user_type = args.usertype
else:
    logger.warn("Invalid usertype provided. Default value used.")

today = datetime.date.today()
#print file_type
#print today
#print user_type

file_name = str(today) + '-' + user_type + '-' + file_type + '-import.xlsx'
workbook = xlsxwriter.Workbook(file_name)
worksheet = workbook.add_worksheet()

add_headers = ['User Type','Username','Authentication Provider','Authentication Username','Security Role','First Name','Last Name','Organization','Title','Acct/Dept','Organizational ID','Is Employee','Primary Email','Alert Email','Work Phone','Work Postal Code','Time Zone ID','HasTDKnowledgeBase','HasTDRequests','HasTDTicketRequests','Is Student']
update_headers = ['Username','Authentication Username','First Name','Last Name','Organization','Title','Acct/Dept','Organizational ID','Is Employee','Primary Email','Alert Email','Work Phone','Work Postal Code','Time Zone ID','Is Student']
headers_employee_only = ['Work Address','Department ID','Reports To Username']


# Add headers specific to employe user type
if user_type == config.usertype_employee:
    if file_type == config.filetype_add:
        add_headers = add_headers + headers_employee_only
    elif file_type == config.filetype_update:
        update_headers = update_headers + headers_employee_only

# write worksheet headers
if file_type == config.filetype_add:
    write_sheet_headers(worksheet, add_headers)
else:
    write_sheet_headers(worksheet, update_headers)

try:
    with pymssql.connect(server=config.server,user=config.user,password=config.password,database=config.database) as conn:
        with conn.cursor(as_dict=True) as cursor:

            # select the correct data
            if user_type == config.usertype_employee:
                cursor.execute('SELECT * from vw_Employees')
            else:
                cursor.execute('SELECT * from vw_Students')

            # process the data
            write_row = 1
            for row in cursor:
                write_col = 0

                if file_type == config.filetype_add:
                    worksheet.write(write_row, write_col, row['User Type'])
                    increment_column()
                
                worksheet.write(write_row, write_col, row['Username'])

                if file_type == config.filetype_add:
                    worksheet.write(write_row, increment_column(), row['Authentication Provider'])

                worksheet.write(write_row, increment_column(), row['Authentication Username'])

                if file_type == config.filetype_add:
                    worksheet.write(write_row, increment_column(), row['Security Role'])

                worksheet.write(write_row, increment_column(), row['First Name'])
                worksheet.write(write_row, increment_column(), row['Last Name'])
                worksheet.write(write_row, increment_column(), row['Organization'])
                worksheet.write(write_row, increment_column(), row['Title'])
                worksheet.write(write_row, increment_column(), row['Acct/Dept'])
                worksheet.write(write_row, increment_column(), row['Organizational ID'])
                worksheet.write(write_row, increment_column(), row['Is Employee'])
                worksheet.write(write_row, increment_column(), row['Primary Email'])
                worksheet.write(write_row, increment_column(), row['Alert Email'])
                worksheet.write(write_row, increment_column(), row['Work Phone'])
                worksheet.write(write_row, increment_column(), row['Work Postal Code'])
                worksheet.write(write_row, increment_column(), row['Time Zone ID'])

                if file_type == config.filetype_add:
                    worksheet.write(write_row, increment_column(), 'T')  #HasTDKnowledgeBase
                    worksheet.write(write_row, increment_column(), 'T')  #HasTDRequests
                    worksheet.write(write_row, increment_column(), 'T')  #HasTDTicketRequests

                worksheet.write(write_row, increment_column(), row['Is Student'])

                # add columns that apply only to employees
                if user_type == config.usertype_employee:
                    worksheet.write(write_row, increment_column(), row['Work Address'])
                    worksheet.write(write_row, increment_column(), row['Department ID'])

                    if file_type == config.filetype_add:
                        worksheet.write(write_row, increment_column(), '')
                    else:
                        worksheet.write(write_row, increment_column(), row['Reports To Username'])

                write_row += 1

except Exception, e:
    #print "Error ", sys.exc_info()[0].message
    print "Error: ", e.args[0]
    logger.exception("Error connecting to db or writing to worksheet")

workbook.close()

#print dir(conn)