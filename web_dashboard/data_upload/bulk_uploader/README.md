# Bulk uploading to CosmosDB

We implemented the Azure Cosmos bulk import functionality described below as a command line program within a .NET core docker container:

https://docs.microsoft.com/en-us/azure/cosmos-db/tutorial-sql-api-dotnet-bulk-import

Using the bulk uploader results in a speed improvement of a just few minutes per scenario, compared to a few hours using a multithreaded Python Cosmos API implementation.

## How to run the bulk uploader

The current steps to run the uploader are:
1. go to the `data_upload/bulk_uploader` folder in CENACS
2. add a folder called `shared`
3. copy the data files to this folder so you have access permissions
4. run this command:
`docker-compose run uploader shared PowerFlow test_container ScenarioUploads.txt CreateContainer`

The parameters are:
`uploader` = service
`arg1` = location of data folder mounted in the container
`arg2` = data schema (options are `PowerFlow` or `PowerGeneration`)
`arg3` = database container name
`arg4` = throughput speed (in RU/s)
`arg5` = name (and location) of the log file
`arg6` = whether to `CreateContainer` or `UpdateContainer`

## How to run bulk uploader bash script with preset upload parameters

Same steps 1-3 as above, however we can run:
`.upload_files_to_database.sh shared ScenarioUploads.txt`