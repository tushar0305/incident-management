from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging
from incidents.kafka_consumer import run_consumer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start the Kafka consumer for incident events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--log-level',
            type=str,
            default='INFO',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Set the logging level (default: INFO)'
        )
        
    def handle(self, *args, **options):
        # Set logging level
        log_level = getattr(logging, options['log_level'].upper())
        logging.getLogger().setLevel(log_level)
        
        self.stdout.write(
            self.style.SUCCESS('Starting Kafka consumer for incident events...')
        )
        
        try:
            # Check if Kafka configuration is available
            if not hasattr(settings, 'KAFKA_CONFIG'):
                raise CommandError('KAFKA_CONFIG not found in Django settings')
            
            # Run the consumer
            run_consumer()
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nKafka consumer interrupted by user')
            )
        except Exception as e:
            raise CommandError(f'Error running Kafka consumer: {e}')
        finally:
            self.stdout.write(
                self.style.SUCCESS('Kafka consumer stopped')
            ) 