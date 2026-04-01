from flask import request
from flask_restful import Resource, Api
from app.services.log import LogService
from app.utils.httpResponses import success_200, error_404, error_500
from flask_jwt_extended import jwt_required
from app.extensions import ma 
from marshmallow import fields 

class LogSchema(ma.Schema):
    id = fields.String(dump_only=True)
    timestamp = fields.DateTime(dump_only=True)
    action = fields.String(dump_only=True)
    details = fields.String(dump_only=True)
    
    class Meta:
        ordered = True

def initializeLogRoutes(api: Api):
    api.add_resource(LogResource, '/api/logs')

class LogResource(Resource):
    
    @jwt_required()
    def get(self):
        try:
            logs = LogService.getAll()
            if not logs:
                return success_200([]) 
            
            log_schema = LogSchema(many=True)
            return success_200(log_schema.dump(logs)) 
        
        except Exception as e:
            print(f"Error getting logs: {e}")
            return error_500("An error occurred while fetching logs.")