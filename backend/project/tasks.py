from celery import shared_task
from celery.contrib.abortable import AbortableTask

from time import sleep

#from .extensions import db


@shared_task(bind=True, base=AbortableTask)
def add_user(self, form_data):
    #db.session.add(User(name=form_data['name']))
    #db.session.commit()
    
    for i in range(1):
        sleep(1)
        if self.is_aborted():
            return 'TASK STOPPED!'
    return 'DONE!'