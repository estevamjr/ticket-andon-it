from flask import request
from flask_restful import Resource, Api
from app.services.andon import AndonService
from app.services.log import LogService
from app.services.llm_service import LLMService
from app.utils.httpResponses import success_201, error_400, error_500
from app.schemas.andon import AndonAnalysisSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

def initializeAndonRoutes(api: Api):
    api.add_resource(AndonResource, '/api/andon/analyze')

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

            # Chama o Service que arrumamos no passo anterior
            analysis_log = AndonService.analyze_telemetry(data)
            
            llm_mitigation = None
            log_details = f"Analysis for device: {data['device_id']} - Status: {analysis_log.andon_status}"
            
            # --- GATILHO REAL DO OPENROUTER ---
            if analysis_log.andon_status in [1, 2]:
                data_for_llm = data.copy()
                data_for_llm['andon_status'] = analysis_log.andon_status
                llm_mitigation = LLMService.get_mitigation(data_for_llm)
                log_details += f" | LLM Mitigation: {llm_mitigation}"

            LogService.create_log("AI_ANDON_ANALYSIS", log_details, user_id=current_user_id)

            schema = AndonAnalysisSchema()
            result_payload = schema.dump(analysis_log)
            if llm_mitigation:
                result_payload['llm_mitigation'] = llm_mitigation

            return success_201(result_payload)

        except Exception as e:
            user_id = None
            try: user_id = get_jwt_identity()
            except: pass
            LogService.create_log("AI_ANALYSIS_ERROR", str(e), user_id=user_id)
            return error_500(f"AI Engine Error: {str(e)}")