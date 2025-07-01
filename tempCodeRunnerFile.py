import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
from datetime import datetime
from SendMail import MailPhotoSender

# Load the CSV file
data = pd.read_csv('visits_today.csv', parse_dates=['entry_time', 'exit_time'])

# Calculate stay time in seconds for each visitor
data['stay_time'] = (data['exit_time'] - data['entry_time']).dt.total_seconds()

# Sort data by stay time
data = data.sort_values(by='stay_time').reset_index(drop=True)

# Create cumulative count of people for each stay time
data['CumulativePeople'] = range(1, len(data) + 1)

# Format stay time for x-axis labels
data['StayTime'] = data['stay_time'].astype(int).astype(str) + ' sec'

# Save the cleaned file (optional, for your existing code)
data[['StayTime', 'CumulativePeople']].to_csv('visits_today.csv', index=False)

# Plotting
plt.style.use('ggplot')
plt.figure(figsize=(12, 7))
# Plotting as a line graph
plt.plot(data['StayTime'], data['CumulativePeople'], marker='o', color='teal', alpha=0.9, linewidth=2, markersize=5 )

# Add point annotations
for i, val in enumerate(data['CumulativePeople']):
    plt.text(i, val + 0.3, f'{val}', ha='center', fontsize=10)

plt.xlabel('Stay Time (seconds)')
plt.ylabel('Cumulative Number of People')
plt.title('Cumulative Number of People by Stay Time')
plt.xticks(rotation=45, ha='right' )

plt.savefig('graph_output.png')
plt.show()