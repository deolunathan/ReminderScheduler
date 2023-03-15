import schedule
from plyer import notification
import datetime
import geopy.distance
import requests
import time


class Reminder:
    def __init__(self, message, reminder_type, interval, start_time=None, end_time=None, location=None, radius=None):
        self.message = message
        self.reminder_type = reminder_type
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.radius = radius

    def reminder(self):
        notification.notify(
            title="Reminder",
            message=self.message,
            timeout=10
        )

    def schedule_reminder(self):
        if self.location:
            schedule_method = self.schedule_location_reminder
        else:
            schedule_method = self.schedule_time_reminder
        schedule_method()

    def schedule_time_reminder(self):
        def trigger_reminder():
            self.reminder()
            if self.end_time and datetime.datetime.now().strftime("%H:%M") >= self.end_time:
                schedule.clear('trigger_reminder')
        schedule.every(self.interval).days.at(self.start_time).do(trigger_reminder).tag('trigger_reminder')
        if self.end_time:
            schedule.every(self.interval).days.at(self.end_time).do(schedule.clear, 'trigger_reminder')

    def schedule_location_reminder(self):
        def trigger_reminder():
            # get current location
            response = requests.get('https://ipapi.com/api/check?format=json')
            data = response.json()
            current_location = (data['latitude'], data['longitude'])
            # calculate distance from reminder location
            reminder_location = (self.location['latitude'], self.location['longitude'])
            distance = geopy.distance.distance(current_location, reminder_location).meters
            if distance <= self.radius:
                # trigger reminder if within radius
                self.reminder()
                if self.end_time and datetime.datetime.now().strftime("%H:%M") >= self.end_time:
                    schedule.clear('trigger_reminder')
        schedule.every(self.interval).days.at(self.start_time).do(trigger_reminder).tag('trigger_reminder')
        if self.end_time:
            schedule.every(self.interval).days.at(self.end_time).do(schedule.clear, 'trigger_reminder')

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


# create a reminder object
my_reminder = Reminder(
    message="Remember to drink water",
    reminder_type="time",
    interval=1,
    start_time="18:38",
    end_time="18:38",
)

# schedule the reminder
my_reminder.schedule_reminder()

# run the scheduler once immediately
schedule.run_all()

# run the scheduler continuously
my_reminder.run_scheduler()
