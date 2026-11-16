#!/bin/bash
# usage: mshot.sh route out [h]  390 px wide via iframe wrapper
W=$(cygpath -w "$PWD/$2")
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=12000 --window-size=420,${3:-1800} "--screenshot=$W" "http://localhost:8791/ui-review/mwrap.html?h=${3:-1800}&u=../index.html%23$1" >/dev/null 2>&1
