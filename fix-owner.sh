#!/bin/bash
start="$(date -u +%s)"
Reset_Color='\033[0m'
Green='\033[0;32m'

while getopts "d:u:g:" opt; do
   case "$opt" in
      d ) opt_destination="$OPTARG" ;;
      u ) opt_user="$OPTARG" ;;
      g ) opt_group="$OPTARG" ;;
   esac
done

#find $opt_destination ! -user $opt_user -exec chown $opt_user:$opt_group {} \;
chown -R $opt_user:$opt_group $opt_destination

end="$(date -u +%s)"
tmin=$(( (end-start)/60 ))
tsec=$(( (end-start)%60 ))
echo -e $Green"Took $tmin minutes $tsec seconds to fix the ownerships."$Reset_Color
