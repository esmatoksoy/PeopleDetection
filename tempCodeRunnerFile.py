import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
# Load the CSV file
csv_file = 'visits_today.csv'
data = pd.read_csv(csv_file)

# Ensure the CSV has the required columns
if len(data.columns) < 2:
    raise ValueError("The CSV file must have at least two columns: one for labels and one for values.")

# Extract labels and values
labels = data.iloc[:, 0]  # First column for labels
values = data.iloc[:, 1]  # Second column for values

# Apply a style
plt.style.use('ggplot')  # Use a valid matplotlib style

# Create the graph
plt.figure(figsize=(12, 7))
bars = plt.bar(labels, values, color=plt.cm.Paired.colors[:len(labels)])
plt.xlabel('Labels', fontsize=14)
plt.ylabel('Values', fontsize=14)
plt.title('Graph from visits_today.csv', fontsize=16)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add value annotations on top of the bars
for bar in bars:
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             f'{bar.get_height():.0f}', ha='center', fontsize=10)

plt.tight_layout()

# Save and show the graph
plt.savefig('graph_output.png')
plt.show()