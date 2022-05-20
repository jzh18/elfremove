import os, sys
import subprocess
import unittest

sys.path[0:0] = ['.']

def main():
    subprocess.call(['make', '-C', 'test/test_files'])

    tests = unittest.TestLoader().discover('test', 'test*.py', 'test')
    result = unittest.TextTestRunner().run(tests)

    subprocess.call(['make', '-C', 'test/test_files', 'clean'])

    if result.wasSuccessful():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
