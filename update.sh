#!/bin/bash

./dpkg-scanpackages -m debs /dev/null > Packages

rm Packages.gz Packages.bz2

gzip -c9 Packages > Packages.gz
bzip2 -c9 Packages > Packages.bz2
xz -c9e Packages > Packages.xz
xz -c9e  --format=lzma Packages > Packages.lzma

python gen_depictions.py

git add --all
git commit -m "."
git push origin master -q