#!/usr/bin/env python3

import apt
import os
import pathlib
import shutil
import sqlite3
import subprocess
import sys

# Check the python version, minimum version needs to be 3.7
if sys.version_info < (3, 7):
    sys.exit("You must use Python 3.7 or newer.")

# Check if pv is installed
cache = apt.Cache()
cache.open()
try:
    cache["pv"].is_installed
except Exception:
    sys.exit("You must install pv, apt install pv.")

# Installation type
installType = ""

# Installation and files/DB locations
pgbInstall = pathlib.Path("/opt/appdata/plex/database/")
plexInstall = pathlib.Path("/var/lib/plexmediaserver/")
cbInstall = pathlib.Path("/opt/plex/")
customInstall = ""

plexdb = ("Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db")
plexdbBack = ("Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db.back")
plexPref = ("Library/Application Support/Plex Media Server/Preferences.xml")
plexPrefBack = ("Library/Application Support/Plex Media Server/Preferences.xml.back")

metaTar = pathlib.Path("plex.tar")
extMsg = "\nDo you want to extract the tar file? (Y/N): "
pathMsg = "\nIs the path correct? (Y/N): "

extractScript = pathlib.Path("extract.sh")
fixOwnerScript = pathlib.Path("fix-owner.sh")

# User input confirmation
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
        return confirmation(msg)

# Fix the ownership of the files
def fix_ownership(arg, arg2, arg3):
    print("\nFixing the ownership on the extracted files, this might take a while...")
    cmd = "./fix-owner.sh -d {} -u {} -g {}".format(arg, arg2, arg3)
    subprocess.check_call(cmd, shell=True)

# Make sure the helper scripts are executable
def make_executable():
    if extractScript.exists():
        os.chmod(extractScript, 0o775)

    if fixOwnerScript.exists():
        os.chmod(fixOwnerScript, 0o775)

# Tar extraction
def extract_tar(arg):
    # Rename the old Preferences.xml
    if arg.joinpath(plexPref).exists():
        os.rename(arg.joinpath(plexPref), arg.joinpath(plexPrefBack))

    # Extract the tar file
    if metaTar.exists():
        print("\nExtracting the tar file, this might take a while...")
        subprocess.check_call("./extract.sh -d '%s'" % str(arg), shell=True)
    else:
        print("\nError! Tar file not found.")
        print("Please make sure that the plex.tar is in the same directory.")
        sys.exit()

    # Rename the Preferences.xml back
    if arg.joinpath(plexPrefBack).exists():
        os.rename(arg.joinpath(plexPrefBack), arg.joinpath(plexPref))

# Execute Order 66
def update_database(arg):
    # Ask for the mount path
    mount_path = input("\nEnter the path of your mount location (E.g. /mnt/plexcloudservers/): ")

    # Confirm with the user if the path is correct
    print("The path is: " + mount_path)
    while not confirmation(pathMsg):
        mount_path = input("\nEnter the path of your mount location (E.g. /mnt/plexcloudservers/): ")

    # Check the mount path and make sure it ends with "/"
    correct_path = mount_path.endswith('/')
    if not correct_path:
        mount_path = mount_path + "/"

    # Backup Database
    if mount_path(plexdb).exists():
	    shutil.copy(mount_path(plexdb), mount_path(plexdbBack), *, follow_symlinks=True)
    print("\nCreating Backup of the Database.")

    print("\nUpdating the database to reflect the new mount path.")
    connection = sqlite3.connect(arg.joinpath(plexdb))
    
    cursor = connection.cursor()

    sql_command = """UPDATE section_locations SET root_path= replace(root_path, "/mnt/unionfs/Media/", "{}") where root_path like "%/mnt/unionfs/Media/%";""".format(mount_path)
    cursor.execute(sql_command)

    sql_command = """UPDATE media_streams SET url= replace(url, "file:///mnt/unionfs/Media/", "file://{}") where url like "%file:///mnt/unionfs/Media/%";""".format(mount_path)
    cursor.execute(sql_command)

    sql_command = """UPDATE media_parts SET file= replace(file, "/mnt/unionfs/Media/", "{}") where file like "%/mnt/unionfs/Media/%";""".format(mount_path)
    cursor.execute(sql_command)

    # Commit the changess
    connection.commit()

    # Close the connection
    connection.close()
    
    print("Database is updated.")

