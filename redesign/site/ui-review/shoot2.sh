#!/bin/bash
# usage: shoot2.sh url out w h [dark]   (headless Chrome; software GL so the WebGL canvas can draw)
W=$(cygpath -w "$2")
EXTRA=""
if [ "$5" = "dark" ]; then EXTRA="--blink-settings=preferredColorScheme=1 --force-dark-mode"; fi
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist --hide-scrollbars --virtual-time-budget=20000 --window-size=$3,$4 $EXTRA "--screenshot=$W" "$1" >/dev/null 2>&1
