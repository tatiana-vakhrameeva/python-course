import unittest
from src.log_analyzer import is_gzip_file, get_log_records


class TestLogAnalyzer(unittest.TestCase):
    def test_is_gzip_file_recognize_gz(self):
        file = "somefile.gz"
        res = is_gzip_file(file)
        self.assertTrue(res)

    def test_is_gzip_file_recognize_not_gz(self):
        file = "somefile.tar"
        res = is_gzip_file(file)
        self.assertFalse(res)

    def test_get_log_recors_return_recors_correctly(self):
        log_path = "tests/data/logs/nginx-access-ui.log-20180320.gz"
        res = get_log_records(log_path)
        self.assertEqual(len(res), 6)

    def test_get_log_recors_raise_error_when_errors_limit_reached(self):
        log_path = "tests/data/logs/nginx-access-ui.log-20180321.gz"
        errors_limit = 0.1
        with self.assertRaises(RuntimeError):
            get_log_records(log_path, errors_limit)

    def test_get_log_recors_return_recors_correctly_when_errors(self):
        log_path = "tests/data/logs/nginx-access-ui.log-20180321.gz"
        errors_limit = 0.5
        res = get_log_records(log_path, errors_limit)
        self.assertEqual(len(res), 4)
