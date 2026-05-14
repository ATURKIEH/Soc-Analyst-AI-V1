from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate

class IncidentReporter:
    def __init__(self):
        self.model = init_chat_model(model = 'llama3', model_provider= 'ollama', temperature = 0.3)
        self.prompt_template = ChatPromptTemplate.from_messages([
                ('system', 'You are a SOC analyst. Generate concise professional incident reports based on the following attack details. Be technical and actionable.'),
                ('human', '{attack_details}')
            ])
        self.chain = self.prompt_template | self.model

    def compute_risk_score(self, anomaly_score, attack_type):
        attack_weights = {
            'DoS':    0.9,
            'Probe':  0.6,
            'R2L':    0.8,
            'U2R':    1.0,
            'normal': 0.0
        }
        risk_score = int(anomaly_score * attack_weights[attack_type] * 100)
        return risk_score
    
    def generate_report(self, attack_type, anomaly_score, src_ip, timestamp):
        risk_score = self.compute_risk_score(anomaly_score, attack_type)

        attack_details = f"Attack Type: {attack_type}\nAnomaly Score: {anomaly_score:.4f}\nSource IP: {src_ip}\nTimestamp: {timestamp}\nRisk Score: {risk_score}/100"
        response = self.chain.invoke({'attack_details': attack_details})
        return response.content, risk_score
        