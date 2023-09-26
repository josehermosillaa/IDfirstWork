from django_cron import CronJobBase, Schedule
from django.core import management
from django.core.management.commands import loaddata
class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.my_cron_job'    # a unique code

    def do(self):
        management.call_command('load_data_cementera', verbosity=0)