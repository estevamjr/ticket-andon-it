from flask import request
from flask_restful import Resource, Api
from app.services.ticket import TicketService
from app.services.log import LogService
from app.utils.httpResponses import success_200, success_201, error_400, error_404, error_500
from app.schemas.ticket import TicketSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import object_session 

class TicketListResource(Resource):
    @jwt_required()
    def get(self):
        """
        List all Kanban tickets
        ---
        tags:
          - Ticket Management
        security:
          - bearerAuth: []
        responses:
          200:
            description: Lista de tickets
        """
        tickets = TicketService.getAll()
        return success_200(TicketSchema(many=True).dump(tickets))

class TicketResource(Resource):
    @jwt_required()
    def put(self, ticket_id):
        """
        Update a ticket status
        ---
        tags:
          - Ticket Management
        security:
          - bearerAuth: []
        parameters:
          - name: ticket_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            required: true
            description: JSON com status e assignee_id
            schema:
              type: object
              properties:
                status:
                  type: string
                assignee_id:
                  type: string
        responses:
          200:
            description: Ticket atualizado
        """
        try:
            data = request.get_json()
            new_status = data.get('status')
            
            updated = TicketService.update_status(ticket_id, new_status)
            
            if updated:
                if 'assignee_id' in data:
                    updated.assignee_id = data['assignee_id']
                    session = object_session(updated)
                    if session:
                        session.commit()

                LogService.create_log("TICKET_MOVE", f"Ticket {ticket_id} -> {new_status}", user_id=get_jwt_identity())
                return success_200(TicketSchema().dump(updated))
            return error_404("Ticket not found")
        except Exception as e:
            return error_500(str(e))

    @jwt_required()
    def delete(self, ticket_id):
        """
        Delete a ticket physically
        ---
        tags:
          - Ticket Management
        security:
          - bearerAuth: []
        parameters:
          - name: ticket_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Ticket deletado com sucesso
          404:
            description: Ticket não encontrado
        """
        try:
            deleted = TicketService.deleteFisical(ticket_id)
            if deleted:
                LogService.create_log("TICKET_DELETE", f"Ticket {ticket_id} removido", user_id=get_jwt_identity())
                return success_200({"message": "Ticket deleted successfully"})
            return error_404("Ticket not found")
        except Exception as e:
            return error_500(str(e))

def initializeRoutes(api: Api):
    api.add_resource(TicketListResource, '/api/v1/tickets')
    api.add_resource(TicketResource, '/api/v1/tickets/<string:ticket_id>')