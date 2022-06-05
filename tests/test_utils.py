import unittest
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from server.pbkdf2 import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        password = "123"
        hsh = hash_password(password)
        ver = verify_password(hsh, password)
        self.assertEqual(ver, True)


if __name__ == '__main__':
    unittest.main()
