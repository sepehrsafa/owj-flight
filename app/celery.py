from celery import Celery

app = Celery(
    "proj",
    broker="redis://default:7ki4TLMGy26YTlehKD9Wj4w5XXt0GlyZ@redis-18399.c322.us-east-1-2.ec2.cloud.redislabs.com:18399",
    backend="redis://default:7ki4TLMGy26YTlehKD9Wj4w5XXt0GlyZ@redis-18399.c322.us-east-1-2.ec2.cloud.redislabs.com:18399",
    include=["app.services.search.tasks"],
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
    celery_task_serializer="json",
    celery_accept_content=["json"],
    celery_result_serializer="json",
    celery_enable_utc=True,
)

if __name__ == "__main__":
    app.start()
