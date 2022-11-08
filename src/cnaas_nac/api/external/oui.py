from cnaas_nac.api.generic import empty_result, jwt_required
from cnaas_nac.db.oui import DeviceOui
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import jsonify, make_response, request
from flask_restx import Namespace, Resource

logger = get_logger()


api = Namespace(
    "oui",
    description="OUI API",
    prefix="/api/{}".format(__api_version__),
)


class DeviceOuiApi(Resource):
    @jwt_required()
    def post(self):
        errors = []
        json_request = request.get_json()

        if not isinstance(json_request, list):
            json_request = [json_request]

        for json_data in json_request:
            if "oui" not in json_data or json_data["oui"] == "":
                errors.append("oui is mandatory")
            if "vlan" not in json_data or json_data["vlan"] == "":
                errors.append("vlan is mandatory")

            if errors != []:
                return make_response(jsonify(empty_result(status="error",
                                                          data=errors)), 400)

            oui = json_data["oui"]
            vlan = json_data["vlan"]

            if "description" in json_data:
                description = json_data["description"]
            else:
                description = None

            try:
                res = DeviceOui.add(oui, vlan, description)
            except Exception as e:
                res = f"Failed to add OUI {oui}"
                print(str(e))

            if res != "":
                errors.append(res)

        if errors != []:
            print(errors)
            return make_response(jsonify(empty_result(status="error",
                                                      data=errors)), 400)

        return make_response(jsonify(empty_result(status="success", data="")), 200)

    @jwt_required()
    def get(self):
        data = DeviceOui.get()

        response = make_response(jsonify(empty_result(status="success",
                                                      data=data)), 200)
        response.headers["X-Total-Count"] = len(data)

        return response

    @jwt_required()
    def delete(self):
        pass


class DeviceOuiApiByName(Resource):
    @jwt_required()
    def get(self, groupname):
        pass

    @jwt_required()
    def put(self, groupname):
        pass

    @jwt_required()
    def delete(self, oui):
        errors = []

        res = DeviceOui.delete(oui)

        if res != "":
            errors.append(res)

        if errors != []:
            return make_response(jsonify(empty_result(status="error",
                                                      data=errors)), 400)

        return make_response(jsonify(empty_result(status="success", data=[])), 200)


api.add_resource(DeviceOuiApi, "")
api.add_resource(DeviceOuiApiByName, "/<string:oui>")
api.add_resource(DeviceOuiApiByName, "/<string:oui>/")
