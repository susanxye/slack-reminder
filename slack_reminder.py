import schedule
import time
import requests
import json
import datetime
from pathlib import Path
import logging

# Configuration
WEBHOOK_URL = "" 

TEAM_MEMBERS = [
    "<@UABCD>",
    "<@UEFGH>"
]

# File to store the current captain index
DATA_FILE = Path("deployment_captain_data.json")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_captain_data():
    """Load the current captain index from file or initialize if not exists"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        # Start with the first team member
        initial_data = {"current_index": 0, "last_updated": datetime.datetime.now().isoformat()}
        save_captain_data(initial_data)
        return initial_data

def save_captain_data(data):
    """Save the current captain index to file"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_next_captain():
    """Get the next captain in the rotation"""
    data = load_captain_data()
    current_index = data["current_index"]
    
    # Validate and fix current_index if it's out of bounds
    if current_index >= len(TEAM_MEMBERS) or current_index < 0:
        logger.warning(f"Invalid current_index {current_index}, resetting to 0")
        current_index = 0
    
    # Get the current captain
    current_captain = TEAM_MEMBERS[current_index]
    # Update to the next captain for next time
    next_index = (current_index + 1) % len(TEAM_MEMBERS)
    data["current_index"] = next_index
    data["last_updated"] = datetime.datetime.now().isoformat()
    save_captain_data(data)
    return current_captain

def send_deployment_captain_reminder():
    """Send a reminder about the current deployment captain to Slack, including the next two captains"""
    try:
        # Get current and next captain indices
        data = load_captain_data()
        current_index = data["current_index"]
        
        # Validate and fix current_index if it's out of bounds
        if current_index >= len(TEAM_MEMBERS) or current_index < 0:
            logger.warning(f"Invalid current_index {current_index}, resetting to 0")
            current_index = 0
            data["current_index"] = current_index
            save_captain_data(data)
        
        current_captain = TEAM_MEMBERS[current_index]
        next_index = (current_index + 1) % len(TEAM_MEMBERS)
        next_captain = TEAM_MEMBERS[next_index]
        next_next_index = (current_index + 2) % len(TEAM_MEMBERS)
        next_next_captain = TEAM_MEMBERS[next_next_index]

        # Update to the next captain for next time
        data["current_index"] = next_index
        data["last_updated"] = datetime.datetime.now().isoformat()
        save_captain_data(data)

        # Create the message payload
        payload = {
            "text": (
                f"{current_captain} is this week's Deployment Captain.\n"
                f"Next week's Deployment Captain: {next_captain}\n"
                f"Following week's Deployment Captain: {next_next_captain}\n"
            )
        }

        # Send the message using the Webhook URL
        response = requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )

        # Check for errors
        if response.status_code != 200:
            logger.error(f"Error sending message: {response.status_code}, {response.text}")
        else:
            logger.info(f"Message sent successfully. Captain: {current_captain}, Next: {next_captain}, Following: {next_next_captain}")

    except Exception as e:
        logger.error(f"Error in send_deployment_captain_reminder: {e}")

#schedule.every(1).minutes.do(send_deployment_captain_reminder)
schedule.every().monday.at("15:00").do(send_deployment_captain_reminder)

# Run the scheduler
if __name__ == "__main__":
    logger.info("Starting the deployment captain reminder scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(300)  # 300 seconds = 5 minutes
