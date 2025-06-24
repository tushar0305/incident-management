import json
import logging
from kafka import KafkaProducer
from django.conf import settings

logger = logging.getLogger(__name__)

_producer = None

def get_kafka_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_CONFIG['BOOTSTRAP_SERVERS'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            return None
    return _producer


def send_incident_notification(incident):
    """
    Send incident notification to Kafka topic
    """
    producer = get_kafka_producer()
    if not producer:
        logger.warning("Kafka producer not available, skipping notification")
        return False
    
    try:
        # Prepare notification message
        message = {
            'incident_id': incident.id,
            'title': incident.title,
            'priority': incident.priority,
            'status': incident.status,
            'category': incident.category,
            'reported_by': incident.reported_by.username,
            'assigned_to': incident.assigned_to.username if incident.assigned_to else None,
            'created_at': incident.created_at.isoformat(),
            'event_type': 'incident_created'
        }
        
        # Send to Kafka topic
        topic = settings.KAFKA_CONFIG['INCIDENT_TOPIC']
        future = producer.send(
            topic=topic,
            key=f"incident_{incident.id}",
            value=message
        )
        
        # Wait for message to be sent
        producer.flush()
        
        logger.info(f"Incident notification sent to Kafka: {incident.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send incident notification: {e}")
        return False
    
    # finally:
    #     if producer:
    #         producer.close()


def send_status_update_notification(incident, old_status, new_status):
    """
    Send status update notification to Kafka
    """
    producer = get_kafka_producer()
    if not producer:
        return False
    
    try:
        message = {
            'incident_id': incident.id,
            'title': incident.title,
            'old_status': old_status,
            'new_status': new_status,
            'priority': incident.priority,
            'assigned_to': incident.assigned_to.username if incident.assigned_to else None,
            'updated_at': incident.updated_at.isoformat(),
            'event_type': 'status_updated'
        }
        
        topic = settings.KAFKA_CONFIG['INCIDENT_TOPIC']
        producer.send(
            topic=topic,
            key=f"incident_{incident.id}_status",
            value=message
        )
        
        producer.flush()
        logger.info(f"Status update notification sent: {incident.id} ({old_status} -> {new_status})")
        return True
        
    except Exception as e:
        logger.error(f"Kafka send failed for incident {incident.id}, event_type={message['event_type']} on topic {topic}: {e}")
        return False
    
    # finally:
    #     if producer:
    #         producer.close()