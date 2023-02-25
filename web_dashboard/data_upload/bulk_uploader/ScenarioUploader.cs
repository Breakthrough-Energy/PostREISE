namespace ScenarioUploader
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.IO;
    using System.Text.Json;
    using System.Threading.Tasks;
    using Microsoft.Azure.Cosmos;


    public class ScenarioUploader
    {
        private static readonly string endpointUrl =
            Environment.GetEnvironmentVariable("COSMOS_ENDPOINT");
        private static readonly string authorizationKey =
            Environment.GetEnvironmentVariable("COSMOS_KEY");
        private static readonly string databaseName =
            Environment.GetEnvironmentVariable("COSMOS_DB_NAME");

        private const int minThroughput = 400;
        private const int maxRetryAttempts = 30;
        private const int MaxRetryWaitTime = 100; // 100 secs

        private static Database database;
        private static Container container;


        static async Task Main(string[] args)
        {
            

            string filePath = args[0];
            string schema = args[1];
            string containerName = args[2];
            int uploadThroughput = minThroughput;
            Int32.TryParse(args[3], out uploadThroughput);
            string containerMode = "UpdateContainer";
            string logFileName = args[4];
            if (args.Length > 5)
            {
                containerMode = args?[5];
            }

            ConfigureLogging(logFileName);

            DirectoryInfo dirInfo = new DirectoryInfo(filePath);

            FileInfo[] files;
            if (schema == "PowerFlow")
            {
                files = dirInfo.GetFiles("pf*");
            }
            else if (schema == "PowerGeneration")
            {
                files = dirInfo.GetFiles("pg*");
            }
            else
            {
                throw new FileNotFoundException("Files were not found for the given schema!");
            }

            Trace.WriteLine($"***Starting bulk upload at {DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss***")}");
            Trace.WriteLine("");
            Trace.WriteLine($"EndpointUrl: {ScenarioUploader.endpointUrl}");
            Console.WriteLine($"AuthorizationKey: {authorizationKey}");
            Trace.WriteLine($"DatabaseName: {databaseName}");
            Trace.WriteLine($"ContainerName: {containerName}");
            Trace.WriteLine($"ContainerMode: {containerMode}");
            Trace.WriteLine("");

            Trace.WriteLine($"Upload filepath: {dirInfo.FullName}");
            Trace.WriteLine("");

            Console.WriteLine("Press any key to start uploading...");
            Console.ReadKey();
            Trace.WriteLine($"Found {files.Length} {schema} files to upload...");
            Console.WriteLine();

            await SetupClientConnection(databaseName, containerName, containerMode, uploadThroughput);

            await SetCosmosThroughput(uploadThroughput);

            try
            {
                await UploadFilesToDatabase(files, containerName, schema);
            }
            catch (Exception ex)
            {
                Trace.WriteLine(ex);
            }
            finally
            {
                await SetCosmosThroughput(minThroughput);
            }
        }

        static void ConfigureLogging(string filename)
        {
            TextWriterTraceListener consoleWriter = new ConsoleTraceListener();
            Trace.Listeners.Add(consoleWriter);
            TextWriterTraceListener logWriter =
                new TextWriterTraceListener(
                    System.IO.File.AppendText(filename)
                    );
            Trace.Listeners.Add(logWriter);
            Trace.AutoFlush = true;
        }

        async static Task UploadFilesToDatabase(FileInfo[] files, string containerName, string schema)
        {
            foreach (var file in files)
            {
                Trace.WriteLine($"Uploading file: {file.Name}");

                var itemsToInsert = new List<KeyValuePair<PartitionKey, Stream>>();
                if (schema == "PowerFlow")
                {
                    var power_flow_items = GetInsertItems<PowerFlow>(file.FullName, containerName);
                    itemsToInsert = await ConvertToMemoryStreams<PowerFlow>(power_flow_items);
                }
                else if (schema == "PowerGeneration")
                {
                    var power_generation_items = GetInsertItems<PowerGeneration>(file.FullName, containerName);
                    itemsToInsert = await ConvertToMemoryStreams<PowerGeneration>(power_generation_items);
                }
                else
                {
                    throw new ArgumentException("A known data schema option was not provided!");
                }

                // Prepare items as memory streams with associated partition
                // keys for insertion
                Trace.WriteLine($"Preparing {itemsToInsert.Count} items to insert...");

                await BulkUploadItems(itemsToInsert);
            }
        }

        async static Task SetupClientConnection(string databaseName, string containerName, string CreateContainer, int uploadThroughput)
        {
            CosmosClient cosmosClient = new CosmosClient(endpointUrl, authorizationKey,
                new CosmosClientOptions() { AllowBulkExecution = true,
                    ConnectionMode = ConnectionMode.Gateway,
                    MaxRetryAttemptsOnRateLimitedRequests = maxRetryAttempts,
                    MaxRetryWaitTimeOnRateLimitedRequests = new TimeSpan(0, 0, MaxRetryWaitTime)
                });

            Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(databaseName);

            if (CreateContainer == "CreateContainer")
            {
                await database
                    .DefineContainer(containerName, "/scenario_id")
                    .WithIndexingPolicy()
                        .WithIndexingMode(IndexingMode.Consistent)
                        .WithIncludedPaths()
                            .Attach()
                        .WithExcludedPaths()
                            .Path("/*")
                            .Attach()
                    .Attach()
                .CreateAsync(uploadThroughput);
            }

            Container container = database.GetContainer(containerName);

            ScenarioUploader.database = database;
            ScenarioUploader.container = container;
        }

        async static Task SetCosmosThroughput(int setThroughput)
        {
            await ScenarioUploader.database.ReplaceThroughputAsync(
                ThroughputProperties.CreateManualThroughput(setThroughput));
            var currentThroughput = await ScenarioUploader.database.ReadThroughputAsync();
            if (currentThroughput == setThroughput)
            {
                Trace.WriteLine($"Throughput set to {setThroughput}RU/s");
                Trace.WriteLine("");
            }
            else
            {
                throw new Exception($"Failed to set throughput to {setThroughput}RU/s, currently at {currentThroughput}RU/s!");
            }
        }

        async static Task BulkUploadItems(List<KeyValuePair<PartitionKey, Stream>> itemsToInsert)
        {
            int numItems = itemsToInsert.Count;

            try
            {
                Console.WriteLine($"Starting...");
                Stopwatch stopwatch = Stopwatch.StartNew();

                // Create the list of Tasks that will handle the insertions
                List<Task> tasks = new List<Task>(numItems);

                for (int i = 0; i < itemsToInsert.Count; i++)
                {
                    KeyValuePair<PartitionKey, Stream> item = itemsToInsert[i];
                    tasks.Add(ScenarioUploader.container
                        .CreateItemStreamAsync(item.Value, item.Key)
                        .ContinueWith((Task<ResponseMessage> task) =>
                            {
                                using (ResponseMessage response = task.Result)
                                {
                                    if (!response.IsSuccessStatusCode)
                                    {
                                        Trace.WriteLine($"Received {response.StatusCode}" +
                                            $" ({response.ErrorMessage}) status code for operation " +
                                            $"{response.RequestMessage.RequestUri}.");
                                    }
                                }
                            })
                    );
                    if (i % 1000 == 0)
                    {
                        Console.WriteLine($"{i} items in upload queue...");
                    }
                }

                Trace.WriteLine($"Uploading {numItems} items into database...");

                await Task.WhenAll(tasks);
                stopwatch.Stop();

                Trace.WriteLine($"Finished writing {numItems} database items in {stopwatch.Elapsed}.");
                Trace.WriteLine("");
                Trace.WriteLine("");
            }
            catch (Exception ex)
            {
                Trace.WriteLine(ex);
            }
        }

        async static Task<List<KeyValuePair<PartitionKey, Stream>>> ConvertToMemoryStreams<T>(List<T> items)
        {
            List<KeyValuePair<PartitionKey, Stream>> itemsToInsert =
                new List<KeyValuePair<PartitionKey, Stream>>(items.Count);
            foreach (var item in items)
            {
                MemoryStream stream = new MemoryStream();
                await JsonSerializer.SerializeAsync(stream, item);

                Type item_type = item.GetType();
                int scenario_id = (int)item_type.GetProperty("scenario_id").GetValue(item, null);

                itemsToInsert.Add(new KeyValuePair<PartitionKey, Stream>
                    (new PartitionKey(scenario_id), stream));
            }
            return itemsToInsert;
        }


        private static List<T> GetInsertItems<T>(string FilePath, string containerName)
        {
            List<T> items = new List<T>();
            try
            {
                string jsonString = File.ReadAllText(FilePath);

                items = JsonSerializer.Deserialize<List<T>>(jsonString);

                for (int i = 0; i < items.Count; i++)
                {
                    Type item_type = items[i].GetType();
                    var prop = item_type.GetProperty("id");
                    prop.SetValue(items[i], Guid.NewGuid().ToString(), null);

                    foreach (var item_prop in item_type.GetProperties())
                    {
                        object value = item_prop.GetValue(items[i], null);

                        bool missingDataExpected = item_prop.ToString().Contains("zone")
                            || item_prop.ToString().Contains("interconnect")
                            || item_prop.ToString().Contains("plant_id");

                        bool isMissingData = value == null || string.IsNullOrEmpty(value.ToString());

                        if (!missingDataExpected && isMissingData)
                        {
                            Trace.WriteLine($"Missing data at index {i} for $property {item_prop}!");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Trace.WriteLine(ex);
            }

            return items;
        }


        public class ScenarioRecord
        {
            public string id { get; set; }
            public int scenario_id { get; set; }
        }


        public class PowerFlow : ScenarioRecord
        {   
            public string from_zone { get; set; }
            public string to_zone { get; set; }
            public string interconnect { get; set; }
            public float median_utilization { get; set; }
            public float risk { get; set; }
            public float bind { get; set; }
            public int branch_id { get; set; }
            public string LOC_ROLLUP { get; set; }
            public string TIME_ROLLUP { get; set; }
        }


        public class PowerGeneration : ScenarioRecord
        {
            public string timestamp { get; set; }
            public int plant_id { get; set; }
            public string zone { get; set; }
            public string interconnect { get; set; }
            public string LOC_ROLLUP { get; set; }
            public string TIME_ROLLUP { get; set; }
            public string resource_type { get; set; }
            public float generation { get; set; }
            public float curtailment { get; set; }
        }
    }
}
