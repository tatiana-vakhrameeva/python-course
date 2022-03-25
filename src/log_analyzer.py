import os
import logging
import json
import re
import gzip
import argparse
import io
from datetime import datetime
from collections import defaultdict
from string import Template
import statistics


LOG_RECORD_RE = re.compile(
    r"^"
    r"\S+ "  # remote_addr
    r"\S+\s+"  # remote_user (note: ends with double space)
    r"\S+ "  # http_x_real_ip
    r"\[\S+ \S+\] "  # time_local [datetime tz] i.e. [29/Jun/2017:10:46:03 +0300]
    r'"\S+ (?P<href>\S+) \S+" '  # request "method href proto" i.e. "GET /api/v2/banner/23815685 HTTP/1.1"
    r"\d+ "  # status
    r"\d+ "  # body_bytes_sent
    r'"\S+" '  # http_referer
    r'".*" '  # http_user_agent
    r'"\S+" '  # http_x_forwarded_for
    r'"\S+" '  # http_X_REQUEST_ID
    r'"\S+" '  # http_X_RB_USER
    r"(?P<time>\d+\.\d+)"  # request_time
)

config = {
    "REPORT_DIR": "reports",
    "LOG_DIR": "nginx_logs",
    "LOG_FILE": "logs/analyzer_logs.txt",
    "ERRORS_LIMIT": 1000,
    "MAX_REPORT_SIZE": 10000,
    "REPORT_TEMPLATE_PATH": "templates",
}

DEFAULT_CONFIG_PATH = "conf/config.json"


def load_conf(conf_path):
    with open(conf_path, "rb") as conf_file:
        conf = json.load(conf_file)
    return conf


####################################
# Analyzing
####################################


def create_report(records, max_records):
    total_records = 0
    total_time = 0
    report_lines = []
    urls_info = defaultdict(list)

    for href, response_time in records:
        total_records += 1
        total_time += response_time

        urls_info[href].append(response_time)

        if total_records == max_records:
            break

    for key, value in urls_info.items():
        count = len(value)
        time_sum = sum(value)
        report_line = {
            "href": key,
            "count": count,
            "count_perc": 100 * float(count) / float(len(urls_info.items())),
            "time_sum": time_sum,
            "time_perc": 100 * float(time_sum) / float(total_time),
            "time_avg": statistics.mean(value),
            "time_max": max(value),
            "time_med": statistics.median(value),
        }

        report_lines.append(report_line)

    return report_lines


def get_log_records(log_path, parse_log_record, errors_limit=None):
    open_fn = gzip.open if is_gzip_file(log_path) else io.open
    errors = 0
    records = []
    with open_fn(log_path, mode="rb") as log_file:
        for line in log_file:
            line = line.decode("utf-8")

            parsed_line = parse_log_record(line)
            if parsed_line is None:
                errors += 1
                continue

            records.append(parsed_line)

    records_count = len(records)

    if (
        errors_limit is not None
        and records_count > 0
        and errors / float(records_count) > errors_limit
    ):
        raise RuntimeError("Errors limit exceeded")

    return records


def parse_log_record(log_line):
    search = re.search(LOG_RECORD_RE, log_line)

    if not search:
        return None

    href = search.group(1)
    request_time = float(search.group(2))

    return href, request_time


####################################
# Utils
####################################


def setup_logger(log_path):
    if log_path is not None:
        log_dir = os.path.split(log_path)[0]
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )


def get_latest_log_info(files_dir):
    if not os.path.isdir(files_dir):
        return None

    latest_file_info = {"file_date": 0, "name": None}

    for filename in os.listdir(files_dir):
        match = re.match(r"^nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$", filename)
        if not match:
            continue

        file_date = re.search(r"(?P<date>\d{8})", filename).group(0)
        if int(file_date) > int(latest_file_info["file_date"]):
            latest_file_info["file_date"] = file_date
            latest_file_info["name"] = filename

    if latest_file_info["name"]:
        return latest_file_info

    return None


def is_gzip_file(file_path):
    return file_path.split(".")[-1] == "gz"


def render_template(template_path, to, data):
    if data is None:
        data = []

    template_file_path = os.path.join(template_path, "report.html")
    with open(template_file_path) as template_file:
        template = Template(template_file.read())

    report = template.safe_substitute(table_json=json.dumps(data))
    with open(to, "w") as report_file:
        report_file.write(report)


def main(config):
    latest_log_info = get_latest_log_info(config.get("LOG_DIR"))

    if not latest_log_info:
        logging.info("Ooops. No log files yet")
        return

    report_date_string = datetime.strptime(
        latest_log_info["file_date"], "%Y%m%d"
    ).strftime("%Y.%m.%d")

    report_filename = "report-{}.html".format(report_date_string)
    report_file_path = os.path.join(config["REPORT_DIR"], report_filename)

    if os.path.isfile(report_file_path):
        logging.info("Looks like everything is up-to-date")
        return

    latest_log_path = os.path.join(config["LOG_DIR"], latest_log_info["name"])

    logging.info('Collecting data from "{}"'.format(os.path.normpath(latest_log_path)))

    log_records = get_log_records(
        latest_log_path, parse_log_record, config.get("ERRORS_LIMIT")
    )

    report_data = create_report(log_records, config["MAX_REPORT_SIZE"])

    render_template(config.get("REPORT_TEMPLATE_PATH"), report_file_path, report_data)

    logging.info("Report saved to {}".format(os.path.normpath(report_file_path)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", help="Config file path", default=DEFAULT_CONFIG_PATH
    )
    args = parser.parse_args()

    args_config = load_conf(args.config)
    config.update(args_config)

    setup_logger(config.get("LOG_FILE", None))

    try:
        main(config)
    except Exception as e:
        logging.exception(msg=e)
