import os
import pathlib
import shutil
import sqlite3
import sys
import tarfile

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

def extract_confirm():
    check = str(input("Do you want to extract the tar file? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
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

def extract_tar(str):
    tar = tarfile.open("plex.tar")
    tar.extractall(str)
    tar.close

# Installation count/type
installCount = 0
installType = ""

# Installation and DB locations
pgbInstall = pathlib.Path("/opt/appdata/plex/database/")
plexInstall = pathlib.Path("/var/lib/plexmediaserver/")
cbInstall = pathlib.Path("/opt/plex/")
plexdb = ("Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")

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
        print("Error! Please run the script as sudo")
        sys.exit()

# Exit the program if we have more than 1 installation type
if installCount > 1:
    print("Error! You have more than 1 installation, please remove the old ones")
    sys.exit()
else:
    if installType == "pgblitz": # PGBlitz Installation
        if extract_confirm():
            extract_tar(pgbInstall)
        connection = sqlite3.connect(pgbInstall.joinpath(plexdb))
    elif installType == "cloudbox": # Cloudbox Installation
        if extract_confirm():
            extract_tar(cbInstall)
        connection = sqlite3.connect(cbInstall.joinpath(plexdb))
    else: # Normal Plex Installation
        if extract_confirm():
            extract_tar(plexInstall)
        connection = sqlite3.connect(plexInstall.joinpath(plexdb))

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
    shutil.chown(plexInstall.joinpath(plexdb), user="plex", group="plex")
