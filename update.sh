#!/bin/bash

./dkpg-scanpackages debs /dev/null > Packages

rm Packages.gz Packages.bz2
gzip -c9 Packages > Packages.gz
bzip2 -c9 Packages > Packages.bz2

git add --all
git commit -m "Updating Files"
git push origin master