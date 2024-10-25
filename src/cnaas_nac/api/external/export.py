import os

from cnaas_nac.api.generic import csv_export, empty_result
from cnaas_nac.db.user import get_users
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import jsonify, make_response
from flask_jwt_extended import decode_token
from flask_restx import Namespace, Resource

logger = get_logger()


api = Namespace(
    "export",
    description="Export API",
    prefix="/api/{}".format(__api_version__),
)


class ExportApi(Resource):
    def __validate_token(self, token):
        if os.environ.get("DISABLE_JWT"):
            return ""

        try:
            decode_token(token)
        except Exception as e:
            return str(e)

        return ""

    def get(self, token):
        err = self.__validate_token(token)

        if err != "":
            return make_response(
                jsonify(empty_result(status="error", data=str(err))), 400
            )

        users = get_users()
        user_count = len(users)

        response = make_response(csv_export(users))
        response.headers["Content-type"] = "application/csv"
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        response.headers["X-Total-Count"] = user_count

        return response


api.add_resource(ExportApi, "/<string:token>")
