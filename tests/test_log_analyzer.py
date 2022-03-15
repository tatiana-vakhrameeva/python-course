import unittest
from src.log_analyzer import is_gzip_file


class TestLogAnalyzer(unittest.TestCase):
    def test_is_gzip_file_recognize_gz(self):
        file = "somefile.gz"
        res = is_gzip_file(file)
        self.assertTrue(res)

    def test_is_gzip_file_recognize_not_gz(self):
        file = "somefile.tar"
        res = is_gzip_file(file)
        self.assertFalse(res)

    # def test_get_log_recors_works_until_error_limits_not_reached(self):
    #     log_path = 'path/to/log'
    #     errors_limit = 2
    #     res = get_log_records(log_path, errors_limit)
