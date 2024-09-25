import streamlit as st
import ping3
import psutil
from pysnmp.hlapi import *
import numpy as np
import smtplib
from email.mime.text import MIMEText

# Function to ping a host
def ping_host(host):
    response = ping3.ping(host)
    return response

# Function to get local metrics
def get_local_metrics():
    return {
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }

# Function to get SNMP data
def snmp_get(oid, ip, community='public'):
    iterator = getCmd(SnmpEngine(),
                      CommunityData(community),
                      UdpTransportTarget((ip, 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity(oid)))
    
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    
    if errorIndication:
        return str(errorIndication)
    elif errorStatus:
        return f'{errorStatus.prettyPrint()} at {errorIndex}' if errorIndex else str(errorStatus)
    
    for varBind in varBinds:
        return varBind.prettyPrint()

# Function for anomaly detection
def detect_anomalies(data):
    if len(data) < 2:
        return []
    mean = np.mean(data)
    std_dev = np.std(data)
    z_scores = [(x - mean) / std_dev for x in data]
    return [x for x in z_scores if abs(x) > 2]

# Function to send alerts
def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'Network Alert'
    msg['From'] = 'your_email@example.com'  # Replace with your email
    msg['To'] = 'recipient@example.com'  # Replace with recipient's email
    
    with smtplib.SMTP('smtp.example.com') as server:  # Replace with your SMTP server
        server.login('your_email@example.com', 'password')  # Replace with your credentials
        server.send_message(msg)

# Streamlit UI
st.title("Automated Network Monitoring Dashboard")
st.write("Enter the IP address of the device you want to monitor:")

# Input field for IP address
host = st.text_input("IP Address", "192.168.1.1")

if st.button("Ping"):
    response_time = ping_host(host)
    if response_time is None:
        st.error(f"Alert: {host} is down!")
        send_alert(f"{host} is down!")
    else:
        st.success(f"{host} responded in {response_time} seconds")

# Display local network metrics
st.subheader("Local Network Metrics")
metrics = get_local_metrics()
st.write("CPU Usage:", metrics['cpu_usage'], "%")
st.write("Memory Usage:", metrics['memory_usage'], "%")
st.write("Disk Usage:", metrics['disk_usage'], "%")

# Collect data from a router or switch
router_ip = st.text_input("Router IP Address", "192.168.1.1")
oid = '1.3.6.1.2.1.1.5.0'  # Replace with the OID you want to monitor

if st.button("Get Router Data"):
    router_data = snmp_get(oid, router_ip)
    st.write("Router Data:", router_data)

# Anomaly detection on CPU usage
if 'cpu_usage_history' not in st.session_state:
    st.session_state.cpu_usage_history = []

# Append current CPU usage to history
st.session_state.cpu_usage_history.append(metrics['cpu_usage'])
if len(st.session_state.cpu_usage_history) > 10:  # Maintain only the last 10 entries
    st.session_state.cpu_usage_history.pop(0)

anomalies = detect_anomalies(st.session_state.cpu_usage_history)
if anomalies:
    st.warning("Anomaly detected in CPU usage!")
    send_alert("Anomaly detected in CPU usage!")

st.write("Anomaly Detection Data:", anomalies)
