# Slack Reminder App

A Python application that sends automated deployment captain reminders to Slack channels on a scheduled basis.

## Features

- **Deployment Captain Rotation**: Automatically rotates through team members for deployment captain duties
- **Scheduled Reminders**: Sends reminders every Monday at 10:00 AM
- **Persistent State**: Maintains captain rotation state between restarts
- **Slack Integration**: Uses Slack webhooks for message delivery
- **Logging**: Comprehensive logging for monitoring and debugging

## Setup

### Prerequisites

- Python 3.7+
- Slack workspace with webhook permissions
- Access to create Slack webhook URLs

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd slack_work
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Slack webhook:
   - Create a Slack app in your workspace
   - Add incoming webhook integration
   - Copy the webhook URL
   - Update `WEBHOOK_URL` in `slack_reminder.py`

4. Update team members:
   - Modify the `TEAM_MEMBERS` list in `slack_reminder.py`
   - Use Slack user IDs in the format `<@USER_ID>`

### Usage

Run the application:
```bash
python slack_reminder.py
```

The application will:
- Start the scheduler
- Send reminders every Monday at 10:00 AM
- Maintain captain rotation state in `deployment_captain_data.json`

### Configuration

#### Environment Variables

You can set the following environment variables:

- `SLACK_WEBHOOK_URL`: Slack webhook URL (overrides hardcoded value)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `REMINDER_TIME`: Time to send reminders (default: "10:00")
- `REMINDER_DAY`: Day to send reminders (default: "monday")

#### Team Members

Update the `TEAM_MEMBERS` list in `slack_reminder.py` with your team's Slack user IDs.

## File Structure

```
slack_work/
├── slack_reminder.py          # Main application file
├── deployment_captain_data.json  # Captain rotation state (auto-generated)
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
└── tests/                   # Test files
    └── test_slack_reminder.py
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Run linting with:

```bash
flake8 slack_reminder.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Deployment

### Docker

Build and run with Docker:

```bash
docker build -t slack-reminder .
docker run -d --name slack-reminder slack-reminder
```

### Systemd Service

Create a systemd service for automatic startup:

```bash
sudo cp slack-reminder.service /etc/systemd/system/
sudo systemctl enable slack-reminder
sudo systemctl start slack-reminder
```

## Troubleshooting

### Common Issues

1. **Webhook URL not working**: Verify the webhook URL is correct and the Slack app has proper permissions
2. **Captain rotation not persisting**: Check file permissions for `deployment_captain_data.json`
3. **Schedule not running**: Ensure the application stays running (consider using a process manager)

### Logs

Check application logs for debugging:
```bash
tail -f slack_reminder.log
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the repository or contact the development team.
