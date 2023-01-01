#!/usr/bin/env bash

git checkout main
if [ $? -ne 0 ]; then 
    echo -e "\nCannot access git repository."
    exit 1
fi

git pull

exit 0
