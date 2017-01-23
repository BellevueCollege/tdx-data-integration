import pymssql
import datetime
import xlsxwriter
import argparse
import logging
import tdapi
import os

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
parser.add_argument('--split', help='Specify a certain user type split. Only valid for a student usertype.')
parser.add_argument('-d', '--dry', action='store_true', help='With this option file is generated but not sent to TDX import endpoint.')
parser.add_argument('-k', '--keepfile', action='store_true', help='With this option the generated file is kept locally.')
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

user_split = None
if args.split is not None and user_type == config.usertype_student and args.split.isdigit() and int(args.split) < len(config.user_splits_student):
    user_split = int(args.split)

today = datetime.datetime.now().strftime('%Y-%m-%d.%H%M%S')

file_name = str(today) + '-' + user_type + '-' + file_type + '-import.xlsx'
# if a file creation path config value is provided, use that path for the import file
if config.file_creation_path is not None and config.file_creation_path:
    file_name = config.file_creation_path + file_name
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
                cursor.execute('SELECT * FROM vw_Employees')
            else:
                if user_split is not None:
                    sql_query = "SELECT * FROM vw_Students WHERE [Last Name] LIKE '[{}]%' ORDER BY [Last Name] asc".format(config.user_splits_student[user_split])
                else:
                    sql_query = "SELECT * FROM vw_Students"
                #print sql_query
                cursor.execute(sql_query)

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

except Exception as e:
    #print "Error ", sys.exc_info()[0].message
    #print "Error: ", e.args[0]
    logger.exception("Error connecting to db or writing to worksheet")

workbook.close()

# If this is not a dry run, then upload file to TDX import file endpoint
if args.dry is not None and args.dry is False:
    #print 'Uploading file...'

    try:
        # create file handle (read, binary)
        xlsx_fh = open(file_name, 'rb')

        # create TDX connection
        td_conn = tdapi.TDConnection(BEID=config.tdx_web_services_beid,
                                    WebServicesKey=config.tdx_web_services_key,
                                    sandbox=config.tdx_web_use_sandbox,
                                    url_root=config.tdx_web_api_root)
        tdapi.TD_CONNECTION = td_conn

        #print dir(tdapi.TD_CONNECTION)
        
        files = {file_name: (file_name,
                                xlsx_fh,
                                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )}

        td_conn.files_request(method='post',
                            url_stem='people/import',
                            files=files)
    except Exception as e:
        logger.exception("Error connecting to TeamDynamix and/or writing file to endpoint")

if args.keepfile is not None and args.keepfile is False:
    try:
        os.remove(file_name)
    except Exception as e:
        logger.exception("Error removing generated import file %s.", file_name)