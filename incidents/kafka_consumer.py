import json
import logging
import threading
import signal
import sys
from typing import Dict, Any, Callable
from kafka import KafkaConsumer
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .models import Incident

logger = logging.getLogger(__name__)

class IncidentEventConsumer:
    """
    Kafka consumer for processing incident events
    """
    
    def __init__(self):
        self.consumer = None
        self.running = False
        self.event_handlers = {
            'incident_created': self.handle_incident_created,
            'status_updated': self.handle_status_updated,
        }
    
    def get_kafka_consumer(self):
        """Create and return Kafka consumer instance"""
        try:
            consumer = KafkaConsumer(
                settings.KAFKA_CONFIG['INCIDENT_TOPIC'],
                bootstrap_servers=settings.KAFKA_CONFIG['BOOTSTRAP_SERVERS'],
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                group_id='incident-management-consumer',
                auto_offset_reset='latest',
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
            )
            return consumer
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return None
    
    def start_consuming(self):
        """Start consuming messages from Kafka"""
        self.consumer = self.get_kafka_consumer()
        if not self.consumer:
            logger.error("Could not create Kafka consumer")
            return
        
        self.running = True
        logger.info("Starting Kafka consumer for incident events...")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        try:
            while self.running:
                try:
                    message_batch = self.consumer.poll(timeout_ms=1000)
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            self.process_message(message)
                except Exception as e:
                    logger.error(f"Error polling messages: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.shutdown()
    
    def process_message(self, message):
        """Process a single Kafka message"""
        try:
            event_data = message.value
            event_type = event_data.get('event_type')
            
            logger.info(f"Processing event: {event_type} for incident {event_data.get('incident_id')}")
            
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
                handler(event_data)
            else:
                logger.warning(f"No handler found for event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(f"Message content: {message.value}")
    
    def handle_incident_created(self, event_data: Dict[str, Any]):
        """Handle incident creation events"""
        try:
            incident_id = event_data['incident_id']
            logger.info(f"Handling incident creation: {incident_id}")
            
            # Send email notification to administrators
            self.send_incident_email_notification(event_data, 'created')
            
            # Check for high priority incidents and trigger escalation
            if event_data.get('priority') in ['high', 'critical']:
                self.trigger_escalation(event_data)
            
            # Log incident metrics
            self.log_incident_metrics(event_data, 'created')
            
            logger.info(f"Successfully processed incident creation: {incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling incident creation: {e}")
    
    def handle_status_updated(self, event_data: Dict[str, Any]):
        """Handle incident status update events"""
        try:
            incident_id = event_data['incident_id']
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            
            logger.info(f"Handling status update for incident {incident_id}: {old_status} -> {new_status}")
            
            # Send email notification for status change
            self.send_status_update_email(event_data)
            
            # If incident is resolved, send celebration notification
            if new_status == 'resolved':
                self.handle_incident_resolved(event_data)
            
            # Log status change metrics
            self.log_incident_metrics(event_data, 'status_updated')
            
            logger.info(f"Successfully processed status update for incident: {incident_id}")
            
        except Exception as e:
            logger.error(f"Error handling status update: {e}")
    
    def send_incident_email_notification(self, event_data: Dict[str, Any], action: str):
        """Send email notification for incident events"""
        try:
            subject = f"[Incident Management] New {action.title()} Incident #{event_data['incident_id']}"
            
            # Get incident details
            incident_id = event_data['incident_id']
            try:
                incident = Incident.objects.get(id=incident_id)
            except Incident.DoesNotExist:
                logger.warning(f"Incident {incident_id} not found in database")
                return
            
            # Prepare email context
            context = {
                'incident': incident,
                'event_data': event_data,
                'action': action,
            }
            
            # Get email recipients (administrators and assigned user)
            recipients = []
            
            # Add administrators
            admin_users = User.objects.filter(is_staff=True, email__isnull=False).exclude(email='')
            recipients.extend([user.email for user in admin_users])
            
            # Add assigned user
            if incident.assigned_to and incident.assigned_to.email:
                recipients.append(incident.assigned_to.email)
            
            if recipients:
                # For now, we'll log the email instead of sending
                # In production, uncomment the send_mail line
                logger.info(f"Would send email to: {recipients}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Incident: {incident.title} ({incident.priority} priority)")
                
                # send_mail(
                #     subject=subject,
                #     message=f"Incident #{incident.id}: {incident.title}\nPriority: {incident.priority}\nStatus: {incident.status}",
                #     from_email='incidents@company.com',
                #     recipient_list=recipients,
                #     fail_silently=False,
                # )
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def send_status_update_email(self, event_data: Dict[str, Any]):
        """Send email notification for status updates"""
        try:
            incident_id = event_data['incident_id']
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            
            subject = f"[Incident Management] Status Update - Incident #{incident_id}"
            message = f"Incident #{incident_id} status changed from '{old_status}' to '{new_status}'"
            
            logger.info(f"Status update notification: {message}")
            
        except Exception as e:
            logger.error(f"Error sending status update email: {e}")
    
    def trigger_escalation(self, event_data: Dict[str, Any]):
        """Trigger escalation for high priority incidents"""
        try:
            incident_id = event_data['incident_id']
            priority = event_data.get('priority')
            
            logger.warning(f"ESCALATION TRIGGERED: High priority incident #{incident_id} ({priority})")
            
            # Here you could:
            # - Send SMS to on-call engineers
            # - Create Slack notifications
            # - Trigger PagerDuty alerts
            # - Update external monitoring systems
            
            escalation_message = {
                'incident_id': incident_id,
                'priority': priority,
                'title': event_data.get('title'),
                'escalated_at': event_data.get('created_at'),
                'event_type': 'escalation_triggered'
            }
            
            # For demonstration, we'll just log the escalation
            logger.critical(f"🚨 ESCALATION: {escalation_message}")
            
        except Exception as e:
            logger.error(f"Error triggering escalation: {e}")
    
    def handle_incident_resolved(self, event_data: Dict[str, Any]):
        """Handle incident resolution"""
        try:
            incident_id = event_data['incident_id']
            logger.info(f"🎉 Incident #{incident_id} has been RESOLVED!")
            
            # Calculate resolution time, send notifications, update metrics
            # This is where you might:
            # - Update SLA dashboards
            # - Send thank you notifications
            # - Trigger post-incident review processes
            
        except Exception as e:
            logger.error(f"Error handling incident resolution: {e}")
    
    def log_incident_metrics(self, event_data: Dict[str, Any], event_type: str):
        """Log incident metrics for monitoring and analytics"""
        try:
            metrics = {
                'timestamp': event_data.get('created_at') or event_data.get('updated_at'),
                'incident_id': event_data['incident_id'],
                'event_type': event_type,
                'priority': event_data.get('priority'),
                'status': event_data.get('status') or event_data.get('new_status'),
                'category': event_data.get('category'),
            }
            
            # Log metrics (in production, send to monitoring system)
            logger.info(f"METRICS: {json.dumps(metrics)}")
            
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
    
    def shutdown(self, signum=None, frame=None):
        """Gracefully shutdown the consumer"""
        logger.info("Shutting down Kafka consumer...")
        self.running = False
        if self.consumer:
            self.consumer.close()
        logger.info("Kafka consumer stopped")


def run_consumer():
    """Entry point to run the consumer"""
    consumer = IncidentEventConsumer()
    consumer.start_consuming() 