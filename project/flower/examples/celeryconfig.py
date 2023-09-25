#broker_url = 'redis://localhost:6379/0'
broker_url = 'amqp://scraper:scraper@rabbitmq/scraper_app'
celery_result_backend = 'redis://localhost:6379/0'
task_send_sent_event = False
broker_connection_retry_on_startup = True
