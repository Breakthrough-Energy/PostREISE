from azure.storage.blob import BlobServiceClient, BlobClient


class BlobUtil(object):
    """
    Upload figures/other files to blob storage for website
    """
    def __init__(self, connection_string, container_name):
        """
        :param connection_string:str needed in order to access storage account container
        :param container_name:str name of blob storage container
        """
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = blob_service_client.get_container_client(container_name)
        self.connection_string = connection_string
        self.container_name = container_name

    def upload_figure_as_blob(self, scenario_id, fig_path, file_name):
        """
        Uploads a figure to blob storage
        :param scenario_id:str number of scenario for folder name 
        :param fig_path:str location of file to be uploaded
        :param file_name:str name of blob on server
        :return: nothing at the moment
        """
        blob = BlobClient.from_connection_string(conn_str=self.connection_string,
                                                 container_name=self.container_name,
                                                 blob_name=scenario_id+'/'+file_name)
        try:
            with open(fig_path, "rb") as data:
                blob.upload_blob(data)
        except Exception as e:
            print(e)

    def list_scenario_figures(self, scenario_id):
        """
        Lists the blobs that start with scenario_id
        :param scenario_id:str string to match start of container blob names
        :return: enumerable list of blob info
        """
        blobs = self.container_client.list_blobs(name_starts_with=scenario_id)
        blob_list = list(blobs)
        for blob in blob_list:
            print("\t" + blob.name)
        return blob_list