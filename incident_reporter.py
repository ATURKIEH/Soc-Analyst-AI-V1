from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

class IncidentReporter:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(IncidentReporter, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.model = init_chat_model(model = 'llama3.2:1b', model_provider= 'ollama', temperature = 0.3)
        self.prompt_template = ChatPromptTemplate.from_messages([
        ('system', 'You are a SOC analyst. Be extremely concise.'),
        ('human', '''Analyze this threat and respond in exactly this format:
            THREAT: [one sentence what it is]
            SEVERITY: {severity}
            ACTION: [one sentence what to do immediately]
            RISK: [one sentence about the risk]

        Attack: {attack_details}''')
        ])
        self.chain = self.prompt_template | self.model

    def compute_risk_score(self, anomaly_score, attack_type):
        base_scores = {
            'DoS':    20,
            'Probe':  10,
            'R2L':    30,
            'U2R':   40,
            'normal': 0
        }
        bonus      = min(int(anomaly_score * 1000), 30)
        risk_score = min(base_scores.get(attack_type, 10) + bonus, 100)
        return risk_score
    
    def generate_report(self, attack_type, anomaly_score, src_ip, timestamp, severity, risk_score):
        risk_score = self.compute_risk_score(anomaly_score, attack_type)

        attack_details = f"Attack Type: {attack_type}\nAnomaly Score: {anomaly_score:.4f}\nSeverity: {severity}\nRisk_score: {risk_score}/100\nSource IP: {src_ip}\nTimestamp: {timestamp}"
        response = self.chain.invoke({'attack_details': attack_details, 'severity': severity})
        return response.content, risk_score
        