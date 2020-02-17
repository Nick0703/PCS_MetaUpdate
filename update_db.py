import os
import pathlib
import shutil
import sqlite3
import sys

def confirmation():
    print("The path is: " + media_path)
    check = str(input("Is the path correct? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            global runSQL
            runSQL = True
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return confirmation()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return confirmation()

def ask_media_path():
    global media_path
    usr_input = input("Enter the path of your media location: ")
    media_path = usr_input

# DB locations
pbzInstall = pathlib.Path("/opt/appdata/plex/database/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
plexInstall = pathlib.Path("/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
cbInstall = pathlib.Path("/opt/plex/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")

# Check if whether user installed Plex with Cloudbox, pgblitz or did a normal install
if pbzInstall.exists():
    connection = sqlite3.connect(pbzInstall)
elif cbInstall.exists():
    connection = sqlite3.connect(cbInstall)
else:
    if os.geteuid() != 0:
        print("Error! Please run the script as sudo")
        sys.exit()
    connection = sqlite3.connect(plexInstall)

# Ask for the media path
ask_media_path()

# Confirm with the user if the path is correct
while not confirmation():
    ask_media_path()

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
    shutil.chown(plexInstall, user="plex", group="plex")
