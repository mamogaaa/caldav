#!/usr/bin/env python3
"""
Test script for mail.ru CalDAV access
"""

import sys
import configparser
from datetime import datetime, timedelta, date
import caldav
from caldav.davclient import DAVClient
from caldav.objects import Calendar

def test_mail_ru_caldav(config_path):
    """Test mail.ru CalDAV with direct calendar access."""
    
    # Read configuration
    config = configparser.ConfigParser()
    config.read(config_path)
    
    caldav_config = config['caldav']
    url = caldav_config.get('url')
    username = caldav_config.get('username')
    password = caldav_config.get('password')
    
    print(f"Testing CalDAV connection to: {url}")
    print(f"Username: {username}")
    
    # Connect to CalDAV server
    client = DAVClient(url=url, username=username, password=password)
    print(f"Client incompatibilities: {getattr(client, 'incompatibilities', 'None')}")
    
    try:
        # Try direct calendar access instead of principal discovery
        calendar = Calendar(client=client, url=url)
        print("Calendar object created successfully")
        
        # Get current week date range
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        start_datetime = datetime.combine(week_start, datetime.min.time())
        end_datetime = datetime.combine(week_end, datetime.max.time())
        
        print(f"Searching for events from {start_datetime.date()} to {end_datetime.date()}")
        
        # Try calendar search with explicit event type
        try:
            events = calendar.search(
                start=start_datetime,
                end=end_datetime,
                event=True,
                expand=True
            )
            
            print(f"Found {len(events)} events")
            
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
                
                print()
                
        except Exception as search_error:
            print(f"Calendar search failed: {search_error}")
            return False
            
    except Exception as e:
        print(f"Calendar access failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_mail_ru.py config.mail.ini")
        sys.exit(1)
    
    config_path = sys.argv[1]
    success = test_mail_ru_caldav(config_path)
    
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")
        sys.exit(1)