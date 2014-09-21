import urllib2

if __name__ == '__main__':
    gdal_version = '1.11.0'
    # parse out the version info
    major, minor, release = map(lambda x: int(x), gdal_version.split('.'))

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

