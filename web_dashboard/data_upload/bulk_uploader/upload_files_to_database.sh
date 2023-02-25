#!/bin/bash
# How to run: upload_files_to_database.sh /upload_files upload_log.txt
# arg1 = location of the folder with the data files 
# arg2 = location/name for the log file

# The bulk uploader is run on individual files using something like:
# docker-compose run uploader shared/pf_data_05_13.json PowerFlow my_container CreateContainer
# The parameters are:
# uploader = container service
# arg1 = location of data folder mounted in the container
#`arg2` = data schema (options are `PowerFlow` or `PowerGeneration`)
#`arg3` = database container name
#`arg4` = throughput speed (in RU/s)
#`arg5` = name (and location) of the log file
#`arg6` = whether to `CreateContainer` or `UpdateContainer`

echo "beginning upload..." | tee -a $2
echo | tee -a $2

echo "uploading pg files..." | tee -a $2
echo | tee -a $2
docker-compose run uploader shared PowerGeneration power-generation 4000 $2

# echo "uploading pf files..." | tee -a $2
# echo | tee -a $2
# docker-compose run uploader shared PowerFlow power-flow 4000 $2

echo | tee -a $2
echo "finished uploading!"
