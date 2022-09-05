import re

from cnaas_nac.api.generic import empty_result, fields
from cnaas_nac.db.groups import Group
from cnaas_nac.db.user import get_users
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

logger = get_logger()


api = Namespace("groups", description="Groups API",
                prefix="/api/{}".format(__api_version__))


class GroupsApi(Resource):
    @jwt_required()
    def post(self):
        errors = []
        json_request = request.get_json()

        if isinstance(json_request, str):
            json_request = [json_request]

        for json_data in json_request:
            if "groupname" not in json_data:
                errors.append("groupname is mandatory")
            if "fieldname" not in json_data:
                errors.append("fieldname is mandatory")
            if "condition" not in json_data:
                errors.append("condition is mandatory")

            if errors != []:
                return make_response(jsonify(empty_result(status="error",
                                                          data=errors)), 400)

            groupname = json_data["groupname"]
            fieldname = json_data["fieldname"]

            if fieldname not in fields:
                errors.append(f"Invalid field: {fieldname}")

            try:
                res = Group.add(groupname,
                                fieldname,
                                json_data["condition"])
            except Exception as e:
                res = f"Failed to add group {groupname}"
                print(str(e))

            if res != "":
                errors.append(res)

        if errors != []:
            return make_response(jsonify(empty_result(status="error",
                                                      data=errors)), 400)

        return make_response(jsonify(empty_result(status="success", data="")), 200)

    @jwt_required()
    def get(self):
        data = Group.get()
        response = make_response(jsonify(empty_result(status="success",
                                                      data=data)), 200)
        response.headers["X-Total-Count"] = len(data)

        return response

    @jwt_required()
    def delete(self):
        pass


class GroupsApiByName(Resource):
    @jwt_required()
    def get(self, groupname):
        errors = []
        group = Group.get(groupname)[0]

        if not group:
            errors.append(f"Could not find group {groupname}")

        users = get_users(field=group["fieldname"],
                          condition=group["condition"])

        if errors != []:
            return make_response(jsonify(empty_result(status="error",
                                                      data=errors)), 400)

        return make_response(jsonify(empty_result(status="success", data=users)), 200)

    @jwt_required()
    def put(self):
        pass

    @jwt_required()
    def delete(self, groupname):
        errors = []

        res = Group.delete(groupname)

        if res != "":
            errors.append(res)

        if errors != []:
            return make_response(jsonify(empty_result(status="error",
                                                      data=errors)), 400)

        return make_response(jsonify(empty_result(status="success", data=[])), 200)


api.add_resource(GroupsApi, "")
api.add_resource(GroupsApiByName, "/<string:groupname>")
api.add_resource(GroupsApiByName, "/<string:groupname>/")
