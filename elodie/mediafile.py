import threading
import os
from .compatability import _decode

from .media.media import Media
from .media.base import get_all_subclasses
from . import log
from send2trash import send2trash


class MediaFile(threading.Thread):

    def __init__(self, file_path, filesystem, parameters, semaphore=None):
        super(MediaFile, self).__init__()
        if os.path.exists(file_path):
            self._file_path = _decode(file_path)
        else:
            raise Exception('Could not find %s' % file_path)

        self.filesystem = filesystem
        self.parameters = parameters
        self.semaphore = semaphore

    def run(self):
        return_object = self.import_file(**self.parameters)
        if (self.semaphore):
            self.semaphore.release()
        return return_object

    def import_file(
            self, destination, album_from_folder, trash, allow_duplicates):
        """Set file metadata and move it to destination.
        """

        destination = _decode(destination)

        # Check if the source, _file_path, is a child folder within destination
        if destination.startswith(os.path.abspath(
                os.path.dirname(self._file_path))+os.sep):
            log.all('{"source": "%s", "destination": "%s", "error_msg": "Source cannot be in destination"}' % (
                self._file_path, destination))
            return

        media = Media.get_class_by_file(self._file_path, get_all_subclasses())
        if not media:
            log.warn('Not a supported file (%s)' % self._file_path)
            log.all('{"source":"%s", "error_msg":"Not a supported file"}' % self._file_path)
            return

        if album_from_folder:
            media.set_album_from_folder()

        dest_path = self.filesystem.process_file(
            self._file_path, destination,
            media, allowDuplicate=allow_duplicates, move=False)
        if dest_path:
            log.all('%s -> %s' % (self._file_path, dest_path))
        if trash:
            send2trash(self._file_path)

        return dest_path or None
