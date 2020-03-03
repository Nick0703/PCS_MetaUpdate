#!/bin/bash
start="$(date -u +%s)"
Reset_Color='\033[0m'
Green='\033[0;32m'

while getopts "d:" opt; do
   case "$opt" in
      d ) opt_destination="$OPTARG" ;;
   esac
done

tar -xf plex.tar --strip-components=2 -C $opt_destination

end="$(date -u +%s)"
tmin=$(( (end-start)/60 ))
tsec=$(( (end-start)%60 ))
echo -e $Green"Total extraction time: $tmin minutes $tsec seconds"$Reset_Color
