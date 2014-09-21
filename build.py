import sys
import os
import urllib2

if __name__ == '__main__':
    version_info = lambda v: map(lambda x: int(x), v.split('.'))

    # if the user provided an argument and it's a file, use that.
    try:
        source_filepath = sys.argv[1]
    except IndexError:
        source_filepath = ''

    if os.path.exists(source_filepath):
        print 'Building from source archive %s' % source_filepath
        local_gzip = source_filepath
    else:
        gdal_version = '1.11.0'
        # parse out the version info
        major, minor, release = version_info(gdal_version)


        gdal_download_uri = 'http://download.osgeo.org/gdal/'
        if minor >= 10:
            gdal_download_uri += gdal_version + '/'

        local_gzip = 'gdal-%s.tar.gz' % gdal_version
        gdal_download_uri += local_gzip
        print gdal_download_uri

        print 'downloading ...'
        u = urllib2.urlopen(gdal_download_uri)
        localFile = open(local_gzip, 'w')
        localFile.write(u.read())
        localFile.close()

