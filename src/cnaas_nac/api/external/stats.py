from cnaas_nac.api.generic import empty_result, jwt_required
from cnaas_nac.db.userinfo import UserInfo
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import jsonify, make_response
from flask_restx import Namespace, Resource

logger = get_logger()


api = Namespace(
    "stats",
    description="Statistics API",
    prefix="/api/{}".format(__api_version__),
)


class StatsApi(Resource):
    @jwt_required()
    def get(self):
        data = UserInfo.get_stats()

        response = make_response(jsonify(empty_result(status="success",
                                                      data=data)), 200)
        response.headers["X-Total-Count"] = len(data)

        return response


api.add_resource(StatsApi, "")
