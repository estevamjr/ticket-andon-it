import os
import requests
from typing import Dict, Any

class LLMService:
    """
    Serviço estático para geração de diagnósticos e planos de mitigação
    de incidentes Andon via API OpenRouter.
    """
    REQUEST_TIMEOUT: int = 100

    @staticmethod
    def _build_system_prompt() -> str:
        """Define as diretrizes e papel operacional da IA."""
        return (
            "Você é um Engenheiro de Suporte de TI Nível 3 e Especialista em Infraestrutura. "
            "Sua função é analisar telemetrias de incidentes críticos e fornecer planos "
            "de mitigação objetivos, técnicos, concisos e orientados à ação. "
            "Priorize comandos operacionais, isolamento de ameaças e liberação de recursos. "
            "Não inclua saudações ou textos introdutórios/conclusivos desnecessários."
        )

    @staticmethod
    def _build_user_prompt(telemetry_data: Dict[str, Any]) -> str:
        """Estrutura os campos de telemetria recebidos em um prompt textual."""
        device_id = telemetry_data.get("device_id", "N/A")
        cpu_usage = telemetry_data.get("cpu_usage_pct", "N/A")
        mem_avail = telemetry_data.get("mem_available_gb", "N/A")
        threats = telemetry_data.get("active_threats", 0)
        untrusted = telemetry_data.get("untrusted_processes", [])
        andon_status = telemetry_data.get("andon_status", "N/A")

        status_label = "Crítico (2)" if andon_status == 2 else f"Aviso ({andon_status})"

        return (
            f"Alerta de Incidente Andon Detectado:\n"
            f"- Device ID: {device_id}\n"
            f"- Status Andon: {status_label}\n"
            f"- Uso de CPU: {cpu_usage}%\n"
            f"- Memória Disponível: {mem_avail} GB\n"
            f"- Ameaças Ativas: {threats}\n"
            f"- Processos Suspeitos: {untrusted}\n\n"
            f"Gere o plano de ação técnico imediato para contenção e mitigação deste incidente."
        )

    @staticmethod
    def get_mitigation(telemetry_data: dict) -> str:
        """
        Consome a API do OpenRouter para gerar o plano de mitigação a partir da telemetria.
        Retorna o erro exato da API em caso de falha (sem fallback genérico).
        """
        # O strip() garante que não haja aspas ou espaços invisíveis vindos do .env quebrando a URL/Modelo
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip(' "\'')
        model_name = os.getenv("LLM_MODEL_NAME", "meta-llama/llama-3.1-8b-instruct:free").strip(' "\'')
        openrouter_url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions").strip(' "\'')

        if not api_key:
            return "[ERRO INTERNO] A variável 'OPENROUTER_API_KEY' não está configurada no .env do container."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": "Ticket Andon MVP"
        }

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": LLMService._build_system_prompt()
                },
                {
                    "role": "user",
                    "content": LLMService._build_user_prompt(telemetry_data)
                }
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(
                url=openrouter_url,
                headers=headers,
                json=payload,
                timeout=LLMService.REQUEST_TIMEOUT
            )

            # Se o OpenRouter negar (Ex: 404, 401, 429), expõe o motivo real direto no JSON
            if response.status_code != 200:
                return f"[ERRO OPENROUTER {response.status_code}] Modelo: {model_name} | Retorno: {response.text}"

            data = response.json()
            choices = data.get("choices")
            if choices and isinstance(choices, list) and len(choices) > 0:
                content = choices[0].get("message", {}).get("content")
                if content and isinstance(content, str):
                    return content.strip()

            return f"[ERRO DE FORMATO] A IA respondeu, mas o JSON veio diferente do esperado: {data}"

        except requests.exceptions.RequestException as req_err:
            return f"[ERRO DE REDE/HTTP] Falha na requisição para o OpenRouter: {str(req_err)}"
        except Exception as exc:
            return f"[ERRO INESPERADO] Ocorreu uma falha no processamento: {str(exc)}"