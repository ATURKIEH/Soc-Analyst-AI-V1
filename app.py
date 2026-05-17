from fastapi import FastAPI, File, Request, UploadFile
import numpy as np
import io
from database import Database
from contextlib import asynccontextmanager
import pickle
import joblib
from chatbot import SOCChatBot
import tensorflow as tf
import pandas as pd
import pydantic

from incident_reporter import IncidentReporter


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model_autoencoder = tf.keras.models.load_model('models/autoencoder_model.keras')
    app.state.model_classifier = joblib.load('models/classifier_model.pkl')
    app.state.scaler = joblib.load('models/scaler.pkl')
    app.state.label_encoder = joblib.load('models/label_encoder.pkl')
    app.state.threshold = joblib.load('models/threshold.pkl')
    app.state.encoder_protocol = joblib.load('models/encoder_protocol.pkl')
    app.state.encoder_service = joblib.load('models/encoder_service.pkl')
    app.state.encoder_flag = joblib.load('models/encoder_flag.pkl')
    app.state.reporter = IncidentReporter()
    app.state.chatbot = SOCChatBot()
    app.state.db = Database()
    yield

app = FastAPI(lifespan=lifespan)


class ChatRequest(pydantic.BaseModel):
    message: str
    session_id: str = 'default'


@app.post('/analyze')
async def analyze_data(file: UploadFile = File(...), request: Request = None):
    contents = await file.read()
    data_input = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    # Preprocess the data using the same steps as during training

    all_43_colums = [
            'duration', 'protocol_type', 'service', 'flag',
            'src_bytes', 'dst_bytes', 'land', 'wrong_fragment',
            'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted',
            'num_root', 'num_file_creations', 'num_shells',
            'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
            'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
            'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
            'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
            'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate',
            'label', 'difficulty'
        ]
    
    columns = [
            'duration', 'protocol_type', 'service', 'flag',
            'src_bytes', 'dst_bytes', 'land', 'wrong_fragment',
            'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted',
            'num_root', 'num_file_creations', 'num_shells',
            'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
            'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
            'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
            'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
            'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
        ]
    
    if len(data_input.columns) == 43:
        data_input.columns = all_43_colums
        data_input.drop(['label', 'difficulty'], axis=1, inplace=True)
    elif len(data_input.columns) == 41:
        data_input.columns = columns

    known_services = request.app.state.encoder_service.classes_
    data_input['service'] = data_input['service'].apply(
        lambda x: x if x in known_services else 'other'
    )

    # Handle unseen protocol values
    known_protocols = request.app.state.encoder_protocol.classes_
    data_input['protocol_type'] = data_input['protocol_type'].apply(
        lambda x: x if x in known_protocols else 'tcp'
    )

    # Handle unseen flag values
    known_flags = request.app.state.encoder_flag.classes_
    data_input['flag'] = data_input['flag'].apply(
        lambda x: x if x in known_flags else 'SF'
    )
    
   
    data_input['protocol_type'] = request.app.state.encoder_protocol.transform(data_input['protocol_type'])
    data_input['service'] = request.app.state.encoder_service.transform(data_input['service'])
    data_input['flag'] = request.app.state.encoder_flag.transform(data_input['flag'])

    # Scale the data
    data_input = request.app.state.scaler.transform(data_input)

    # Detect anomalies using the autoencoder
    reconstructed = request.app.state.model_autoencoder.predict(data_input)
    errors        = np.mean(np.square(data_input - reconstructed), axis=1)
    anomaly_mask  = errors > request.app.state.threshold
    data_anomalous = data_input[anomaly_mask]

    predictions   = request.app.state.model_classifier.predict_proba(data_anomalous)
    class_indices = np.argmax(predictions, axis=1)
    attack_types  = request.app.state.label_encoder.inverse_transform(class_indices)
    confidences   = np.max(predictions, axis=1)
    

    

    results = []
    for i in range(len(data_anomalous)):
        anomaly_score = float(errors[anomaly_mask][i])
        attack_type   = str(attack_types[i])
        confidence    = min(float(confidences[i]),0.95)
        
        # Compute risk score first
        risk_score = request.app.state.reporter.compute_risk_score(
            anomaly_score, attack_type
        )
        
        # Compute severity from risk score
        if risk_score >= 80:
            severity = 'Critical'
        elif risk_score >= 60:
            severity = 'High'
        elif risk_score >= 40:
            severity = 'Medium'
        else:
            severity = 'Low'
        
        # Now generate report with both
        report, _ = request.app.state.reporter.generate_report(
            attack_type   = attack_type,
            anomaly_score = anomaly_score,
            src_ip        = "unknown",
            timestamp     = str(pd.Timestamp.now()),
            severity      = severity,
            risk_score    = risk_score
        )
        
        results.append({
            "attack_type":   attack_type,
            "confidence":    confidence,
            "anomaly_score": anomaly_score,
            "risk_score":    risk_score,
            "severity":      severity,
            "report":        report
        })

    for result in results:
        request.app.state.db.insert_incident(
            attack_type   = result["attack_type"],
            confidence    = result["confidence"],
            anomaly_score = result["anomaly_score"],
            risk_score    = result["risk_score"],
            severity      = result["severity"],
            report        = result["report"],
            timestamp     = str(pd.Timestamp.now())
        )

    return results


@app.post('/chat')
async def chat_with_analyst(chat_request: ChatRequest, request: Request):
    response = request.app.state.chatbot.chat(
        chat_request.message,
        chat_request.session_id
    )
    return {"response": response}


@app.get('/history')
async def get_incident_history(request: Request):
    return {"incidents": request.app.state.db.fetch_incidents()}


@app.get('/health')
def health_check():
    return {"status": "healthy"}