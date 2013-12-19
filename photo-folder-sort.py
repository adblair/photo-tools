import datetime
import os
import sys
import pprint

import pyexiv2

class Photo(object):
    
    def __init__(self, path):
        """Raises IOError if a valid image path isn't given"""
        self.path = path
        self.name = os.path.basename(path)
        self.meta = pyexiv2.metadata.ImageMetadata(path)
        self.meta.read()
        # print self.path, self.datetime
        if self.name == 'berlin 2002 - 06.jpg':
            pprint.pprint(self.meta.keys())
            print self.meta.get('Exif.Image.ExifTag')
            print self.meta.get('Exif.Image.DateTime') #Not the right one (there doesn't seem to be one!!)
            print self.meta.get('Exif.Image.DateTimeOriginal')


    @property
    def datetime(self):
        timestamp = getattr(self.meta.get('Exif.Image.DateTimeOriginal'), 'value', None)
        return timestamp if isinstance(timestamp, datetime.datetime) else None


class PhotoDirectory(list):

    def __init__(self, path):
        self.path = path
        self.extend(self.load_photos(path))

    def load_photos(self, path):
        dirpath, dirnames, filenames = os.walk(path).next()
        for filename in filenames:
            try:
                yield Photo(os.path.join(dirpath, filename))
            except IOError:
                pass

    def set_modified_timestamp_to_median_photo_timestamp(self):
        dates = sorted([img.datetime for img in self if img.datetime is not None])
        if dates:
            median_timestamp = dates[int(len(dates)/2)]
            epoch = datetime.datetime.utcfromtimestamp(0)
            atime = (datetime.datetime.today() - epoch).total_seconds()
            mtime = (median_timestamp - epoch).total_seconds()
            os.utime(self.path, (atime, mtime))

def set_all_dirs(path):
    for dirpath, dirnames, filenames in os.walk(path):
        PhotoDirectory(dirpath).set_modified_timestamp_to_median_photo_timestamp()


if __name__ == "__main__":

    set_all_dirs(sys.argv[1])
