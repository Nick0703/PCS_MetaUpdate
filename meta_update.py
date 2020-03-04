#!/usr/bin/env python3

import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys

# Installation count/type
installCount = 0
installType = ""

# Installation and DB locations
pgbInstall = pathlib.Path("/opt/appdata/plex/database/")
plexInstall = pathlib.Path("/var/lib/plexmediaserver/")
cbInstall = pathlib.Path("/opt/plex/")
plexdb = ("Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
plexPref = ("Library/Application Support/Plex Media Server/Preferences.xml")
plexPrefBack = ("Library/Application Support/Plex Media Server/Preferences.xml.back")
metaTar = pathlib.Path("plex.tar")
extMsg = "Do you want to extract the tar file? (Y/N): "
pathMsg = "\nIs the path correct? (Y/N): "

def confirmation(msg):
    check = str(input(msg)).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print("Invalid Input.")
            return confirmation(msg)
    except Exception as error:
        print("Please enter valid inputs.")
        #print(error)
        return confirmation(msg)

def ask_media_path():
    global media_path
    usr_input = input("\nEnter the path of your media location: ")
    media_path = usr_input

def extract_tar(arg):
    if metaTar.exists():
        print("\nExtracting the tar file, this might take a while...")
        subprocess.check_call("./extract.sh -d '%s'" % str(arg), shell=True)
    else:
        print("\nError! Tar file not found.")
        print("Please make sure that the plex.tar is in the same directory.")
        sys.exit()

def fix_permissions(arg):
    print("\nFixing the permissions on the extracted files, this might take a while...")
    subprocess.check_call("./fix-owner.sh -d '%s'" % str(arg), shell=True)

# Check if whether user installed Plex with Cloudbox, pgblitz or did a normal install
if pgbInstall.exists():
    installCount = installCount + 1
    installType = "pgblitz"
elif cbInstall.exists():
    installCount = installCount + 1
    installType = "cloudbox"
else:
    installCount = installCount + 1
    if os.geteuid() != 0:
        print("Error! Please run the script as sudo.")
        sys.exit()

# Exit the program if we have more than 1 installation type
if installCount > 1:
    print("Error! You have more than 1 installation, please remove the old ones.")
    sys.exit()
else:
    if installType == "pgblitz": # PGBlitz Installation
        if confirmation(extMsg):
            # Rename the old Preferences.xml
            if pgbInstall.joinpath(plexPref).exists():
                os.rename(pgbInstall.joinpath(plexPref), pgbInstall.joinpath(plexPrefBack))

            # Extract the tar file
            extract_tar(pgbInstall)

            # Rename the Preferences.xml back
            if pgbInstall.joinpath(plexPrefBack).exists():
                os.rename(pgbInstall.joinpath(plexPrefBack), pgbInstall.joinpath(plexPref))

        connection = sqlite3.connect(pgbInstall.joinpath(plexdb))
    elif installType == "cloudbox": # Cloudbox Installation
        if confirmation(extMsg):
            # Rename the old Preferences.xml
            if cbInstall.joinpath(plexPref).exists():
                os.rename(cbInstall.joinpath(plexPref), cbInstall.joinpath(plexPrefBack))

            # Extract the tar file
            extract_tar(cbInstall)

            # Rename the Preferences.xml back
            if cbInstall.joinpath(plexPrefBack).exists():
                os.rename(cbInstall.joinpath(plexPrefBack), cbInstall.joinpath(plexPref))

        connection = sqlite3.connect(cbInstall.joinpath(plexdb))
    else: # Normal Plex Installation
        if confirmation(extMsg):
            # Rename the old Preferences.xml
            if plexInstall.joinpath(plexPref).exists():
                os.rename(plexInstall.joinpath(plexPref), plexInstall.joinpath(plexPrefBack))

            # Extract the tar file
            extract_tar(plexInstall)

            # Rename the Preferences.xml back
            if plexInstall.joinpath(plexPrefBack).exists():
                os.rename(plexInstall.joinpath(plexPrefBack), plexInstall.joinpath(plexPref))

        connection = sqlite3.connect(plexInstall.joinpath(plexdb))

# Ask for the media path
ask_media_path()

# Confirm with the user if the path is correct
print("The path is: " + media_path)
while not confirmation(pathMsg):
    ask_media_path()
runSQL = True

# Check the media path and make sure it ends with "/"
correct_path = media_path.endswith('/')
if not correct_path:
    media_path = media_path + "/"

# If the user answered yes for the correct path
if runSQL:
    cursor = connection.cursor()

    sql_command = """UPDATE section_locations SET root_path= replace(root_path, "/mnt/unionfs/Media/", "{}") where root_path like "%/mnt/unionfs/Media/%";""".format(media_path)
    cursor.execute(sql_command)

    sql_command = """UPDATE media_streams SET url= replace(url, "file:///mnt/unionfs/Media/", "file://{}") where url like "%file:///mnt/unionfs/Media/%";""".format(media_path)
    cursor.execute(sql_command)

    sql_command = """UPDATE media_parts SET file= replace(file, "/mnt/unionfs/Media/", "{}") where file like "%/mnt/unionfs/Media/%";""".format(media_path)
    cursor.execute(sql_command)

    # Commit the changes
    connection.commit()

    # Close the connection
    connection.close()

# Make sure that the db for the normal plex install has the proper
# ownership
if plexInstall.exists():
    fix_permissions(plexInstall)
