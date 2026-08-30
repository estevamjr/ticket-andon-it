from app.extensions import db
from app.models.log import Log
from app.ml_logic.predictor import AndonPredictor

ai_engine = AndonPredictor()

class AndonService:
    @staticmethod
    def analyze_telemetry(data: dict) -> Log:
        try:
            # 1. Tratamento seguro: Se for lista, pega o tamanho. Se não, converte para int.
            threats_data = data.get('active_threats', 0)
            threats_count = len(threats_data) if isinstance(threats_data, list) else int(threats_data)

            untrusted_data = data.get('untrusted_processes', 0)
            untrusted_count = len(untrusted_data) if isinstance(untrusted_data, list) else int(untrusted_data)

            # 2. Envio para a IA com os números já tratados
            prediction = ai_engine.predict(
                cpu=float(data['cpu_usage_pct']),
                ram=float(data['mem_available_gb']),
                threats=threats_count,
                untrusted=untrusted_count
            )

            # 3. Salvamento no banco de dados
            new_entry = Log(
                action="AI_ANDON_ANALYSIS",
                details=f"Device: {data.get('device_id')}",
                cpu_usage=data['cpu_usage_pct'],
                ram_usage=data['mem_available_gb'],
                active_threats=threats_count,
                untrusted_processes=untrusted_count,
                andon_status=prediction
            )

            db.session.add(new_entry)
            db.session.commit()
            return new_entry

        except Exception as e:
            db.session.rollback()
            raise e