#!/bin/bash

read -p "Enter a number: " num

while [ $num -gt 0 ]
do
    echo "Countdown: $num"
    num=$((num-1))
    sleep 1
done

echo "Done!"
