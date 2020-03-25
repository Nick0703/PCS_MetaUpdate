# PCS_MetaUpdate
Python script used to update plex database when using the tar file from PCS.

Download
---------------------------------
- To download the latest release [click here](https://github.com/Nick0703/PCS_MetaUpdate/releases)

Requirements
---------------------------------
- Python 3.7.5 or newer
    - Double check your python3 version `python3 --version`, if it's less than 3.7.5, update it to the latest version.
- plex.tar (If you want to use the backed-up metadata)
	- Make sure that the file is in the same directory (Script).
- pv `apt install pv`
    - Used to show the progress of the extraction.

How to use it
---------------------------------
- `python3 meta_update.py`
- If you installed PMS through dpkg (Standard Installation), then run it as sudo `sudo python3 meta_update.py`

To-do list
---------------------------------
- [x] Add a trailing "/" if the user didn't add it their path
- [x] Check whether user has multiple installation paths, currently we're just assuming that they have only one
- [x] Automatically extract the tar file and move the files over for the user
- [x] Backup the original Preferences.xml and restore it after
- [x] Rework the extraction part, not working as intended.
- [x] Double check the permissions after extracting the tar file
- [ ] Check if the custom path exists
- [ ] Fix permissions for custom path type
