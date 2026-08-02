#!/bin/bash

show_menu() {
    echo "===== System Information ====="
    echo "Current User: $USER"
    echo "Home Directory: $HOME"
    echo "Current Directory: $(pwd)"
    echo
}

check_disk() {
    echo "Disk Usage:"
    df -h /
    echo
}

check_memory() {
    echo "Memory Usage:"
    free -h
    echo
}

show_menu

if [ -d "$HOME/backups" ]; then
    echo "Backup folder exists."
else
    echo "Backup folder NOT found."
fi

echo

for i in 1 2 3 4 5
do
    echo "Loop Count: $i"
done

echo

check_disk

check_memory
