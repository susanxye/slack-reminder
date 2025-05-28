import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import sys
import os

# Add the parent directory to the path so we can import slack_reminder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import slack_reminder


class TestSlackReminder(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_data = {
            "current_index": 2,
            "last_updated": "2025-05-28T10:00:00"
        }
        
    @patch('slack_reminder.DATA_FILE')
    @patch('builtins.open', new_callable=mock_open)
    @patch('slack_reminder.Path.exists')
    def test_load_captain_data_existing_file(self, mock_exists, mock_file, mock_data_file):
        """Test loading captain data when file exists."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.test_data)
        
        result = slack_reminder.load_captain_data()
        
        self.assertEqual(result["current_index"], 2)
        self.assertEqual(result["last_updated"], "2025-05-28T10:00:00")
        
    @patch('slack_reminder.DATA_FILE')
    @patch('slack_reminder.save_captain_data')
    @patch('slack_reminder.Path.exists')
    def test_load_captain_data_new_file(self, mock_exists, mock_save, mock_data_file):
        """Test loading captain data when file doesn't exist."""
        mock_exists.return_value = False
        
        result = slack_reminder.load_captain_data()
        
        self.assertEqual(result["current_index"], 0)
        self.assertIn("last_updated", result)
        mock_save.assert_called_once()
        
    @patch('builtins.open', new_callable=mock_open)
    @patch('slack_reminder.DATA_FILE')
    def test_save_captain_data(self, mock_data_file, mock_file):
        """Test saving captain data to file."""
        test_data = {"current_index": 3, "last_updated": "2025-05-28T11:00:00"}
        
        slack_reminder.save_captain_data(test_data)
        
        mock_file.assert_called_once()
        # Verify that json.dump was called with the correct data
        handle = mock_file.return_value.__enter__.return_value
        written_data = handle.write.call_args_list
        self.assertTrue(len(written_data) > 0)
        
    @patch('slack_reminder.save_captain_data')
    @patch('slack_reminder.load_captain_data')
    def test_get_next_captain(self, mock_load, mock_save):
        """Test getting the next captain in rotation."""
        mock_load.return_value = {"current_index": 1, "last_updated": "2025-05-28T10:00:00"}
        
        captain = slack_reminder.get_next_captain()
        
        # Should return the captain at index 1
        expected_captain = slack_reminder.TEAM_MEMBERS[1]
        self.assertEqual(captain, expected_captain)
        
        # Should save data with incremented index
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(saved_data["current_index"], 2)
        
    @patch('slack_reminder.save_captain_data')
    @patch('slack_reminder.load_captain_data')
    def test_get_next_captain_wrap_around(self, mock_load, mock_save):
        """Test captain rotation wraps around to beginning."""
        # Set to last team member
        last_index = len(slack_reminder.TEAM_MEMBERS) - 1
        mock_load.return_value = {"current_index": last_index, "last_updated": "2025-05-28T10:00:00"}
        
        captain = slack_reminder.get_next_captain()
        
        # Should return the last captain
        expected_captain = slack_reminder.TEAM_MEMBERS[last_index]
        self.assertEqual(captain, expected_captain)
        
        # Should wrap around to index 0
        mock_save.assert_called_once()
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(saved_data["current_index"], 0)
        
    @patch('slack_reminder.requests.post')
    @patch('slack_reminder.get_next_captain')
    def test_send_deployment_captain_reminder_success(self, mock_get_captain, mock_post):
        """Test successful sending of deployment captain reminder."""
        mock_get_captain.return_value = "<@U123456789>"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Should not raise any exception
        slack_reminder.send_deployment_captain_reminder()
        
        # Verify the request was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        self.assertEqual(call_args[0][0], slack_reminder.WEBHOOK_URL)
        
        # Check headers
        self.assertEqual(call_args[1]["headers"]["Content-Type"], "application/json")
        
        # Check payload contains the captain
        payload_data = json.loads(call_args[1]["data"])
        self.assertIn("<@U123456789>", payload_data["text"])
        
    @patch('slack_reminder.requests.post')
    @patch('slack_reminder.get_next_captain')
    @patch('slack_reminder.logger')
    def test_send_deployment_captain_reminder_failure(self, mock_logger, mock_get_captain, mock_post):
        """Test handling of failed reminder sending."""
        mock_get_captain.return_value = "<@U123456789>"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response
        
        slack_reminder.send_deployment_captain_reminder()
        
        # Should log an error
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("Error sending message", error_call)
        self.assertIn("404", error_call)
        
    @patch('slack_reminder.requests.post')
    @patch('slack_reminder.get_next_captain')
    @patch('slack_reminder.logger')
    def test_send_deployment_captain_reminder_exception(self, mock_logger, mock_get_captain, mock_post):
        """Test handling of exceptions during reminder sending."""
        mock_get_captain.return_value = "<@U123456789>"
        mock_post.side_effect = Exception("Network error")
        
        slack_reminder.send_deployment_captain_reminder()
        
        # Should log an error
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("Error in send_deployment_captain_reminder", error_call)
        
    def test_team_members_not_empty(self):
        """Test that team members list is not empty."""
        self.assertTrue(len(slack_reminder.TEAM_MEMBERS) > 0)
        
    def test_team_members_format(self):
        """Test that team members are in correct Slack format."""
        for member in slack_reminder.TEAM_MEMBERS:
            self.assertTrue(member.startswith("<@"))
            self.assertTrue(member.endswith(">"))
            
    def test_webhook_url_configured(self):
        """Test that webhook URL is configured."""
        self.assertTrue(slack_reminder.WEBHOOK_URL.startswith("https://hooks.slack.com/"))


if __name__ == '__main__':
    unittest.main()
