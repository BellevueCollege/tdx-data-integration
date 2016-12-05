import pymssql
import datetime
import xlsxwriter
import argparse
import logging

import config

logging.basicConfig(level=logging.INFO) #set logging level

def write_sheet_headers(worksheet, headers):
    write_col = 0
    for header in headers:
        worksheet.write(0, write_col, header)
        write_col += 1
    return

def increment_column():
    global write_col
    write_col += 1
    return write_col

parser = argparse.ArgumentParser()
parser.add_argument('--type', help='add or update. Default is update.')
args = parser.parse_args()

#print args.type
file_type = config.filetype_update
if args.type is not None and args.type in [config.filetype_add, config.filetype_update]:
    file_type = args.type

today = datetime.date.today()
#print file_type
#print today

workbook = xlsxwriter.Workbook('employee-'+ file_type + '-' + 'import-' + str(today) + '.xlsx')
worksheet = workbook.add_worksheet()

add_headers = ['User Type','Username','Authentication Provider','Authentication Username','Security Role','First Name','Last Name','Organization','Title','Acct/Dept','Organizational ID','Is Employee','Primary Email','Alert Email','Work Phone','Work Address','Work Postal Code','Time Zone ID','HasTDKnowledgeBase','HasTDRequests','HasTDTicketRequests','Department ID','Is Student']
update_headers = ['Username','Authentication Username','First Name','Last Name','Organization','Title','Acct/Dept','Organizational ID','Is Employee','Primary Email','Alert Email','Work Phone','Work Address','Work Postal Code','Time Zone ID','Reports To Username','Department ID', 'Is Student']

if file_type == config.filetype_add:
    write_sheet_headers(worksheet, add_headers)
else:
    write_sheet_headers(worksheet, update_headers)

try:
    with pymssql.connect(server=config.server,user=config.user,password=config.password,database=config.database) as conn:
        with conn.cursor(as_dict=True) as cursor:
            #cursor.execute('SELECT * FROM Forms')
            cursor.execute('SELECT TOP 100 * from vw_Employees')

            write_row = 1
            for row in cursor:
                write_col = 0
                if file_type == config.filetype_add:
                    worksheet.write(write_row, write_col, row['User Type'])
                
                worksheet.write(write_row, increment_column(), row['Username'])

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
                worksheet.write(write_row, increment_column(), row['Work Address'])
                worksheet.write(write_row, increment_column(), row['Work Postal Code'])
                worksheet.write(write_row, increment_column(), row['Time Zone ID'])

                if file_type == config.filetype_update:
                    worksheet.write(write_row, increment_column(), 'Reports to Username')

                if file_type == config.filetype_add:
                    worksheet.write(write_row, increment_column(), 'T')  #HasTDKnowledgeBase
                    worksheet.write(write_row, increment_column(), 'T')  #HasTDRequests
                    worksheet.write(write_row, increment_column(), 'T')  #HasTDTicketRequests

                worksheet.write(write_row, increment_column(), row['Department ID'])
                worksheet.write(write_row, increment_column(), row['Is Student'])
                write_row += 1

except Exception, e:
    #print "Error ", sys.exc_info()[0].message
    print "Error: ", e.args[0]
    logging.exception("Error connecting to db or writing to worksheet")

workbook.close()
#print dir(conn)