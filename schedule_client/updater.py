from apscheduler.schedulers.background import BackgroundScheduler

from atproto_scheduler.settings import SCHEDULER_INTERVAL
from schedule_client.schedule_jobs import schedule_and_post


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        schedule_and_post,
        'interval',
        seconds=SCHEDULER_INTERVAL.seconds
    )
    scheduler.start()