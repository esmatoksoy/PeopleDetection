import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from SendMail import MailPhotoSender

class GraphGenerator:
    def __init__(self, csv_file, env_file, smtp_server="smtp.gmail.com", smtp_port=587):
        self.csv_file = csv_file
        self.env_file = env_file
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.data = None
        self.graph_path = "graph_output.png"

    def load_data(self):
        # Load the CSV file
        self.data = pd.read_csv(self.csv_file, parse_dates=['entry_time', 'exit_time'])
        # Calculate stay time in seconds for each visitor
        self.data['stay_time'] = (self.data['exit_time'] - self.data['entry_time']).dt.total_seconds()
        # Sort data by stay time
        self.data = self.data.sort_values(by='stay_time').reset_index(drop=True)
        # Create cumulative count of people for each stay time
        self.data['CumulativePeople'] = range(1, len(self.data) + 1)
        # Format stay time for x-axis labels
        self.data['StayTime'] = self.data['stay_time'].astype(int).astype(str) + ' sec'
        # Save the cleaned file (optional)
        self.data[['StayTime', 'CumulativePeople']].to_csv(self.csv_file, index=False)

    def generate_graph(self):
        # Plotting
        plt.style.use('ggplot')
        plt.figure(figsize=(12, 7))
        plt.plot(self.data['StayTime'], self.data['CumulativePeople'], marker='o', color='teal', alpha=0.9, linewidth=2, markersize=5)
        # Add point annotations
        for i, val in enumerate(self.data['CumulativePeople']):
            plt.text(i, val + 0.3, f'{val}', ha='center', fontsize=10)
        plt.xlabel('Stay Time (seconds)')
        plt.ylabel('Cumulative Number of People')
        plt.title('Cumulative Number of People by Stay Time')
        plt.xticks(rotation=45, ha='right')
        plt.savefig(self.graph_path)
        plt.show()

    def send_graph_via_email(self):
        # Load environment variables
        load_dotenv(dotenv_path=self.env_file)
        sender_email = os.getenv("FROM_EMAIL")
        recipient_email = os.getenv("TO_EMAIL")
        password = os.getenv("PASSWORD")
        subject = "Graph Output"
        body = "Please find the attached graph generated from visits_today.csv."
        # Initialize the MailPhotoSender class
        mail_sender = MailPhotoSender(sender_email, password, self.smtp_server, self.smtp_port)
        # Send the email with the graph attachment
        mail_sender.send_mail_with_image(
            subject=subject,
            body=body,
            to_email=recipient_email,
            image_path=self.graph_path
        )

if __name__ == "__main__":

    graph_generator = GraphGenerator(csv_file="visits_today.csv", env_file="infos.env")
    # Load data, generate graph, and send it via email
    #add delay to ensure the CSV file is ready
    time.sleep(2)  # Adjust the delay as needed
    # Load data from CSV, generate the graph, and send it via email
    graph_generator.load_data()
    graph_generator.generate_graph()
    graph_generator.send_graph_via_email()
