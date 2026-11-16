#!/bin/bash
# usage: shot.sh url out w h [full]
W=$(cygpath -w "$2")
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=10000 --window-size=$3,$4 "--screenshot=$W" "$1" >/dev/null 2>&1
