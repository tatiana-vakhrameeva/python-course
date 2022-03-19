import unittest
from src.log_analyzer import is_gzip_file, get_log_records, parse_log_record


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

    def test_parse_log_record(self):
        log = '1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704'  # noqa: E501
        parsed_log = parse_log_record(log)
        self.assertEqual(parsed_log, ("/api/v2/slot/4705/groups", 0.704))

    def test_parse_log_record_when_wrong_format(self):
        log = '1200 2613 "516057-4708-9752745" "2a828197ae235b0b3cb" '
        parsed_log = parse_log_record(log)
        self.assertEqual(parsed_log, None)
