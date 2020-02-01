from postreise.plot.upload_to_blobs.blob_upload import BlobUtil


def test_blob_upload():
    conn_str  = "DefaultEndpointsProtocol=https;AccountName=cleanenergyteststore;AccountKey=E0kD1PJ3eP54t30EbnSGTUPbhZacbsQ1CBpyx9KJDMgwhnXeseZ0rgcVxSsTlHgUQto9ugM6sgFl9APg0Dy9Pg==;EndpointSuffix=core.windows.net"
    blob_store = BlobUtil(conn_str , 'test-blob')

    scenario_id = '88'
    fig_path = './WesternInfeasibilities.png'
    file_name = 'WesternInfeasibilities.png'
    blob_store.upload_figure_as_blob(scenario_id, fig_path, file_name)
