import json
import subprocess


class Synchronizer:

    def __init__(self, root1, root2, rcloneCommand='rclone'):
        self._root1 = root1
        self._root2 = root2
        self._rcloneCommand = rcloneCommand

    def isSynced(self):
        synced = subprocess.call([
            self._rcloneCommand,
            'check', self._root1,
            self._root2
        ])
        return synced == 0

    def synchronize(self):
        list1 = self._getFileList(self._root1)
        list2 = self._getFileList(self._root2)
        self._copyMissingFiles(list1, list2, self._root1, self._root2)
        self._copyMissingFiles(list2, list1, self._root2, self._root1)

    def _copyMissingFiles(self, list1, list2, fromRoot, toRoot):
        for path in list1:
            if list2.get(path) == None:
                self._copyFile(path, fromRoot, toRoot)

    def _copyFile(self, path, fromRoot, toRoot):
        arguments = [
            self._rcloneCommand,
            'copy',
            fromRoot + '/' + path,
            toRoot
        ]
        p = subprocess.call(arguments)
        if p != 0:
            raise Exception(f'Could not copy file {path} from {fromRoot} to {toRoot}')

    def _getFileList(self, root):
        arguments = [
            self._rcloneCommand,
            'lsjson',
            '--hash',
            root
        ]
        p = subprocess.Popen(arguments + [], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        r = p.communicate()
        if p.returncode != 0:
            raise ('Could not list files on one of the remotes')

        list = json.loads(r[0])
        dict = {}
        for object in list:
            dict[object['Path']] = object

        return dict
