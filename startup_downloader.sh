#!/bin/bash
for pid in $(pidof startup_downloader.sh); do
    if [ $pid != $$ ]; then
        exit 1
    fi 
done

cd ~/Dev/Workspace/Python-FTP-Sync
python DownloadProcessor.py
echo "sh $0 $@" | at `date +%H:%M` " + 30 minutes" &
