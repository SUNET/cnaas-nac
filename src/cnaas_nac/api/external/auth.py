import csv
import io
import json
import os
import time
from datetime import datetime

from cnaas_nac.api.external.coa import CoA
from cnaas_nac.api.generic import csv_to_json, empty_result
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.reply import Reply
from cnaas_nac.db.user import User, UserInfo, get_users
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource
from netaddr import EUI, mac_unix_expanded

logger = get_logger()


api = Namespace("auth", description="Authentication API",
                prefix="/api/{}".format(__api_version__))


class AuthApi(Resource):
    @jwt_required()
    def get(self):
        """
        Get a JSON blob with all users, replies and other information.
        """
        field = None
        condition = ""
        direction = "username"
        when = None
        client_type = None

        response = None
        user_count = 0
        csv_file = False

        headers = dict()

        for arg in request.args:
            if "filter" in arg:
                field = arg[arg.find("[")+1: arg.find("]")]
                condition = request.args[arg].split("?")[0]
            if "sort" in arg:
                direction = request.args[arg]
            if "when" in arg:
                when = request.args[arg]
            if "type" in arg:
                client_type = request.args[arg]
            if "file" in arg:
                csv_file = True

        users = get_users(field=field, condition=condition,
                          order=direction, when=when, client_type=client_type)
        user_count = len(users)

        if "Content-Type" in request.headers:
            if request.headers["Content-Type"] in ("application/csv", "text/csv"):
                content = io.StringIO()
                data = csv.DictWriter(content, users[0].keys())

                for k, v in users[0].items():
                    headers[k] = k

                data.writerow(headers)
                data.writerows(users)

                response = make_response(content.getvalue())
                response.headers["Content-type"] = request.headers["Content-Type"]

                if csv_file:
                    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

        if not response:
            response = make_response(jsonify(empty_result(status="success",
                                                          data=users)), 200)
            response.headers["Content-Type"] = "application/json"

        response.headers["X-Total-Count"] = user_count

        return response

    @jwt_required()
    def post(self):
        """
        Add a user manually.
        """

        users = list()
        errors = []

        if "RADIUS_SLAVE" in os.environ:
            if os.environ["RADIUS_SLAVE"] == "yes":
                return empty_result(status="error",
                                    data="Users can only be added to master server."), 400

        if "Content-Type" in request.headers and request.headers["Content-Type"] in ("application/csv", "text/csv"):
            try:
                json_request = csv_to_json(request.data.decode())
            except ValueError as e:
                return empty_result(status="error",
                                    data=str(e)), 400
        else:
            if isinstance(request.get_json(), list):
                json_request = request.get_json()
            else:
                json_request = [request.get_json()]

        # First check if any of the users to be added already exists
        for json_data in json_request:
            if "username" not in json_data:
                errors.append("username is a required argument")

            try:
                username = str(EUI(
                    json_data["username"], dialect=mac_unix_expanded))
            except Exception:
                username = json_data["username"]

            if User.get(username) != []:
                errors.append(f"User {username} already exists")

            if Reply.get(username) != []:
                errors.append(f"Reply for {username} already exists")

            if UserInfo.get([username])[username] != {}:
                errors.append(f"UserInfo for {username} already exists")

            if NasPort.get(username) != None:
                errors.append(f"NasPort for {username} already exists")

            if "access_start" in json_data:
                try:
                    access_start = datetime.strptime(
                        json_data["access_start"], "%Y-%m-%d %H:%M")
                except ValueError as e:
                    errors.append(f"{username}: Invalid date and time format")
                    access_start = False
            else:
                access_start = None

            if "access_stop" in json_data:
                try:
                    access_stop = datetime.strptime(
                        json_data["access_stop"], "%Y-%m-%d %H:%M")
                except ValueError as e:
                    errors.append(f"{username}: Invalid date and time format.")
                    access_stop = False
            else:
                access_stop = None

            if access_start and access_stop:
                start_time = int(round(time.mktime(access_start.timetuple())))
                stop_time = int(round(time.mktime(access_stop.timetuple())))

                if start_time == stop_time:
                    errors.append(
                        f"{username}: Start time and stop time must not be identical.")

                if start_time > stop_time:
                    errors.append(
                        f"{username}: Start time must be before stop time.")

            if errors != []:
                return make_response(jsonify(empty_result(status="error", data=errors)), 400)

        for json_data in json_request:
            try:
                username = str(EUI(
                    json_data["username"], dialect=mac_unix_expanded))
            except Exception:
                username = json_data["username"]

            if "password" in json_data:
                try:
                    password = str(EUI(
                        json_data["password"], dialect=mac_unix_expanded))
                except Exception:
                    password = json_data["password"]
            else:
                password = username

            if "vlan" in json_data:
                vlan = json_data["vlan"]
            else:
                if "RADIUS_DEFAULT_VLAN" in os.environ:
                    vlan = os.environ["RADIUS_DEFAULT_VLAN"]
                else:
                    vlan = 13

            if "comment" in json_data:
                comment = json_data["comment"]
            else:
                comment = None

            if "nas_identifier" not in json_data:
                nas_identifier = None
            else:
                nas_identifier = json_data["nas_identifier"]

            if "nas_port_id" not in json_data:
                nas_port_id = None
            else:
                nas_port_id = json_data["nas_port_id"]

            if "nas_ip_address" not in json_data:
                nas_ip_address = None
            else:
                nas_ip_address = json_data["nas_ip_address"]

            if "calling_station_id" not in json_data:
                calling_station_id = None
            else:
                calling_station_id = json_data["calling_station_id"]

            if "called_station_id" not in json_data:
                called_station_id = None
            else:
                called_station_id = json_data["called_station_id"]

            if nas_identifier == "" or nas_identifier is None:
                nas_identifier = username

            err = User.add(username, password)

            if err != "":
                return empty_result(status="error", data=err), 400

            err = Reply.add(username, vlan)

            if err != "":
                return empty_result(status="error", data=err), 400

            err = UserInfo.add(username, comment=comment,
                               access_start=access_start,
                               access_stop=access_stop)

            if err != "":
                return empty_result(status="error", data=err), 400

            err = NasPort.add(username, nas_ip_address, nas_identifier,
                              nas_port_id,
                              calling_station_id,
                              called_station_id)

            if err != "":
                return empty_result(status="error", data=err), 400

            if "active" in json_data and isinstance(json_data["active"], bool):
                if json_data["active"]:
                    User.enable(username)

            user = get_users(field="username", condition=username)[0]
            users.append(user)

        response = make_response(jsonify(empty_result(status="success",
                                                      data=users)), 200)
        response.headers["X-Total-Count"] = len(users)

        return response


