from typing import Dict, Any
from marshmallow import Schema
from app.schemas.ticket import TicketCreateSchema, TicketSchema, UserSchema, LogSchema
from app.schemas.andon import AndonAnalysisSchema

# Technical Mapping for Swagger data types
FIELD_TYPE_MAP = {
    'String': ('string', None),
    'Integer': ('integer', 'int32'),
    'Float': ('number', 'float'),
    'DateTime': ('string', 'date-time'),
    'Boolean': ('boolean', None)
}

def _schema_to_definition(schema_cls: Schema) -> Dict[str, Any]:
    """Converts Marshmallow Schemas into standard Swagger JSON definitions."""
    schema = schema_cls()
    props = {}
    for name, field in schema.fields.items():
        fname = field.__class__.__name__
        otype, format_ = FIELD_TYPE_MAP.get(fname, ('string', None))
        props[name] = {'type': otype}
        if format_: 
            props[name]['format'] = format_
    return {'type': 'object', 'properties': props}

def build_swagger_template() -> Dict[str, Any]:
    """Generates the full Swagger template in English for the Agile Bison API."""
    
    definitions = {
        'Ticket': _schema_to_definition(TicketSchema),
        'TicketCreate': _schema_to_definition(TicketCreateSchema),
        'Log': _schema_to_definition(LogSchema),
        'User': _schema_to_definition(UserSchema),
        'AndonAnalysis': _schema_to_definition(AndonAnalysisSchema),
    }

    template = {
        'swagger': '2.0',
        'info': {
            'title': 'Agile Bison API - Ticket Management & Andon AI',
            'version': '2.0.0',
            'description': 'API documentation for IT incident management with predictive analysis via Machine Learning.'
        },
        'securityDefinitions': {
            'bearerAuth': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Enter the JWT token in the format: Bearer <your_token_here>'
            }
        },
        'definitions': definitions,
        'paths': {
            # --- AUTHENTICATION ---
            '/api/auth/register': {
                'post': {
                    'tags': ['Authentication'],
                    'summary': 'Register a new user in the system',
                    'parameters': [
                        {
                            'in': 'body', 'name': 'body', 'schema': {
                            'type': 'object',
                            'properties': {
                                    'username': {'type': 'string'},
                                    'password': {'type': 'string'}
                                }
                            }
                        }
                    ],
                    'responses': {'201': {'description': 'User created successfully'}}
                }
            },
            '/api/auth/login': {
                'post': {
                    'tags': ['Authentication'],
                    'summary': 'Login and obtain JWT token',
                    'parameters': [
                        {'in': 'body', 'name': 'credentials', 'schema': {
                            'type': 'object',
                            'properties': {
                                'username': {'type': 'string'},
                                'password': {'type': 'string'}
                            }
                        }}
                    ],
                    'responses': {'200': {'description': 'Successful login, token generated'}}
                }
            },
            # --- TICKETS ---
            '/api/tickets': {
                'get': {
                    'tags': ['Ticket Management'],
                    'summary': 'List all Kanban tickets',
                    'security': [{'bearerAuth': []}],
                    'responses': {'200': {'schema': {'type': 'array', 'items': {'$ref': '#/definitions/Ticket'}}}}
                },
                'post': {
                    'tags': ['Ticket Management'],
                    'summary': 'Create a ticket manually',
                    'security': [{'bearerAuth': []}],
                    'parameters': [
                        {'in': 'body', 'name': 'body', 'schema': {'$ref': '#/definitions/TicketCreate'}}
                    ],
                    'responses': {'201': {'schema': {'$ref': '#/definitions/Ticket'}}}
                }
            },
            '/api/tickets/<int:id>': {
                'put': {
                    'tags': ['Ticket Management'],
                    'summary': 'Update ticket status (Closed-Loop Workflow)',
                    'security': [{'bearerAuth': []}],
                    'parameters': [
                        {'in': 'path', 'name': 'id', 'required': True, 'type': 'integer', 'description': 'Ticket ID'},
                        {'in': 'body', 'name': 'body', 'schema': {'type': 'object', 'properties': {'status': {'type': 'string'}}}}
                    ],
                    'responses': {'200': {'schema': {'$ref': '#/definitions/Ticket'}}}
                }
            },
            # --- ANDON AI & LOGS ---
            '/api/andon/analyze': {
                'post': {
                    'tags': ['Andon AI Intelligence'],
                    'summary': 'Analyze telemetry and generate automated alerts',
                    'security': [{'bearerAuth': []}],
                    'parameters': [
                        {'in': 'body', 'name': 'telemetry_data', 'schema': {'$ref': '#/definitions/AndonAnalysis'}}
                    ],
                    'responses': {
                        '201': {
                            'description': 'ML analysis completed. Andon updated.',
                            'schema': {'$ref': '#/definitions/AndonAnalysis'}
                        }
                    }
                }
            },
            '/api/logs': {
                'get': {
                    'tags': ['Telemetry'],
                    'summary': 'Consult history of logs processed by AI',
                    'security': [{'bearerAuth': []}],
                    'responses': {'200': {'schema': {'type': 'array', 'items': {'$ref': '#/definitions/Log'}}}}
                }
            }
        }
    }
    return template

__all__ = [
    "build_swagger_template",
]