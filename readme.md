# TeamDynamix Data Integration

### Requirements
In general, to use these scripts, you need:

 - Python 2.7 (with pip)
 - 3rd party Python packages
 	- [tdapi package](https://github.com/borwick/tdapi) by John Borwick
 	- XlsxWriter
 	- pymssql (similar to php5-mssql, this has a FreeTDS prerequisite)

### To use 
 
- Clone this repo.
- Create a config file, `config.py`, using the provided sample config file as an example.
- Update the `requirements.txt` file. Note that it provides for direct installing of the tdapi package from git. You can also clone the repo locally and update the path in your `requirements.txt` to be the local path.
- Install project requirements using `pip`.
	
	```pip install -r /path/to/requirements.txt```


## Import file creation and upload

- _create-import-file.py_

The import file creation script allows creation of files for the TeamDynamix Import Jobs functionality that does bulk imports of data. It supports creating import files for adding users and updating information for existing users, per Bellevue College's TDX data specifications for its users.

BC is considered to have two types of users - employees (full-time staff and student employees) and students (excludes student employees) as the two type of users have different data specifications and groups in TeamDynamix.

This script accepts commandline arguments.

| Argument | Accepted values | Default | Purpose | 
| --- | --- | --- | --- |
| --filetype | add, update | update | Specify type of file to generate |
| --usertype | employee, student | employee | Specify the type of user for which to generate import file | 
| --dry, -d | - | - | A flag that allows for a "dry" run, i.e. the generated file will _not_ be sent to TDX. Without this flag, the file is by default sent to TDX. |
| --keepfile, -k | - | - | A flag that specifies to keep locally the file generated. Without this flag, the file is by default deleted after it is sent to TDX. |

####Example usage
```
$ python /path/to/create-import-file.py --filetype add --usertype employee -d -k
```

## Add users via API

- _add-users-via-api.py_

This script adds smaller batches of users to TDX via the Web API.

####Example usage
```
$ python /path/to/add-users-via-api.py
```

## Deactivate users

- _deactivate-users.py_

This script deactivates users in the TDX system by setting a user's IsActive field to false. It uses the TDX Web API to do this.

####Example usage
```
$ python /path/to/deactivate-users.py
```

## Sync/update user groups

- _update-groups.py_

This script updates BC-specified TDX user groups based on user field available in TDX. As an example, it can add/remove users from an Employees group based on the the IsEmployee field in TDX. Groups to update and the TDX field to match on for each group is specified in the config file.

####Example usage
```
$ python update-groups.py
```

