#!/bin/bash

if [ "$1" == "comment" ]; then
  sed -i '/cpu=\[0\,8\,1\,2\,3\,4\,5\,6\,7\]/ c# cpu=\[0\,8\,1\,2\,3\,4\,5\,6\,7\]' shinjuku.conf
elif [ "$1" == "uncomment" ]; then
  sed -i '/# cpu=\[0\,8\,1\,2\,3\,4\,5\,6\,7\]/ ccpu=\[0\,8\,1\,2\,3\,4\,5\,6\,7\]' shinjuku.conf
fi
