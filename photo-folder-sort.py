import datetime
import logging
import os
import sys

import pyexiv2

logging.basicConfig()
logging.setLevel(logging.WARNING)


def rget(mapping_object, keys, default=None):
    """Return the value from a dict-like object for the first valid key in the
    given seqence of keys, or else a default value if none of the keys is set.

    :param mapping_object: A dict-like object (must have a .get() method)
    :param keys: A sequence of keys to try in order
    :param default: The default value to return, if none of the keys is present
    """
    next = rget(mapping_object, keys[1:]) if len(keys) > 1 else default
    return mapping_object.get(keys[0], next)


def get_photo_metadata(filepath):
    """Return the ImageMetadata object for a given filepath.  Return False if
    the filepath does not exist or is not an image file.
    """
    meta = pyexiv2.ImageMetadata(filepath)
    try:
        meta.read()
    except IOError:
        return False
    return meta


def get_photo_timestamp(filepath):
    """Return the timestamp on which a given photo was taken."""
    meta = get_photo_metadata(filepath)

    tags = [
        'Xmp.exif.DateTimeOriginal',
        'Exif.Photo.DateTimeOriginal',
    ]

    if meta:
        return getattr(rget(meta, tags), 'value', None)


def set_folder_dates_to_median(path):
        logging.info('Setting timestamps for {0}'.format(path))

        dirpath, dirnames, filenames = os.walk(path).next()

        timestamps = [get_photo_timestamp(os.path.join(dirpath, fname)) for fname in filenames]
        timestamps = sorted([tstamp.replace(tzinfo=None) for tstamp in timestamps if tstamp])

        if timestamps:

            median_timestamp = timestamps[int(len(timestamps)/2)]

            """Generate integers (number of seconds since epoch) to represent
            the Accessed and Modified timestamps, to be set for this folder.
            """
            epoch = datetime.datetime.utcfromtimestamp(0)
            atime = (datetime.datetime.today() - epoch).total_seconds()
            mtime = (median_timestamp - epoch).total_seconds()

            os.utim(path, (atime, mtime))
            loggingdebug("Set Accessed time for {0} to {1}".format(path, atime))
            logging.debug("Set Modified time for {0} to {1}".format(path, mtime))

        else:            logging.warning("No valid timestamps found for {0}".format(path))


if __name__ == '__main__':

    for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
        set_folder_dates_to_median(dirpath)
