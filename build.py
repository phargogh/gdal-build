import sys
import tarfile
import os
import urllib2
import time
import shutil
import subprocess
import zipfile
import zlib
import platform

def _download_archive(url):
    out_file = os.path.basename(url)
    u = urllib2.urlopen(url)
    local_file = open(out_file, 'wb')
    local_file.write(u.read())
    local_file.close()

def download_geos(version):
    # parse out the version info
    major, minor, release = version_info(version)
    geos_download_uri = 'http://download.osgeo.org/geos/'
    if minor >= 10:
        geos_download_uri += version = '/'

    local_gzip = 'geos=%s.tar.bz2' % version
    geos_download_uri += local_gzip
    _download_archive(geos_download_uri)

def download_gdal(version, fmt='gz'):
    """Download the approprate version of the GDAL source from the official
    download mirror.

    version - the version of GDAL to download.  Must be a string in the form
        1.1.1
    fmt - the archive format to download.  One of 'gz'|'zip'

    Returns the absolute path to the downloaded tar.gz file."""

    # parse out the version info
    major, minor, release = version_info(version)

    gdal_download_uri = 'http://download.osgeo.org/gdal/'
    if minor >= 10:
        gdal_download_uri += version + '/'

    if fmt == 'gz':
        local_gzip = 'gdal-%s.tar.gz' % version
    elif fmt == 'zip':
        local_gzip = 'gdal%s.zip' % version.replace('.', '')
    else:
        raise Exception('format %s not recognized!' % fmt)
    gdal_download_uri += local_gzip
    print gdal_download_uri

    print 'downloading ...'
    _download_archive(gdal_download_uri)

    return os.path.abspath(local_gzip)

def set_gdal_home(filepath):
    tmp_out_filepath = os.path.join(os.getcwd(), 'tmp_%s' %
        os.path.basename(filepath))
    new_out_file = open(tmp_out_filepath, 'w')
    new_gdal_home = os.path.join(os.path.dirname(__file__), 'build')
    with open(filepath, 'r') as old_file:
        for line in old_file:
            if line.startswith('GDAL_HOME'):
                new_out_file.write('GDAL_HOME = "%s"\n' % new_gdal_home)
            elif line.startswith('PYDIR'):
                new_out_file.write('PYDIR = "%s"\n' %
                    os.path.dirname(sys.executable))
            else:
                new_out_file.write(line)

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

    try:
        print 'extracting', local_gzip
        tfile = tarfile.open(local_gzip, 'r:gz')
        tfile.extractall('.')
    except zlib.error:
        # happens when gzip is corrupt.
        # in this case, get the zipfile instead
        print 'gzip extraction failed.  Trying zipfile'
        local_zip = download_gdal(gdal_version, 'zip')
        with open(local_zip, 'rb') as MyZip:
              print(MyZip.read(4))

        zip = zipfile.ZipFile(local_zip)
        zip.extractall('.')

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
