#!/usr/bin/env python3
from datetime import datetime

log_record = {
    'timestamp': '',
    'log_level': '',
    'msg_type': '',
    'data': ''
}

FIXED_FIELDS = ["DATE", "TIME", "LOG_LEVEL", "MSG_TYPE"]

def main():
    with open('audit_log_sample.log', 'r') as log_file:
        for line in log_file:
            record = line.split()
            log_fixed_fields = dict(zip(FIXED_FIELDS, record[:4]))
            data_dict = {}
            for data in record[4:]:
                key, _, value = data.partition('=')
                data_dict[key] = value
            log_record['timestamp'] = f"{log_fixed_fields['DATE']} {log_fixed_fields['TIME']}"
            log_record['log_level'] = f"{log_fixed_fields['LOG_LEVEL']}"
            log_record['msg_type'] = f"{log_fixed_fields['MSG_TYPE']}"
            log_record['data'] = data_dict
            print(log_record)
if __name__ == "__main__":
    main()