#Removing the database backup
def remove_database_backup(arg):
    # Ask for the mount path
    mount_path = input("\nEnter the path of your mount location (E.g. /mnt/plexcloudservers/): ")

    # Confirm with the user if the path is correct
    print("The path is: " + mount_path)
    while not confirmation(pathMsg):
        mount_path = input("\nEnter the path of your mount location (E.g. /mnt/plexcloudservers/): ")

    # Check the mount path and make sure it ends with "/"
    correct_path = mount_path.endswith('/')
    if not correct_path:
        mount_path = mount_path + "/"

    # Backup Database
    if mount_path(plexdbBack).exists():
        os.remove(mount_path(plexdbBack))
    print("\nDeleting Backup of the Database.")
	
# Menu
def make_menu():
    global installType
    global customInstall
    options = "0"
    while options == "0":
        print("Please select your installation type:\n")
        print(" 1. PGBlitz\n 2. CloudBox\n 3. Plex Media Server .deb file (Standard Install)\n 4. Custom path (Docker Install)\n 5. Exit\n")
        options = input("Option (1-5): ")
        
        if options == "1":
            if pgbInstall.exists():
                installType = "pgblitz"
        
        elif options == "2":
            if cbInstall.exists():
                installType = "cloudbox"
        
        elif options == "3":
            if os.geteuid() != 0:
                print("Error! Please run the script as sudo.")
                sys.exit()
            
            if plexInstall.exists():
                installType = "dpkg"
        
        elif options == "4":
            if os.geteuid() != 0:
                print("Error! Please run the script as sudo.")
                sys.exit()
            
            usrPath = input("\nPlease enter the path of the custom installation: ")
            print("The path is: " + usrPath)
            while not confirmation(pathMsg):
                usrPath = input("\nEnter the path of the custom installation: ")

            if not pathlib.Path(usrPath).exists():
                sys.exit("\nPath doesn't exist, please double check it!\n")
            else:
                customInstall = usrPath

            installType = "custom"
        
        elif options == "5":
            print("\nExiting")
            sys.exit()
        
        else:
            print("\nIncorrect answer")
            return make_menu()

# Main function
def main():
    # Make the menu
    make_menu()

    if installType == "pgblitz": # PGBlitz Installation
        if confirmation(extMsg):
            extract_tar(pgbInstall)

        # Execute Order 66
        update_database(pgbInstall)
    
    elif installType == "cloudbox": # Cloudbox Installation
        if confirmation(extMsg):
            extract_tar(cbInstall)

        # Execute Order 66
        update_database(cbInstall)
    
    elif installType == "dpkg": # Normal Plex Installation
        if confirmation(extMsg):
            extract_tar(plexInstall)

        # Execute Order 66
        update_database(plexInstall)

        # Fix the ownership
        fix_ownership(plexInstall, "plex", "plex")
    
    elif installType == "custom": # Plex Docker Installation
        if confirmation(extMsg):
            extract_tar(pathlib.Path(customInstall))
        
        # Execute Order 66
        update_database(pathlib.Path(customInstall))

        # Custom user:group
        print("\nSetting custom ownership for the files, e.g. chown user:user")
        perm_user = input("\nEnter the user name: ")
        perm_group = input("Enter the group name: ")
        
        # Fixing the ownership
        fix_ownership(customInstall, perm_user, perm_group)
		
    elif installType == "DeleteDatabaseBackup": # Database Removal
        if confirmation(extMsg):
                # Remove Database Backup
        remove_database_backup(mount_path)   
    else:
        sys.exit("\nWell then something went wrong here... Exiting")

# Main program
main()
print("\nDone. Enjoy!")
