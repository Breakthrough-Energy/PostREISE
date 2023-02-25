import gzip
import json

from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from bokeh.embed import json_item


class BlobUtil(object):
    """
    Upload figures/other files to blob storage for website
    """

    def __init__(self, connection_string, container_name):
        """
        :param connection_string: str needed in order to access storage account container
            You can find the connection string in the
            azure portal > storage accounts > access keys
        :param container_name: str name of blob storage container.
            In Storage Explorer this is the top level folder under "BLOB CONTAINERS"
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_client = blob_service_client.get_container_client(container_name)
        self.connection_string = connection_string
        self.container_name = container_name

    def upload_png(self, file_path, blob_path):
        """Uploads a figure to blob storage. Will overwrite existing files

        :param scenario_id:str number of scenario for folder name
        :param file_path:str location of png file to be uploaded
        :param blob_path:str location to put the blob in azure
            e.g. if container_name is "scenarios", blob path might be
            something like "2030_western_overbuild/emissions.png"
            thus the final blob location would be
            "scenarios/2030_western_overbuild/emissions.png"
        """
        print(f"Uploading {file_path} to {self.container_name}/{blob_path}")

        blob = BlobClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=self.container_name,
            blob_name=blob_path,
        )
        try:
            with open(file_path, "rb") as data:
                blob.upload_blob(data, overwrite=True)
                blob.set_http_headers(
                    content_settings=ContentSettings(content_type="image/png")
                )
        except Exception as e:
            print(e)

        print("Upload complete")

    def upload_gzip(self, file_path, blob_path):
        """Uploads a json gzip file to blob storage. Will overwrite existing files

        :param scenario_id:str number of scenario for folder name
        :param file_path:str location of png file to be uploaded
        :param blob_path:str location to put the blob in azure
            e.g. if container_name is "scenarios", blob path might be
            something like "2030_western_overbuild/emissions.png"
            thus the final blob location would be
            "scenarios/2030_western_overbuild/emissions.png"
        """
        print(f"Uploading {file_path} to {self.container_name}/{blob_path}")

        blob = BlobClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=self.container_name,
            blob_name=blob_path,
        )
        try:
            with open(file_path, "rb") as data:
                blob.upload_blob(data, overwrite=True)
                blob.set_http_headers(
                    content_settings=ContentSettings(
                        content_type="text/json", content_encoding="gzip"
                    )
                )
        except Exception as e:
            print(e)

        print("Upload complete")

    def upload_dict_as_json_gzip(self, data, local_save_path, blob_path):
        """Takes a dictionary, turns it into JSON, gzips it,
           saves the file locally, and uploads it to blob storage.
           Will overwrite existing files.

        :param data:dict the dictionary to be uploaded
        :param local_save_path:str location to save the gzipped json on your
            local computer
        :param blob_path:str location to put the blob in azure
                e.g. if container_name is "scenarios", blob path might be
                something like "2030_western_overbuild/emissions.png"
                thus the final blob location would be
                "scenarios/2030_western_overbuild/emissions.png"
        TODO: optionally do this without saving a file
        """
        json_str = json.dumps(data) + "\n"
        json_bytes = json_str.encode("utf-8")

        print(f"Saving file to {local_save_path}")
        with gzip.GzipFile(local_save_path, "wb") as fout:
            fout.write(json_bytes)

        self.upload_gzip(local_save_path, blob_path)

    def upload_bokeh_figure_as_json_gzip(
        self, figure, string_identifier, local_save_path, blob_path
    ):
        """Takes a bokeh figure, turns it into JSON, gzips it,
           saves the file locally, and uploads it to blob storage.
           Will overwrite existing files.

        :param figure:bokeh.model.Model figure generated by bokeh
        :param string_identifier:str bokeh uses this to attach the figure to
            html on the front end.
        :param local_save_path:str location to save the gzipped json on your
            local computer
        :param blob_path:str location to put the blob in azure
                e.g. if container_name is "scenarios", blob path might be
                something like "2030_western_overbuild/emissions.png"
                thus the final blob location would be
                "scenarios/2030_western_overbuild/emissions.png"
        TODO: optionally do this without saving a file
        NOTE: MAKE SURE YOU ARE USING THE CORRECT VERSION OF BOKEH from requirements.txt
            If you have the wrong version this will silently fail until we try
            to load the graph on the front end and then... boom
        """

        json_str = json.dumps(json_item(figure, string_identifier)) + "\n"
        json_bytes = json_str.encode("utf-8")

        print(f"Saving file to {local_save_path}")
        with gzip.GzipFile(local_save_path, "wb") as fout:
            fout.write(json_bytes)

        self.upload_gzip(local_save_path, blob_path)

    def list_blobs_in_container(self):
        """Lists the blobs that exist in the container

        :return: enumerable list of blob info
        """
        blobs = self.container_client.list_blobs()
        blob_list = list(blobs)
        for blob in blob_list:
            print("\t" + blob.name)
        return blob_list
