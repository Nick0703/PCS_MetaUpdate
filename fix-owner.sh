#!/bin/bash
start="$(date -u +%s)"
Reset_Color='\033[0m'
Green='\033[0;32m'

while getopts "d:" opt; do
   case "$opt" in
      d ) opt_destination="$OPTARG" ;;
   esac
done

chown -R plex:plex $opt_destination

end="$(date -u +%s)"
tmin=$(( (end-start)/60 ))
tsec=$(( (end-start)%60 ))
echo -e $Green"Took $tmin minutes $tsec seconds to fix the permissions."$Reset_Color
