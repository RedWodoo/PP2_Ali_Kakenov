# dates.py

from datetime import datetime, timedelta

# 1. Subtract five days from current date
today = datetime.now()
print("Now:", today)
print("Five days ago:", today - timedelta(days=5))

# 2. Yesterday, today, tomorrow
print("Yesterday:", today - timedelta(days=1))
print("Today:", today)
print("Tomorrow:", today + timedelta(days=1))

# 3. Drop microseconds
print("Without microseconds:", today.replace(microsecond=0))

# 4. Difference between two dates in seconds
date1 = datetime(2025, 1, 1)
date2 = datetime(2025, 1, 10)
difference = (date2 - date1).total_seconds()
print("Difference in seconds:", difference)