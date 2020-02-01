from postreise.plot.upload_to_blobs.blob_upload import BlobUtil
import urllib


def test_blob_upload():
    connection_string = "DefaultEndpointsProtocol=https;AccountName=cleanenergyteststore;AccountKey=E0kD1PJ3eP54t30EbnSGTUPbhZacbsQ1CBpyx9KJDMgwhnXeseZ0rgcVxSsTlHgUQto9ugM6sgFl9APg0Dy9Pg==;EndpointSuffix=core.windows.net"

    blob_store = BlobUtil(connection_string, 'test-blob')
    blob_store.upload_figure_as_blob(200, 'TestFigure.png', 'TestFigure.png')
    