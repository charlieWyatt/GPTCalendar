import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from configs.config import CREDENTIALS_FILE_PATH, TIMEZONE, USERNAME


class Calendar:
    def __init__(self, credentials_file, calendar_id, timezone='Australia/Sydney'):
        self.timezone = timezone
        self.calendar_id = calendar_id
        self.service = self._create_service(credentials_file)

    def _create_service(self, credentials_file):
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=scopes
        )
        service = build('calendar', 'v3', credentials=credentials)
        return service

    def get_calendar_events(self, start_range, end_range):
        from_dt = start_range.isoformat() + 'Z'
        to_dt = end_range.isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=from_dt,
                # timeMax=to_dt + timedelta(days=1),
                timeZone=self.timezone
            ).execute()

            events = events_result.get('items', [])

            calendar_events = []
            for event in events:
                summary = event.get('summary', 'No summary')
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                calendar_events.append({
                    'summary': summary,
                    'start': start,
                    'end': end
                })

            return calendar_events

        except HttpError as e:
            print(f"An error occurred: {e}")

    def add_event(self, event_summary, start_datetime, end_datetime, event_location):
        event = {
            'summary': event_summary,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': self.timezone,
            },
            'location': event_location,
        }

        try:
            self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            return "Event added successfully."
        except HttpError as e:
            return (f"Failed to add event to the calendar: {e}")

    def update_event(self, old_event_summary, old_start, old_end, old_location, new_event_summary = None, new_start = None, new_end = None, new_location = None):
      # if they dont want to update a field, assume it is the same as it was previously
      if new_event_summary is None:
        new_event_summary = old_event_summary
      if new_start is None:
        new_start = old_start
      if new_end is None:
        new_end = old_end
      if new_location is None:
        new_location = old_location

      # loops through all the events at the one time period
      events = self.get_calendar_events(old_start, old_end)
      if events is None:
         return "No events found"
      foundEvent = None
      print(events)
      print(old_start)
      print(old_end)
      for event in events:
        # finds the closest match
        if event['location'] == old_location:
          foundEvent = event
        if event['summary'] == old_event_summary:
          foundEvent = event
        if event['summary'] == old_event_summary and event['location'] == old_location:
          # found the exact match
          foundEvent = event
          break
      foundEvent['summary'] = new_event_summary
      foundEvent['start'] = new_start
      foundEvent['end'] = new_end
      foundEvent['location'] = new_location

      try:
          self.service.events().update(calendarId=self.calendar_id, eventId=foundEvent['id'], body=foundEvent).execute()
          print("Event updated successfully.")
      except HttpError as e:
          print(f"Failed to update event: {e}")

    def delete_event(self, event_id):
        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
            print("Event deleted successfully.")
        except HttpError as e:
            print(f"Failed to delete event: {e}")

# # Example usage
# credentials_file = CREDENTIALS_FILE_PATH
# timezone = TIMEZONE
# username = USERNAME

# start_range = datetime.datetime(2023, 6, 26, 0, 0)
# end_range = datetime.datetime(2023, 6, 27, 0, 0)

# calendar = Calendar(credentials_file, username, timezone)
# events = calendar.get_calendar_events(start_range, end_range)

# for event in events:
#     print("Event Summary:", event['summary'])
#     print("Event Start:", event['start'])
#     print("Event End:", event['end'])
#     print("-------------------")

# calendar.add_event("BEST EVENT EVER", datetime.datetime(2023, 6, 26, 11, 40), datetime.datetime(2023, 6, 26, 11, 45))
