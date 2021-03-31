for tile_file in `ls tif_files*`; do
	cat $tile_file | awk -F '_' '{print $4 " "$3}' | awk -F '.tif' '{print $1  $2}'
done
