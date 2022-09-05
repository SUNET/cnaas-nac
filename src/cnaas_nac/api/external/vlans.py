from cnaas_nac.api.generic import empty_result
from cnaas_nac.db.reply import Reply
from cnaas_nac.db.user import get_users
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

logger = get_logger()


api = Namespace("vlans", description="Vlans API",
                prefix="/api/{}".format(__api_version__))


class VlansApi(Resource):
    @jwt_required()
    def get(self):
        vlans = Reply.get_vlans()
        response = make_response(jsonify(empty_result(status="success",
                                                      data=vlans)), 200)
        response.headers["X-Total-Count"] = len(vlans)

        return response


class VlansApiByName(Resource):
    @jwt_required()
    def get(self, vlan):
        vlan_users = Reply.get_users_from_vlan(vlan)
        users = get_users(usernames_list=vlan_users)

        response = make_response(jsonify(empty_result(status="success",
                                                      data=users)), 200)
        response.headers["X-Total-Count"] = len(users)

        return response


api.add_resource(VlansApi, "")
api.add_resource(VlansApiByName, "/<string:vlan>")
api.add_resource(VlansApiByName, "/<string:vlan>/")
