from flask import request
from flask_restful import Resource, Api
from app.services.andon import AndonService
from app.services.log import LogService
from app.services.llm_service import LLMService
from app.utils.httpResponses import success_201, error_400, error_500
from app.schemas.andon import AndonAnalysisSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

# Importações para a criação do Ticket Autônomo
from app.extensions import db # Ajuste para app.extensions se necessário
from app.models.ticket import Ticket # Ajuste o caminho exato do seu model

def initializeAndonRoutes(api: Api):
    api.add_resource(AndonResource, '/api/v1/andon/analyze')

class AndonResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json(silent=True)

            if not data:
                return error_400("Payload JSON ausente ou inválido.")

            required = ['device_id', 'cpu_usage_pct', 'mem_available_gb', 'active_threats', 'untrusted_processes']
            if not all(field in data for field in required):
                return error_400("Missing required telemetry fields")

            analysis_log = AndonService.analyze_telemetry(data)
            
            llm_mitigation = None
            log_details = f"Analysis for device: {data['device_id']} - Status: {analysis_log.andon_status}"
            ticket_criado_id = None
            
            # --- GATILHO REAL DO OPENROUTER ---
            if analysis_log.andon_status in [1, 2]:
                data_for_llm = data.copy()
                data_for_llm['andon_status'] = analysis_log.andon_status
                llm_mitigation = LLMService.get_mitigation(data_for_llm)
                log_details += f" | LLM Mitigation: {llm_mitigation}"

                # INTEGRAÇÃO AUTÔNOMA: Criação do ticket no banco
                try:
                    novo_ticket = Ticket(
                        title=f"[Andon IA] Incidente Crítico - {data['device_id']}",
                        description=llm_mitigation,
                        priority="high",
                        status="open",
                        user_id=current_user_id
                    )
                    db.session.add(novo_ticket)
                    db.session.commit()
                    ticket_criado_id = str(novo_ticket.id)
                except Exception as db_err:
                    db.session.rollback()
                    LogService.create_log("TICKET_CREATION_ERROR", str(db_err), user_id=current_user_id)

            LogService.create_log("AI_ANDON_ANALYSIS", log_details, user_id=current_user_id)

            schema = AndonAnalysisSchema()
            result_payload = schema.dump(analysis_log)
            if llm_mitigation:
                result_payload['llm_mitigation'] = llm_mitigation
                
            if ticket_criado_id:
                result_payload['ticket_id'] = ticket_criado_id

            return success_201(result_payload)

        except Exception as e:
            user_id = None
            try: user_id = get_jwt_identity()
            except: pass
            LogService.create_log("AI_ANALYSIS_ERROR", str(e), user_id=user_id)
            return error_500(f"AI Engine Error: {str(e)}")