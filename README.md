# PCS_MetaUpdate
Python script used to update plex database when using the tar file from PCS.

Requirements
---------------------------------
- Python 3.0

How to use it
---------------------------------
- `python3 meta_update.py`
- If you installed PMS through dpkg, then run it as sudo `sudo python3 meta_update.py`

To-do list
---------------------------------
- [x] Add a trailing "/" if the user didn't add it their path
- [x] Check whether user has multiple installation paths, currently we're just assuming that they have only one
- [x] Automatically extract the tar file and move the files over for the user
- [x] Backup the original Preferences.xml and restore it after
