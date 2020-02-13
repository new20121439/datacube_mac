from google.cloud import storage
import os
from .image_processing import merge_separate_bands

from pathlib import Path

current_dir = Path(__file__).parent.absolute()

class google_cloud_class:
    credentialfile = os.path.join(current_dir, 'sentinel2-gcs.json')
    bucket_name = 'gcp-public-data-sentinel-2'
    client = storage.Client.from_service_account_json(credentialfile)

    def list_blobs(self, max_results=None):
        """Lists all the blobs in the bucket."""
        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = self.client.list_blobs(self.bucket_name, max_results=max_results)
        list_blob_name = []
        for blob in blobs:
            list_blob_name.append(blob)
        return list_blob_name

    def list_blobs_with_prefix(self, prefix, delimiter=None, max_results=None):
        """Lists all the blobs in the bucket that begin with the prefix.

        This can be used to list all blobs in a "folder", e.g. "public/".

        The delimiter argument can be used to restrict the results to only the
        "files" in the given "folder". Without the delimiter, the entire tree under
        the prefix is returned. For example, given these blobs:
            a/1.txt
            a/b/2.txt
        If you just specify prefix = 'a', you'll get back:
            a/1.txt
            a/b/2.txt
        However, if you specify prefix='a' and delimiter='/', you'll get back:
            a/1.txt
        Additionally, the same request will return blobs.prefixes populated with:
            a/b/
        """

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = self.client.list_blobs(
            self.bucket_name, prefix=prefix, delimiter=delimiter, max_results=max_results
        )

        blobs_name_result = []
        for blob in blobs:
            blobs_name_result.append(blob.name)
        if delimiter:
            blobs_prefix_result = []
            for prefix in blobs.prefixes:
                blobs_prefix_result.append(prefix)
            return {'name': blobs_name_result, 'prefix': blobs_prefix_result}
        else:
            return {'name': blobs_name_result}

    def download_blob(self, source_blob_name, destination_dir):
        """Downloads a blob from the bucket."""
        # bucket_name = "your-bucket-name"
        # source_blob_name = "storage-object-name"
        # destination_file_name = "local/path/to/file"
        destination_file_name = os.path.join(destination_dir, os.path.basename(source_blob_name))
        if os.path.exists(destination_file_name):
            print("{} is already exist.".format(destination_file_name))
            return destination_file_name
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(
            "Blob {} downloaded to {}.".format(
                source_blob_name, destination_file_name
            )
        )
        return destination_file_name

    def download_list_blob(self, list_source_blob_name, destination_dir):
        list_destination_file_name = []
        for source_blob_name in list_source_blob_name:
            destination_file_name = self.download_blob(source_blob_name, destination_dir)
            list_destination_file_name.append(destination_file_name)
        return list_destination_file_name


class sentinel2_google_cloud(google_cloud_class):

    credentialfile = os.path.join(current_dir, 'sentinel2-gcs.json')
    bucket_name = 'gcp-public-data-sentinel-2'

    def __init__(self, name_file):
        self.name_file = name_file

    def get_sentinel2_prefix(self):
        """
        UTM_ZONE: A number indicating the longitude zone in the Universal Transverse Mercator (UTM) system.
        LATITUDE_BAND: A letter in the range "C" through "X" (omitting "I" and "O") which indicates the latitude band.
        GRID_SQUARE: A two-letter code indicating the particular 100 km square region.
        GRANULE_ID: The Sentinel-2 id of a particular granule, which contains images of this grid square at some point in time.
        """
        arr = self.name_file.split('_')
        prefix = arr[5]
        return {
            'UTM_ZONE': prefix[1:3],
            'LATITUDE_BAND': prefix[3],
            'GRID_SQUARE': prefix[4:6],
            'GRANULE_ID': self.name_file,
            'NAME_BAND': prefix + '_' + arr[2]
        }

    def get_band_blobs(self, bands, resolution):
        """
        return:
            List
            download_objects: paths of bands of the image which store in google cloud
        """
        sentinel2_prefix = self.get_sentinel2_prefix()
        resolution = str(resolution) + 'm'
        GRANULE_prefix = "L2/tiles/{}/{}/{}/{}.SAFE/GRANULE/".format(sentinel2_prefix['UTM_ZONE'],
                                                                     sentinel2_prefix['LATITUDE_BAND'],
                                                                     sentinel2_prefix['GRID_SQUARE'],
                                                                     sentinel2_prefix['GRANULE_ID'])
        response = self.list_blobs_with_prefix(GRANULE_prefix, '/')
        print(response['prefix'])
        sub_granule_prefix = response['prefix'][0]
        prefix = sub_granule_prefix + 'IMG_DATA/R' + resolution + '/'
        list_blob_name = []
        for band in bands:
            blob_name = prefix + '{}_B0{}_{}.jp2'.format(sentinel2_prefix['NAME_BAND'], band, resolution)
            list_blob_name.append(blob_name)
        return list_blob_name

    def download(self, destination_dir, bands=[2, 3, 4, 8], resolution=10):
        list_source_blob_name = self.get_band_blobs(bands, resolution)
        list_destination_file_name = self.download_list_blob(list_source_blob_name, destination_dir)
        merge_path = merge_separate_bands(list_destination_file_name, self.name_file)
        return merge_path


def main():
    sentinel2_google_cloud(file_name).download(download_dir, bands=[2, 3, 4, 8], resolution=10)

if __name__ == "__main__":
    file_name = 'S2A_MSIL2A_20191213T034141_N0213_R061_T47PQS_20191213T070657'
    download_dir = '/home/dung/Downloads/sentinel_2'
    main()