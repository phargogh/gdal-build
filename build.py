import sys
import tarfile
import os
import urllib2
import time
import shutil
import subprocess

def download_gdal(version):
    """Download the approprate version of the GDAL source from the official
    download mirror.

    version - the version of GDAL to download.  Must be a string in the form
        1.1.1

    Returns the absolute path to the downloaded tar.gz file."""

    # parse out the version info
    major, minor, release = version_info(version)

    gdal_download_uri = 'http://download.osgeo.org/gdal/'
    if minor >= 10:
        gdal_download_uri += version + '/'

    local_gzip = 'gdal-%s.tar.gz' % version
    gdal_download_uri += local_gzip
    print gdal_download_uri

    print 'downloading ...'
    u = urllib2.urlopen(gdal_download_uri)
    localFile = open(local_gzip, 'w')
    localFile.write(u.read())
    localFile.close()

    return os.path.abspath(local_gzip)


if __name__ == '__main__':
    start_time = time.time()
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
        gdal_version = '1.11.1'
        local_gzip = download_gdal(gdal_version)

    gdal_dir = local_gzip.replace('.tar.gz', '')
    if os.path.exists(gdal_dir):
        print 'removing %s' % gdal_dir
        shutil.rmtree(gdal_dir)

    print 'extracting', local_gzip
    tfile = tarfile.open(local_gzip, 'r:gz')
    tfile.extractall('.')

    os.chdir(gdal_dir)
    if platform.system() == 'Windows':
        # set the GDAL_HOME folder to something sensible, like the project dir
        set_gdal_home(os.path.abspath('nmake.opt'))
        subprocess.call('nmake /f makefile.vc')
        os.chdir('swig\\python')
        subprocess.call('python setup.py build bdist_wininst', shell=True)
        subprocess.call('python setup.py build bdist_wheel', shell=True)
    else:
        subprocess.call('./autogen.sh', shell=True)
        subprocess.call('./configure --with-python', shell=True)
        subprocess.call('make', shell=True)

    end_time = time.time()
    print 'All operations took %ss' % ((end_time - start_time))
