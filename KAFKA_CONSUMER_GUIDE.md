# 🎯 Kafka Consumer Implementation Guide

## Overview

The Incident Management System now includes a complete **Kafka Consumer** implementation that processes incident events in real-time. This enables:

- **Real-time notifications** for incident creation and status updates
- **Automated escalation** for high-priority incidents  
- **Event-driven workflows** for notifications and integrations
- **Monitoring and metrics** collection
- **Scalable event processing** architecture

## 🏗️ Architecture

```
┌─────────────────┐    Kafka Events     ┌─────────────────┐
│   Django App    │ ──────────────────► │ Kafka Cluster   │
│   (Producer)    │                     │                 │
└─────────────────┘                     └─────────────────┘
                                                   │
                                                   │ Consume Events
                                                   ▼
                                        ┌─────────────────┐
                                        │  Consumer App   │
                                        │                 │
                                        │ • Notifications │
                                        │ • Escalations   │
                                        │ • Metrics       │
                                        │ • Workflows     │
                                        └─────────────────┘
```

## 📋 Event Types Processed

### 1. **incident_created**
- **Triggered**: When a new incident is created
- **Actions**:
  - Send email notifications to administrators
  - Trigger escalation for high/critical priority incidents
  - Log incident creation metrics

### 2. **status_updated**  
- **Triggered**: When incident status changes
- **Actions**:
  - Send status update notifications
  - Handle incident resolution workflows
  - Track status change metrics

## 🚀 Usage Instructions

### **1. Start All Services**

```bash
# Start Kafka and PostgreSQL
./scripts/dev_start.sh
```

### **2. Start Django Application**

```bash
source venv/bin/activate
python manage.py runserver
```

### **3. Start Kafka Consumer**

**Option A: Using the startup script**
```bash
./scripts/start_consumer.sh
```

**Option B: Using Django management command**
```bash
source venv/bin/activate
python manage.py consume_incidents --log-level=INFO
```

### **4. Test the System**

1. **Create an incident** via the web interface at http://localhost:8000
2. **Update incident status** to see status change events
3. **Check consumer logs** to see event processing

## 📊 Consumer Features

### **Event Handlers**
- `handle_incident_created()` - Processes new incident events
- `handle_status_updated()` - Processes status change events  
- `handle_incident_resolved()` - Special handling for resolved incidents
- `trigger_escalation()` - Escalates high-priority incidents

### **Notification System**
- Email notifications for administrators
- Status update notifications for assigned users
- Escalation alerts for critical incidents

### **Monitoring & Metrics**
- Event processing metrics
- Incident lifecycle tracking
- Performance monitoring logs

### **Error Handling**
- Graceful error handling for failed event processing
- Kafka connection retry logic
- Message processing failure recovery

## 🔧 Configuration

### **Kafka Settings** (`settings.py`)
```python
KAFKA_CONFIG = {
    'BOOTSTRAP_SERVERS': ['localhost:9092'],
    'INCIDENT_TOPIC': 'incidents-created'
}
```

### **Consumer Settings**
- **Consumer Group**: `incident-management-consumer`
- **Auto Offset Reset**: `latest` (only new messages)
- **Auto Commit**: `True`
- **Timeout**: `1000ms`

## 🎛️ Management Commands

### **Start Consumer**
```bash
python manage.py consume_incidents [--log-level=INFO]
```

**Options:**
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### **Consumer Process Management**

**Check if running:**
```bash
ps aux | grep "consume_incidents"
```

**Stop consumer:**
```bash
# Use Ctrl+C for graceful shutdown
```

## 📝 Event Message Format

### **Incident Created Event**
```json
{
  "incident_id": 123,
  "title": "Server Down",
  "priority": "high",
  "status": "open",
  "category": "hardware",
  "reported_by": "john.doe",
  "assigned_to": "jane.smith",
  "created_at": "2024-01-01T10:00:00Z",
  "event_type": "incident_created"
}
```

### **Status Updated Event**
```json
{
  "incident_id": 123,
  "title": "Server Down",
  "old_status": "open",
  "new_status": "resolved",
  "priority": "high",
  "assigned_to": "jane.smith",
  "updated_at": "2024-01-01T11:30:00Z",
  "event_type": "status_updated"
}
```

## 🚨 Production Deployment

### **1. Email Configuration**
Uncomment and configure email settings in `kafka_consumer.py`:
```python
send_mail(
    subject=subject,
    message=message,
    from_email='incidents@company.com',
    recipient_list=recipients,
    fail_silently=False,
)
```

### **2. External Integrations**
Extend the consumer for:
- **Slack notifications**: Add Slack webhook calls
- **PagerDuty alerts**: Integrate PagerDuty API for escalations
- **SMS notifications**: Add Twilio integration
- **Monitoring systems**: Send metrics to Prometheus/Grafana

### **3. Scaling**
- Run multiple consumer instances for high availability
- Use different consumer groups for different processing workflows
- Implement dead letter queues for failed messages

### **4. Monitoring**
- Monitor consumer lag
- Track processing times
- Set up alerts for consumer failures

## 🐛 Troubleshooting

### **Consumer Not Starting**
1. Check Kafka is running: `podman ps | grep kafka`
2. Verify topics exist: `podman exec incident-kafka kafka-topics --list --bootstrap-server localhost:9092`
3. Check Django settings for KAFKA_CONFIG

### **No Events Received**
1. Verify producer is sending events (check Django logs)
2. Check Kafka UI at http://localhost:8080
3. Verify topic name matches in producer and consumer

### **Consumer Process Dies**
1. Check system resources (memory, CPU)
2. Review error logs
3. Verify Kafka connectivity