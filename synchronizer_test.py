import os
import shutil
import subprocess
import unittest
from unittest import TestCase

from synchronizer import Synchronizer


class TestSynchronizer(TestCase):

    def __init__(self, *args):
        super(TestSynchronizer, self).__init__(*args)
        self._rcloneCommand = 'rclone'

    @classmethod
    def setUpClass(cls) -> None:
        shutil.rmtree('test', ignore_errors=True, onerror=None)
        os.makedirs(TestSynchronizer.getRoot1())
        os.makedirs(TestSynchronizer.getRoot2())

    @staticmethod
    def getRoot1():
        return 'test/root1'

    @staticmethod
    def getRoot2():
        return 'test/root2'

    def createTextFile(self, root, path, content):
        with open(f'{root}/{path}', 'w') as f:
            f.write(content)

    def createFolder(self, root, path):
        os.mkdir(f'{root}/{path}')

    def getSynchronizer(self):
        return Synchronizer(self.getRoot1(), self.getRoot2(), self._rcloneCommand)

    def check(self, fixture):
        synchronizer = self.getSynchronizer()
        self.assertTrue(synchronizer.isSynced())
        self.assertTrue(Synchronizer(fixture + '/expected/', self.getRoot1()).isSynced())
        self.assertTrue(Synchronizer(fixture + '/expected/', self.getRoot2()).isSynced())

    def prepareRoots(self, fixture):
        # Assert that the return code is 0, to make sure that there are no errors while preparing the test cases
        self.assertEqual(subprocess.call([self._rcloneCommand, 'sync', fixture + '/root1/', self.getRoot1()]), 0)
        self.assertEqual(subprocess.call([self._rcloneCommand, 'sync', fixture + '/root2/', self.getRoot2()]), 0)

    def testIsSyncedTrue(self):
        """If everything is in sync isSynced() returns true"""
        self.prepareRoots('fixtures/isSynced/synced')
        self.assertTrue(self.getSynchronizer().isSynced())

    def testUnsyncedFile(self):
        """If there is an unsynced file isSynced() returns false"""
        self.prepareRoots('fixtures/isSynced/notSynced')
        self.assertFalse(self.getSynchronizer().isSynced())

    @unittest.skip("Not directly supported by rclone, but we can live with that limitation for now")
    def testUnsyncedEmptyFolder(self):
        """If there is an unsynced empty folder isSynced() returns false"""
        try:
            os.makedirs('ixtures/isSynced/notSyncedEmptyFolder/root2/newFolder')
        except(FileExistsError):
            pass
        self.prepareRoots('fixtures/isSynced/notSyncedEmptyFolder')
        self.assertFalse(self.getSynchronizer().isSynced())

    def testNewFileInRoot1(self):
        self.prepareRoots('fixtures/newFileInRoot1')
        self.getSynchronizer().synchronize()
        self.createTextFile(self.getRoot1(), 'newFile.txt', 'newFile')
        self.getSynchronizer().synchronize()
        self.check('fixtures/newFileInRoot1')

    def testNewFileInRoot2(self):
        self.prepareRoots('fixtures/newFileInRoot2')
        self.getSynchronizer().synchronize()
        self.createTextFile(self.getRoot2(), 'newFile.txt', 'newFile')
        self.getSynchronizer().synchronize()
        self.check('fixtures/newFileInRoot2')

    @unittest.skip("Not directly supported by rclone, but we can live with that limitation for now")
    def testNewFolderInRoot1(self):
        """If there is an empty folder in root1, it should be synchronized"""
        try:
            os.makedirs('fixtures/newFolderInRoot1/root1/newFolder')
        except(FileExistsError):
            pass
        try:
            os.makedirs('fixtures/newFolderInRoot1/expected/newFolder')
        except(FileExistsError):
            pass
        self.prepareRoots(('fixtures/newFolderInRoot1'))
        self.getSynchronizer().synchronize()
        self.createFolder(self.getRoot1(), 'newFolder')
        self.getSynchronizer().synchronize()
        self.check('fixtures/newFolderInRoot1')
        self.assertTrue(os.path.isdir('test/newFolderInRoot1/root2/newFolder'))

    @unittest.skip("Not directly supported by rclone, but we can live with that limitation for now")
    def testNewFolderInRoot2(self):
        """If there is an empty folder in root1, it should be synchronized"""
        try:
            os.makedirs('fixtures/newFolderInRoot2/root2/newFolder')
        except(FileExistsError):
            pass
        try:
            os.makedirs('fixtures/newFolderInRoot2/expected/newFolder')
        except(FileExistsError):
            pass
        self.prepareRoots(('fixtures/newFolderInRoot2'))
        self.getSynchronizer().synchronize()
        self.createFolder(self.getRoot2(), 'newFolder')
        self.getSynchronizer().synchronize()
        self.check('fixtures/newFolderInRoot2')
        self.assertTrue(os.path.isdir('test/newFolderInRoot2/root1/newFolder'))

    # TODO Use cases to be implemented
    #  - A file changes on one side
    #  - A file changes on both sides (conflict resolution)
    #  - A file is deleted on one side
    #  - A folder is deleted on one side
    #  - A file is deleted on both sides
    #  - A folder is deleted on both sides
    #  - Block, if watermark for too many deletes is exceeded
    #  - Run tests against google drive
    #  - How to handle Google Docs files?
    #  - How to handle Links in google drive?