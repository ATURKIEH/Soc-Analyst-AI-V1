import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import numpy as np


class DataProcessing:
    def __init__(self):
        pass

    def load_and_process(self, df1: np.ndarray, df2: np.ndarray) -> np.ndarray:
        '''
            Function that takes in the Datasets, both Train and test Datasets, adds the column names,
            removes a column, scales and encodes(part of it) the dataset and returns the split
            Arguments:
                df1: np.ndarray (m,) m examples (Pandas dataset csv)
                df2: np.ndarray (m,) m examples (Pandas dataset csv)
        
        '''

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
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate',
            'label', 'difficulty'
        ]

        attack_map = {
            'normal': 'normal',
            
            # DoS attacks
            'neptune':'DoS', 'back':'DoS', 'land':'DoS',
            'pod':'DoS', 'smurf':'DoS', 'teardrop':'DoS',
            'mailbomb':'DoS', 'apache2':'DoS', 'processtable':'DoS',
            'udpstorm':'DoS',
            
            # Probe attacks
            'ipsweep':'Probe', 'nmap':'Probe', 'portsweep':'Probe',
            'satan':'Probe', 'mscan':'Probe', 'saint':'Probe',
            
            # R2L attacks
            'ftp_write':'R2L', 'guess_passwd':'R2L', 'imap':'R2L',
            'multihop':'R2L', 'phf':'R2L', 'spy':'R2L',
            'warezclient':'R2L', 'warezmaster':'R2L', 'sendmail':'R2L',
            'named':'R2L', 'snmpgetattack':'R2L', 'snmpguess':'R2L',
            'xlock':'R2L', 'xsnoop':'R2L', 'worm':'R2L',
            
            # U2R attacks
            'buffer_overflow':'U2R', 'loadmodule':'U2R',
            'perl':'U2R', 'rootkit':'U2R', 'httptunnel':'U2R',
            'ps':'U2R', 'sqlattack':'U2R', 'xterm':'U2R'
        }

        #assign columns
        df1.columns = columns
        df2.columns = columns

        #drop 
        df1.drop('difficulty', axis=1, inplace=True)
        df2.drop('difficulty', axis=1, inplace=True)
        #map to attackmap
        df1['label'] = df1['label'].map(attack_map)
        df2['label'] = df2['label'].map(attack_map)

        df1['label'] = df1['label'].fillna('other')
        df2['label'] = df2['label'].fillna('other')

        #encode
        encoder_protocol = LabelEncoder()
        df1['protocol_type'] = encoder_protocol.fit_transform(df1['protocol_type'])
        df2['protocol_type'] = df2['protocol_type'].apply(
            lambda x: x if x in encoder_protocol.classes_ else 'other'
        )
        df2['protocol_type'] = encoder_protocol.transform(df2['protocol_type'])

        encoder_service = LabelEncoder()
        df1['service'] = encoder_service.fit_transform(df1['service'])
        df2['service'] = df2['service'].apply(
            lambda x: x if x in encoder_service.classes_ else 'other'
        )
        df2['service'] = encoder_service.transform(df2['service'])

        encoder_flag = LabelEncoder()
        df1['flag'] = encoder_flag.fit_transform(df1['flag'])
        df2['flag'] = df2['flag'].apply(
            lambda x: x if x in encoder_flag.classes_ else 'other'
        )
        df2['flag'] = encoder_flag.transform(df2['flag'])

        #splitting and scaling
        X_train = df1.drop('label', axis = 1)
        y_train = df1['label']

        X_test = df2.drop('label', axis = 1)
        y_test = df2['label']

        scaler = MinMaxScaler()

        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test, encoder_protocol, encoder_flag, encoder_service, scaler

    def get_normal_traffic(self, X_train_scaled: np.ndarray, 
                        y_train: pd.Series) -> np.ndarray:
        
        '''
            Takes in scaled X_train numpy array dataset, and their values,
            Function aims to return the examples of the dataset where they are normal(not anomalies) in order to train the model with only normal examples
            Arguments:
                X_train_scaled: np.ndarray (m,) m examples
                y_train: np.Series (m,) m rows
        '''
        mask = y_train.values == 'normal'
        return X_train_scaled[mask]
    


