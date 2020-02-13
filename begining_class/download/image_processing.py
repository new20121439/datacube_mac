import os
from .utils import get_name, make_dest_path
import gdal, gdalconst
from cogeotiff.cog import create_cog
from glob import glob


def merge_separate_bands(band_paths, name_file):
    """
    Merge seperate band (tif, jp2,...) into name_file.tif
    """
    print('Merge seperate bands')
    dest_path = os.path.dirname(band_paths[0]) + '/' + name_file + '.tif'
    if not os.path.exists(dest_path):
        cmd = 'gdal_merge.py -separate -a_nodata 0 -o {} {}'.format(dest_path, ' '.join(band_paths))
        os.system(cmd)
        for band_path in band_paths:
            if os.path.exists(band_path):
                os.remove(band_path)
    return dest_path


def process_by_snap(path, gpt='~/app/snap/bin/gpt', graph='graph_mlc_50m.xml'):
    dest_path = make_dest_path(path, '.tif')
    if not os.path.exists(dest_path):
        cmd = gpt + '  {} -Pinputfile={} -Poutputfile={}'.format(graph, path, dest_path)
        os.system(cmd)
    return dest_path


def set_metadata(source_path, dest_path):
    # Open the file:
    file_name = get_name(source_path)
    source_path = '/vsizip/{0}/{1}.SAFE'.format(source_path, file_name)
    source_ds = gdal.Open(source_path, gdalconst.GA_ReadOnly)
    metadata = source_ds.GetMetadata()
    gcp = source_ds.GetGCPs()
    gcpproj = source_ds.GetGCPProjection()

    ds = gdal.Open(dest_path, gdalconst.GA_Update)

    # resolution from 10m to 50m
    newgcp = [gdal.GCP(tmp.GCPX, tmp.GCPY, tmp.GCPZ, tmp.GCPPixel // 5, tmp.GCPLine // 5) for tmp in gcp]

    # set metadata
    ds.SetGCPs(newgcp, gcpproj)
    ds.SetMetadata(metadata)
    return True


def toEPSG4326(path):
    """
    Change GEOTIFF image path='folder/abc.tif' to 4326 GEOTIFF 'folder/abc_4326.tif'
    """
    dest_path = make_dest_path(path, '_4326.tif')
    if not os.path.exists(dest_path):
        cmd = 'gdalwarp -t_srs EPSG:4326 -dstnodata 0 {0} {1}'.format(path, dest_path)
        os.system(cmd)
    return dest_path


def toCOG(path):
    """
    GEOTIFF path='folder/abc.tif' to CLOUD OPTIMIZED GEOTIFF 'folder/abc_cog.tif'
    """
    dest_path = make_dest_path(path, '_cog.tif')
    if not os.path.exists(dest_path):
        create_cog(path, dest_path, compress='LZW')
    return dest_path


def sentinel_2_process(path_tif):
    # processe image
    path_COG = make_dest_path(path_tif, '_4326_cog.tif')
    if not os.path.exists(path_COG):
        path_4326 = toEPSG4326(path_tif)
        path_COG = toCOG(path_4326)
        if os.path.exists(path_tif):
            os.remove(path_tif)
        for path_4326__ in glob(path_4326 + '*'):
            if os.path.exists(path_4326__):
                os.remove(path_4326__)
    return path_COG


def sentinel_1_process(zip_path, gpt, graph):
    path_COG = make_dest_path(zip_path, '_4326_cog.tif')
    if not os.path.exists(path_COG):
        tif_path = process_by_snap(zip_path, gpt, graph)
        set_metadata(zip_path, tif_path)
        path_4326 = toEPSG4326(tif_path)
        path_COG = toCOG(path_4326)
        if os.path.exists(tif_path):
            os.remove(tif_path)
        for path_4326__ in glob(path_4326 + '*'):
            if os.path.exists(path_4326__):
                os.remove(path_4326__)
    return path_COG


def main():
    # a = sentinel_2_process(path_tif, imageid)
    a = sentinel_1_process(sentinel_1_path, gpt_path, graph)
    print(a)


if __name__ == "__main__":
    path_tif = "/home/dung/Downloads/sentinel_2/S2A_MSIL2A_20191213T034141_N0213_R061_T47PQS_20191213T070657.tif"
    imageid = 'S2A_MSIL2A_20191213T034141_N0213_R061_T47PQS_20191213T070657'
    sentinel_1_path = "/home/dung/Desktop/S1A_IW_GRDH_1SDV_20200203T223350_20200203T223417_031094_0392B9_2C8E.zip"
    gpt_path = "/home/dung/Datacube/snap/bin/gpt"
    graph = "/home/dung/Datacube/my_datacube_package/sentinel/graph_mlc_50m.xml"
    main()