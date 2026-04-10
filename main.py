#!/usr/bin/env python3
from datetime import datetime
from enum import Enum
# Things to do:
# 1) Design a clean internal model.
#     Normalize timestamps (timezone-aware) -- Don't know how to do that since we don't know the orig tz)
#     Enforce valid statuses (SUCCESS, FAILED, etc.)
#     Gracefully handle bad data
# 2) Parse each line into structured data
#     Need to Handle:
#       Missing fields
#       Malformed lines
#       Unexpected formats
log_rec = {
    'timestamp': '',
    'log_level': '',
    'event': '',
    'data': ''
}

class Statuses(Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

class log_record():
    def __init__(self, log_line):
        self.raw_line = log_line.strip()
        self.valid_statuses = Statuses
        self.format_data()

    def format_data(self):
        parts = self.raw_line.split()
        if len(parts) < 5:
            raise TypeError("Not enough fields")
        
        date_str = parts[0]
        time_str = parts[1]
        try:
            timestamp = datetime.strptime(
                f"{date_str} {time_str}",
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            raise ValueError(f"Invalid timestamp: {date_str} {time_str}")
        
        try:
            status = Statuses(parts[2])
        except ValueError:
            raise ValueError(f"Invalid log status: {parts[2]}")

        
def main():
    FIXED_FIELDS = ["DATE", "TIME", "LOG_LEVEL", "EVENT"]
    with open('audit_log_sample.log', 'r') as log_file:
        for line in log_file:
            record = log_record(line)
            # record = line.split()
            # log_fixed_fields = dict(zip(FIXED_FIELDS, record[:4]))
            # data_dict = {}
            # for data in record[4:]:
            #     key, _, value = data.partition('=')
            #     data_dict[key] = value
            # record = log_record({
            #     'timestamp': f"{log_fixed_fields['DATE']} {log_fixed_fields['TIME']}",
            #     'log_level': f"{log_fixed_fields['LOG_LEVEL']}",
            #     'event': f"{log_fixed_fields['EVENT']}",
            #     'data': data_dict
            # })

if __name__ == "__main__":
    main()