class AuthApiByName(Resource):
    @jwt_required()
    def get(self, username):
        """
        Return a JSON blob with all users, VLANs and other information.
        """

        users = get_users(field="username", condition=username)
        response = make_response(jsonify(empty_result(status="success",
                                                      data=users)), 200)

        response.headers["X-Total-Count"] = len(users)
        response.headers["Content-Type"] = "application/json"

        return response

    @jwt_required()
    def put(self, username):
        """
        Update user parameters such as VLAN, if the user is
        enabled/disabled and so on.
        """
        json_data = request.get_json()
        result = ""

        if json_data is None:
            return empty_result(status="error", data="No JSON input found"), 400

        if "password" in json_data:
            userdata = get_users(field="username", condition=username)
            if userdata == []:
                return empty_result(status="error", data="User not found")
            result = User.password(username, json_data["password"])
        if "active" in json_data:
            if json_data["active"] is True:
                result = User.enable(username)
            else:
                result = User.disable(username)
            UserInfo.add(username, reason="", auth=True)
        if "vlan" in json_data:
            result = Reply.vlan(username, json_data["vlan"])
        if "comment" in json_data:
            result = UserInfo.add(username, comment=json_data["comment"])
        if "bounce" in json_data and json_data["bounce"] is True:
            userdata = get_users(field="username", condition=username)
            if userdata == []:
                return empty_result(status="error", data="User not found")

            nas_ip_address = userdata[0]["nas_ip_address"]
            nas_port_id = userdata[0]["nas_port_id"]

            attrs = {
                "NAS-IP-Address": nas_ip_address,
                "NAS-Port-Id": nas_port_id,
                "Arista-PortFlap": "1"
            }

            if "RADIUS_COA_SECRET" not in os.environ:
                return empty_result(status="error", data="CoA secret not configured."), 400
            secret = str.encode(os.environ["RADIUS_COA_SECRET"])

            try:
                coa_request = CoA(nas_ip_address, secret)
                coa_request.send_packet(attrs=attrs)
            except Exception as e:
                result = str(e)

        if result != "":
            return empty_result(status="error", data=result), 400

        user = get_users(field="username", condition=username)
        response = make_response(jsonify(empty_result(status="success",
                                                      data=user)), 200)
        return response

    @jwt_required()
    def delete(self, username):
        """
        Remove a user.
        """
        errors = []
        result = User.delete(username)
        if result != "":
            errors.append(result)

        result = Reply.delete(username)
        if result != "":
            errors.append(result)

        result = NasPort.delete(username)
        if result != "":
            errors.append(result)

        result = UserInfo.delete(username)
        if result != "":
            errors.append(result)

        if errors != []:
            return empty_result(status="error", data=errors), 400
        return empty_result(status="success", data=[])


api.add_resource(AuthApi, "")
api.add_resource(AuthApi, "/")
api.add_resource(AuthApiByName, "/<string:username>")
api.add_resource(AuthApiByName, "/<string:username>/")
