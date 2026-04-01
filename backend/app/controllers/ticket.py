from flask import request
from flask_restful import Resource, Api
from app.services.ticket import TicketService
from app.services.log import LogService
from app.utils.httpResponses import success_200, success_201, error_400, error_404, error_500
from app.schemas.ticket import TicketSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

class TicketListResource(Resource):
    @jwt_required()
    def get(self):
        tickets = TicketService.getAll()
        return success_200(TicketSchema(many=True).dump(tickets))

class TicketCreateResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            uid = get_jwt_identity()
            ticket = TicketService.create(data, uid)
            if ticket == "USER_NOT_FOUND": return error_404("User not found")
            return success_201(TicketSchema().dump(ticket))
        except Exception as e:
            return error_500(str(e))

class TicketResource(Resource):
    @jwt_required()
    def put(self, ticket_id):
        try:
            data = request.get_json()
            new_status = data.get('status')
            updated = TicketService.update_status(ticket_id, new_status)
            if updated:
                LogService.create_log("TICKET_MOVE", f"Ticket {ticket_id} -> {new_status}", user_id=get_jwt_identity())
                return success_200(TicketSchema().dump(updated))
            return error_404("Ticket not found")
        except Exception as e:
            return error_500(str(e))

def initializeRoutes(api: Api):
    api.add_resource(TicketListResource, '/api/tickets')
    api.add_resource(TicketCreateResource, '/api/tickets')
    api.add_resource(TicketResource, '/api/tickets/<string:ticket_id>')