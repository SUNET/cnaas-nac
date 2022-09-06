import csv
import io
import re

from flask import request

fields = [
    "username",
    "nas_identifier",
    "nas_port_id",
    "nas_ip_address",
    "calling_station_id",
    "called_station_id",
    "comment",
    "authdate",
    "vlan"
]


def limit_results() -> int:
    """Find number of results to limit query to, either by user requested
    param or a default value."""
    limit = 10

    args = request.args
    if 'limit' in args:
        try:
            r_limit = int(args['limit'])
            limit = max(1, min(100, r_limit))
        except Exception:
            pass

    return limit


def build_filter(f_class, query):
    args = request.args
    if 'filter' not in args:
        return query
    split = args['filter'].split(',')
    if not len(split) == 2:
        # invalid
        return query
    attribute, value = split
    if attribute not in f_class.__table__._columns.keys():
        # invalid
        return query
    kwargs = {attribute: value}
    return query.filter_by(**kwargs)


def empty_result(status='success', data=None):
    if status == 'success':
        return {
            'status': status,
            'data': data
        }
    elif status == 'error':
        return {
            'status': status,
            'message': data if data else "Unknown error"
        }


def csv_to_json(text):
    json_data = []

    for line in text.split("\n"):
        res_line = re.sub(r",\s", ",", line)
        csv_fields = res_line.split(",")

        if len(csv_fields) != 11:
            raise ValueError("Invalid number of fields in CSV, should be 11.")

        tmp_dict = {
            "username": csv_fields[0],
            "password": csv_fields[1],
            "active": csv_fields[2],
            "vlan": csv_fields[3],
            "nas_identifier": csv_fields[4],
            "nas_port_id": csv_fields[5],
            "nas_ip_address": csv_fields[6],
            "calling_station_id": csv_fields[7],
            "called_station_id": csv_fields[8],
            "access_start": csv_fields[9],
            "access_stop": csv_fields[10],
        }

        json_data.append(tmp_dict)

    return json_data


def csv_export(users):
    headers = {}
    content = io.StringIO()
    data = csv.DictWriter(content, users[0].keys())

    for k, v in users[0].items():
        headers[k] = k

    data.writerow(headers)
    data.writerows(users)

    return content.getvalue()
