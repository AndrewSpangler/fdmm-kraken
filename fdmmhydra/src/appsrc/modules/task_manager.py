import datetime
import logging
from flask import Flask
from apscheduler import job
from apscheduler.schedulers.background import BackgroundScheduler

class BackgroundTask:
    def __init__(
            self,
            manager,
            name:str,
            task:callable,
            interval:int = 15,
            enabled:bool = True,
            delay_startup:bool = False
        ):
        self.manager = manager
        self.name = name
        self.enabled = enabled
        self.task = task
        self.job = None
        self.interval = interval
        self.running = False
        self.last_run = None
        
        if delay_startup:
            self.reschedule()
        else:
            self.trigger()

    def _handle_task(self) -> None:
        if not self.enabled:
            logging.info(f"Skipping disabled scheduled task {self.name} - {self.job.id}")
            return
        logging.info(f"Running scheduled task {self.name} - {self.job.id}")
        self.last_run = datetime.datetime.utcnow()
        self.running = True
        try:
            self.task()
        except:
            pass
        self.running = False

    def _reinit(self) -> None:
        try:
            self.manager.remove_job(self.job.id)
        except:
            pass
        self._handle_task()
        self.reschedule()
    
    def trigger(self) -> bool:
        """
        Returns a bool indicating if the trigger was successful
        """
        if not self.running:
            self.job = self.manager.add_job(
                self._reinit,
                'date',
                coalesce = True
            )
            return True
        return False
    
    def reschedule(self) -> None:
        """
        Reschedules the next run
        """
        try:
            self.manager.remove_job(self.job.id)
        except:
            pass
        self.job = self.manager.add_job(
            self._handle_task,
            'interval',
            minutes = self.interval,
            coalesce = True
        )
        self.running = False

class BackgroundTaskManager:
    def __init__(self, app:Flask):
        if hasattr(app, "task_manager"):
            raise AttributeError("Background task scheduler already initialized")
        self.app = app
        app.scheduler = BackgroundScheduler()
        app.task_manager = self       
        self.tasks = {}

    def create_task(
        self,
        name:str,
        task:callable,
        interval:int = 15,
        enabled:bool = True,
        delay_startup:bool = False
    ) -> BackgroundTask:
        task = BackgroundTask(
            self,
            name,
            task,
            interval = interval,
            enabled = enabled,
            delay_startup = delay_startup
        )
        self.tasks[name] = task
        return task

    def remove_job(self, job_id:str) -> None:
        self.app.scheduler.remove_job(job_id)

    def add_job(self, *args, **kwargs) -> job:
        return self.app.scheduler.add_job(*args, **kwargs)