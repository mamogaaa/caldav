#!/usr/bin/env python3
"""
CalDAV Calendar Data Fetcher

This script fetches calendar data from a CalDAV server for the previous, current, and next weeks.
Usage: python3 fetch_calendar_weeks.py /path/to/config.ini
"""

import sys
import os
import configparser
from datetime import datetime, timedelta, date
import caldav
from caldav.davclient import DAVClient


def get_week_bounds(target_date):
    """Get the start and end datetime for the week containing the target date."""
    # Find Monday of the week containing target_date
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    # Convert to datetime objects for the full day range
    start_datetime = datetime.combine(week_start, datetime.min.time())
    end_datetime = datetime.combine(week_end, datetime.max.time())
    
    return start_datetime, end_datetime


def fetch_calendar_data(config_path):
    """Fetch calendar data for prev, current, and next weeks."""
    
    # Read configuration
    config = configparser.ConfigParser()
    config.read(config_path)
    
    if 'caldav' not in config:
        raise ValueError("No [caldav] section found in config file")
    
    caldav_config = config['caldav']
    url = caldav_config.get('url')
    username = caldav_config.get('username')
    password = caldav_config.get('password')
    
    if not all([url, username, password]):
        raise ValueError("Missing required config: url, username, or password")
    
    # Connect to CalDAV server
    client = DAVClient(url=url, username=username, password=password)
    
    try:
        # Get principal and calendars
        principal = client.principal()
        calendars = principal.calendars()
        
        if not calendars:
            print("No calendars found")
            return
        
        print(f"Found {len(calendars)} calendar(s)")
        
        # Get date ranges for the three weeks
        today = date.today()
        
        # Previous week
        prev_week_start, prev_week_end = get_week_bounds(today - timedelta(days=7))
        # Current week
        curr_week_start, curr_week_end = get_week_bounds(today)
        # Next week
        next_week_start, next_week_end = get_week_bounds(today + timedelta(days=7))
        
        # Fetch events for all calendars
        for calendar in calendars:
            print(f"\n{'='*60}")
            print(f"Calendar: {calendar.name}")
            print(f"{'='*60}")
            
            # Fetch events for each week
            weeks = [
                ("Previous Week", prev_week_start, prev_week_end),
                ("Current Week", curr_week_start, curr_week_end),
                ("Next Week", next_week_start, next_week_end)
            ]
            
            for week_name, start_date, end_date in weeks:
                print(f"\n{week_name} ({start_date.date()} to {end_date.date()}):")
                print("-" * 50)
                
                try:
                    # Search for events in the date range
                    events = calendar.search(
                        start=start_date,
                        end=end_date,
                        event=True,
                        expand=True
                    )
                    
                    if not events:
                        print("  No events found")
                        continue
                    
                    # Sort events by start time
                    events.sort(key=lambda e: e.component.get('dtstart', datetime.min).dt if e.component.get('dtstart') else datetime.min)
                    
                    for event in events:
                        component = event.component
                        summary = component.get('summary', 'No title')
                        dtstart = component.get('dtstart')
                        dtend = component.get('dtend')
                        
                        if dtstart:
                            start_str = dtstart.dt.strftime('%Y-%m-%d %H:%M') if hasattr(dtstart.dt, 'strftime') else str(dtstart.dt)
                        else:
                            start_str = "No start time"
                        
                        if dtend:
                            end_str = dtend.dt.strftime('%Y-%m-%d %H:%M') if hasattr(dtend.dt, 'strftime') else str(dtend.dt)
                        else:
                            end_str = "No end time"
                        
                        print(f"  • {summary}")
                        print(f"    {start_str} - {end_str}")
                        
                        # Show location if available
                        location = component.get('location')
                        if location:
                            print(f"    Location: {location}")
                        
                        # Show description if available (truncated)
                        description = component.get('description')
                        if description:
                            desc_str = str(description)[:100]
                            if len(str(description)) > 100:
                                desc_str += "..."
                            print(f"    Description: {desc_str}")
                        
                        print()
                
                except Exception as e:
                    print(f"  Error fetching events: {e}")
                    continue
    
    except Exception as e:
        print(f"Error connecting to CalDAV server: {e}")
        return False
    
    return True


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python3 fetch_calendar_weeks.py /path/to/config.ini")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    if not os.path.exists(config_path):
        print(f"Error: Config file '{config_path}' not found")
        sys.exit(1)
    
    try:
        success = fetch_calendar_data(config_path)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()