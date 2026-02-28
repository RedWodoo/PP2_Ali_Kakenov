from datetime import datetime, timedelta

today = datetime.now()
print("Now:", today)
print("Five days ago:", today - timedelta(days=5))

print("Yesterday:", today - timedelta(days=1))
print("Today:", today)
print("Tomorrow:", today + timedelta(days=1))

print("Without microseconds:", today.replace(microsecond=0))

date1 = datetime(2025, 1, 1)
date2 = datetime(2025, 1, 10)
difference = (date2 - date1).total_seconds()
print("Difference in seconds:", difference)
