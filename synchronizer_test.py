import os
import shutil
import subprocess
from unittest import TestCase

from synchronizer import Synchronizer


class TestSynchronizer(TestCase):

    def __init__(self, *args):
        super(TestSynchronizer, self).__init__(*args)
        self._rcloneCommand = 'rclone'

    @classmethod
    def setUpClass(cls) -> None:
        shutil.rmtree('test', ignore_errors=True, onerror=None)
        os.makedirs('test/root1')
        os.makedirs('test/root2')

    @staticmethod
    def getRoot1():
        return 'test/root1'

    @staticmethod
    def getRoot2():
        return 'test/root2'

    @staticmethod
    def createTextFile(root, path, content):
        with open(root + '/' + path, 'w') as f:
            f.write(content)

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
        self.prepareRoots('fixtures/isSynced/synced')
        self.assertTrue(self.getSynchronizer().isSynced())

    def testIsSyncedFalse(self):
        self.prepareRoots('fixtures/isSynced/notSynced')
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
