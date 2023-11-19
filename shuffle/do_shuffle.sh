#!/bin/bash

# Get original image geometry
origgeom=$(identify -format %g input.jpg)
echo $origgeom
# Calculate new geometry as exact multiple of tilesize
newgeom=$(convert input.jpg -format "%[fx:int(w/16)*16]x%[fx:int(h/16)*16]" info:)
echo $newgeom

# Resize to new geometry and tile
convert input.jpg -resize $newgeom -crop 12x12@ tile.jpg

# Rebuild in random order then correct geometry
montage -background none -geometry +0+0 $(ls tile*jpg | awk 'BEGIN{srand()}{print rand() "\t" $0}' | sort -n | cut -f2-) JPG:- | convert JPG: -resize ${origgeom}! output.jpg

rm tile*.jpg