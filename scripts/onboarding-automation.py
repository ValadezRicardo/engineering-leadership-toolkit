"""
Onboarding Automation Script

Automates the technical onboarding process for new engineering team members.
Integrates with various tools and platforms to streamline setup and tracking.

Author: Ricardo Valadez
Purpose: Reduce onboarding time and ensure consistent experience
Last Updated: 2024-05-24
"""

import os
import json
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import subprocess
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('onboarding.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class NewEmployee:
    """Data class for new employee information"""
    first_name: str
    last_name: str
    email: str
    role: str
    team: str
    start_date: str
    manager_email: str
    buddy_email: Optional[str] = None
    github_username: Optional[str] = None
    slack_user_id: Optional[str] = None
    employee_id: Optional[str] = None

@dataclass
class OnboardingTask:
    """Data class for onboarding tasks"""
    id: str
    title: str
    description: str
    owner: str
    due_date: str
    status: str = "pending"
    dependencies: List[str] = None
    automation_script: Optional[str] = None

class OnboardingConfig:
    """Configuration management for onboarding automation"""
    
    def __init__(self, config_file: str = "onboarding_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found. Using defaults.")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration if file doesn't exist"""
        return {
            'company': {
                'name': 'Your Company',
                'domain': 'company.com',
                'slack_workspace': 'company.slack.com'
            },
            'github': {
                'org': 'your-org',
                'base_url': 'https://api.github.com'
            },
            'jira': {
                'url': 'https://company.atlassian.net',
                'project_key': 'ONBOARD'
            },
            'aws': {
                'region': 'us-west-2',
                'account_id': '123456789012'
            },
            'email': {
                'smtp_server': 'smtp.company.com',
                'smtp_port': 587,
                'from_address': 'engineering@company.com'
            },
            'teams': {
                'backend': ['python', 'postgres', 'redis', 'aws'],
                'frontend': ['react', 'typescript', 'webpack'],
                'fullstack': ['python', 'react', 'postgres', 'aws'],
                'devops': ['terraform', 'kubernetes', 'aws', 'monitoring']
            }
        }

class GitHubIntegration:
    """GitHub API integration for repository access and team management"""
    
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def add_user_to_org(self, username: str) -> bool:
        """Add user to GitHub organization"""
        url = f"{self.base_url}/orgs/{self.org}/memberships/{username}"
        data = {'role': 'member'}
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                logger.info(f"Added {username} to GitHub org {self.org}")
                return True
            else:
                logger.error(f"Failed to add {username} to org: {response.text}")
                return False
        except Exception as e:
            logger.error(f"GitHub API error: {e}")
            return False
    
    def add_user_to_team(self, username: str, team_name: str) -> bool:
        """Add user to specific GitHub team"""
        # First, get team ID
        team_id = self._get_team_id(team_name)
        if not team_id:
            return False
        
        url = f"{self.base_url}/teams/{team_id}/memberships/{username}"
        data = {'role': 'member'}
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                logger.info(f"Added {username} to team {team_name}")
                return True
            else:
                logger.error(f"Failed to add {username} to team: {response.text}")
                return False
        except Exception as e:
            logger.error(f"GitHub team API error: {e}")
            return False
    
    def _get_team_id(self, team_name: str) -> Optional[int]:
        """Get team ID by name"""
        url = f"{self.base_url}/orgs/{self.org}/teams"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                teams = response.json()
                for team in teams:
                    if team['name'].lower() == team_name.lower():
                        return team['id']
            return None
        except Exception as e:
            logger.error(f"Error getting team ID: {e}")
            return None
    
    def grant_repository_access(self, username: str, repositories: List[str]) -> Dict[str, bool]:
        """Grant user access to specified repositories"""
        results = {}
        
        for repo in repositories:
            url = f"{self.base_url}/repos/{self.org}/{repo}/collaborators/{username}"
            data = {'permission': 'write'}
            
            try:
                response = requests.put(url, headers=self.headers, json=data)
                success = response.status_code in [200, 201, 204]
                results[repo] = success
                
                if success:
                    logger.info(f"Granted {username} access to {repo}")
                else:
                    logger.error(f"Failed to grant access to {repo}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error granting access to {repo}: {e}")
                results[repo] = False
        
        return results

class SlackIntegration:
    """Slack API integration for user management and notifications"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://slack.com/api'
    
    def send_welcome_message(self, user_id: str, employee: NewEmployee) -> bool:
        """Send welcome message to new employee"""
        welcome_text = f"""
🎉 Welcome to the team, {employee.first_name}!

I'm here to help you get started. Here's what's happening:

📅 **Your onboarding schedule:**
• Week 1: Environment setup and team introductions
• Week 2: First projects and code reviews
• Week 3: Deeper technical dive and architecture overview
• Month 1: Performance check-in with your manager

👥 **Key people:**
• **Manager:** <@{self._get_user_id_by_email(employee.manager_email)}>
• **Onboarding Buddy:** <@{self._get_user_id_by_email(employee.buddy_email) if employee.buddy_email else 'TBD'}>

🔗 **Important links:**
• Engineering Handbook: https://handbook.company.com
• Team Calendar: https://calendar.company.com
• Development Setup: https://github.com/your-org/dev-setup

💬 **Key channels to join:**
• #engineering-general
• #team-{employee.team}
• #random
• #announcements

Questions? Just ask! We're here to help. 🚀
        """
        
        return self._send_direct_message(user_id, welcome_text)
    
    def add_user_to_channels(self, user_id: str, team: str) -> Dict[str, bool]:
        """Add user to relevant Slack channels"""
        channels = [
            'engineering-general',
            'announcements',
            'random',
            f'team-{team}',
            'code-reviews',
            'tech-talks'
        ]
        
        results = {}
        for channel in channels:
            channel_id = self._get_channel_id(channel)
            if channel_id:
                success = self._add_user_to_channel(user_id, channel_id)
                results[channel] = success
            else:
                results[channel] = False
                logger.warning(f"Channel {channel} not found")
        
        return results
    
    def notify_team_about_new_member(self, team_channel: str, employee: NewEmployee) -> bool:
        """Notify team about new member joining"""
        notification_text = f"""
👋 **New team member alert!**

Please welcome {employee.first_name} {employee.last_name} who's joining us as a {employee.role}!

**Start date:** {employee.start_date}
**Manager:** <@{self._get_user_id_by_email(employee.manager_email)}>

{employee.first_name} will be going through onboarding over the next few weeks. Please help them feel welcome and don't hesitate to introduce yourselves! 

Looking forward to having you on the team, <@{employee.slack_user_id}>! 🎉
        """
        
        channel_id = self._get_channel_id(team_channel)
        if channel_id:
            return self._send_channel_message(channel_id, notification_text)
        return False
    
    def _send_direct_message(self, user_id: str, text: str) -> bool:
        """Send direct message to user"""
        url = f"{self.base_url}/chat.postMessage"
        data = {
            'channel': user_id,
            'text': text,
            'as_user': True
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            success = response.json().get('ok', False)
            if success:
                logger.info(f"Sent welcome message to {user_id}")
            else:
                logger.error(f"Failed to send message: {response.text}")
            return success
        except Exception as e:
            logger.error(f"Slack API error: {e}")
            return False
    
    def _send_channel_message(self, channel_id: str, text: str) -> bool:
        """Send message to channel"""
        url = f"{self.base_url}/chat.postMessage"
        data = {
            'channel': channel_id,
            'text': text
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            return response.json().get('ok', False)
        except Exception as e:
            logger.error(f"Error sending channel message: {e}")
            return False
    
    def _get_channel_id(self, channel_name: str) -> Optional[str]:
        """Get channel ID by name"""
        url = f"{self.base_url}/conversations.list"
        params = {'types': 'public_channel,private_channel'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                channels = response.json().get('channels', [])
                for channel in channels:
                    if channel['name'] == channel_name:
                        return channel['id']
            return None
        except Exception as e:
            logger.error(f"Error getting channel ID: {e}")
            return None
    
    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Get user ID by email"""
        url = f"{self.base_url}/users.lookupByEmail"
        params = {'email': email}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('user', {}).get('id')
            return None
        except Exception as e:
            logger.error(f"Error looking up user by email: {e}")
            return None
    
    def _add_user_to_channel(self, user_id: str, channel_id: str) -> bool:
        """Add user to specific channel"""
        url = f"{self.base_url}/conversations.invite"
        data = {
            'channel': channel_id,
            'users': user_id
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            return response.json().get('ok', False)
        except Exception as e:
            logger.error(f"Error adding user to channel: {e}")
            return False

class JiraIntegration:
    """Jira API integration for onboarding task management"""
    
    def __init__(self, url: str, username: str, api_token: str):
        self.url = url
        self.auth = (username, api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def create_onboarding_epic(self, employee: NewEmployee) -> Optional[str]:
        """Create onboarding epic for new employee"""
        epic_data = {
            "fields": {
                "project": {"key": "ONBOARD"},
                "summary": f"Onboarding: {employee.first_name} {employee.last_name}",
                "description": f"""
Onboarding epic for {employee.first_name} {employee.last_name}

**Role:** {employee.role}
**Team:** {employee.team}
**Start Date:** {employee.start_date}
**Manager:** {employee.manager_email}

This epic tracks all onboarding tasks and milestones.
                """,
                "issuetype": {"name": "Epic"},
                "assignee": {"emailAddress": employee.manager_email},
                "customfield_10011": f"{employee.first_name} {employee.last_name} Onboarding",  # Epic Name
                "labels": ["onboarding", employee.team, employee.role.replace(" ", "-").lower()]
            }
        }
        
        try:
            response = requests.post(
                f"{self.url}/rest/api/2/issue",
                auth=self.auth,
                headers=self.headers,
                json=epic_data
            )
            
            if response.status_code == 201:
                epic_key = response.json()['key']
                logger.info(f"Created onboarding epic: {epic_key}")
                return epic_key
            else:
                logger.error(f"Failed to create epic: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Jira API error: {e}")
            return None
    
    def create_onboarding_tasks(self, epic_key: str, employee: NewEmployee) -> List[str]:
        """Create standardized onboarding tasks"""
        tasks = self._get_onboarding_tasks(employee)
        created_tasks = []
        
        for task in tasks:
            task_key = self._create_task(task, epic_key, employee)
            if task_key:
                created_tasks.append(task_key)
        
        return created_tasks
    
    def _get_onboarding_tasks(self, employee: NewEmployee) -> List[OnboardingTask]:
        """Get list of onboarding tasks based on role and team"""
        base_tasks = [
            OnboardingTask(
                id="setup-accounts",
                title="Setup Development Accounts",
                description="Create and configure GitHub, Slack, and AWS accounts",
                owner="IT",
                due_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            ),
            OnboardingTask(
                id="environment-setup",
                title="Development Environment Setup",
                description="Install and configure development tools and IDE",
                owner=employee.buddy_email or employee.manager_email,
                due_date=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                dependencies=["setup-accounts"]
            ),
            OnboardingTask(
                id="team-introductions",
                title="Team Introductions and Meet & Greets",
                description="Schedule 30-min introductory meetings with key team members",
                owner=employee.manager_email,
                due_date=(datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            ),
            OnboardingTask(
                id="codebase-walkthrough",
                title="Codebase Architecture Walkthrough",
                description="Review system architecture and key repositories",
                owner=employee.buddy_email or employee.manager_email,
                due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                dependencies=["environment-setup"]
            ),
            OnboardingTask(
                id="first-pr",
                title="Submit First Pull Request",
                description="Complete a small bug fix or documentation update",
                owner=employee.email,
                due_date=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                dependencies=["codebase-walkthrough"]
            ),
            OnboardingTask(
                id="security-training",
                title="Complete Security Training",
                description="Complete mandatory security awareness training",
                owner=employee.email,
                due_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            ),
            OnboardingTask(
                id="30-day-checkin",
                title="30-Day Performance Check-in",
                description="Formal review of progress and goal setting",
                owner=employee.manager_email,
                due_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            )
        ]
        
        # Add role-specific tasks
        if "backend" in employee.role.lower() or employee.team == "backend":
            base_tasks.extend([
                OnboardingTask(
                    id="database-access",
                    title="Database Access and Training",
                    description="Setup database access and review data models",
                    owner="DBA",
                    due_date=(datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                    dependencies=["setup-accounts"]
                ),
                OnboardingTask(
                    id="api-documentation",
                    title="Review API Documentation and Standards",
                    description="Study API design patterns and documentation",
                    owner=employee.buddy_email or employee.manager_email,
                    due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                )
            ])
        
        if "frontend" in employee.role.lower() or employee.team == "frontend":
            base_tasks.extend([
                OnboardingTask(
                    id="design-system",
                    title="Design System and Component Library Review",
                    description="Learn company design system and component usage",
                    owner="Design Team",
                    due_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                ),
                OnboardingTask(
                    id="accessibility-training",
                    title="Accessibility Standards Training",
                    description="Complete web accessibility best practices training",
                    owner=employee.email,
                    due_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
                )
            ])
        
        return base_tasks
    
    def _create_task(self, task: OnboardingTask, epic_key: str, employee: NewEmployee) -> Optional[str]:
        """Create individual onboarding task"""
        task_data = {
            "fields": {
                "project": {"key": "ONBOARD"},
                "summary": task.title,
                "description": task.description,
                "issuetype": {"name": "Task"},
                "assignee": {"emailAddress": task.owner},
                "duedate": task.due_date,
                "customfield_10014": epic_key,  # Epic Link
                "labels": ["onboarding", employee.team, task.id]
            }
        }
        
        try:
            response = requests.post(
                f"{self.url}/rest/api/2/issue",
                auth=self.auth,
                headers=self.headers,
                json=task_data
            )
            
            if response.status_code == 201:
                task_key = response.json()['key']
                logger.info(f"Created onboarding task: {task_key} - {task.title}")
                return task_key
            else:
                logger.error(f"Failed to create task {task.title}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating task {task.title}: {e}")
            return None

class EmailNotification:
    """Email notification system for onboarding communications"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_address: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
    
    def send_welcome_email(self, employee: NewEmployee) -> bool:
        """Send welcome email to new employee"""
        subject = f"Welcome to the team, {employee.first_name}!"
        
        body = f"""
Dear {employee.first_name},

Welcome to the {employee.team} team! We're excited to have you join us as a {employee.role}.

Your onboarding has been automatically scheduled and you should expect:

📅 **This Week:**
• Account setup and access provisioning
• Development environment configuration
• Team introductions and initial meetings

🔧 **Development Setup:**
• GitHub access to our repositories
• Slack invitation to team channels
• AWS account and necessary permissions
• Development tools and IDE configuration

👥 **Your Team:**
• Manager: {employee.manager_email}
• Onboarding Buddy: {employee.buddy_email or 'Will be assigned soon'}

📋 **Next Steps:**
1. Check your email for various account invitations
2. Join the team Slack and introduce yourself
3. Complete the development environment setup
4. Schedule your first week's meetings

If you have any questions or need help with anything, don't hesitate to reach out to your manager or the engineering team.

Looking forward to working with you!

Best regards,
Engineering Team
        """
        
        return self._send_email(employee.email, subject, body)
    
    def send_manager_notification(self, employee: NewEmployee, epic_key: str, tasks: List[str]) -> bool:
        """Send notification to manager about onboarding setup"""
        subject = f"Onboarding Setup Complete: {employee.first_name} {employee.last_name}"
        
        body = f"""
Hi there,

The automated onboarding process has been initiated for {employee.first_name} {employee.last_name}.

**Employee Details:**
• Name: {employee.first_name} {employee.last_name}
• Role: {employee.role}
• Team: {employee.team}
• Start Date: {employee.start_date}
• Email: {employee.email}

**Automated Setup Completed:**
✅ GitHub organization and team access
✅ Slack channel invitations
✅ Jira onboarding epic created: {epic_key}
✅ {len(tasks)} onboarding tasks created

**Your Action Items:**
• Review and customize the onboarding timeline
• Assign an onboarding buddy if not already done
• Schedule the first week's meetings and introductions
• Review the automatically created tasks in Jira

**Jira Epic:** {epic_key}
**Created Tasks:** {', '.join(tasks)}

The system has sent a welcome email to {employee.first_name} with basic information about their first week.

Please reach out if you need any adjustments to the onboarding plan.

Best regards,
Engineering Operations
        """
        
        return self._send_email(employee.manager_email, subject, body)
    
    def send_buddy_assignment(self, employee: NewEmployee, buddy_email: str) -> bool:
        """Send notification to assigned onboarding buddy"""
        subject = f"Onboarding Buddy Assignment: {employee.first_name} {employee.last_name}"
        
        body = f"""
Hi there,

You've been assigned as the onboarding buddy for our new team member!

**New Team Member:**
• Name: {employee.first_name} {employee.last_name}
• Role: {employee.role}
• Team: {employee.team}
• Start Date: {employee.start_date}

**Your Responsibilities as Onboarding Buddy:**
• Help with development environment setup
• Provide codebase walkthrough and architecture overview
• Be available for technical questions during first month
• Schedule regular check-ins during first two weeks
• Help with first pull request and code review

**Suggested Schedule:**
• Day 1: Welcome and initial setup help
• Day 3: Development environment review
• Week 1: Codebase walkthrough
• Week 2: First project assignment and guidance
• Week 4: Check-in and feedback session

The system has created relevant tasks in Jira that are assigned to you. Please check your notifications for the specific timeline.

Thanks for helping our new team member get up to speed!

Best regards,
Engineering Team
        """
        
        return self._send_email(buddy_email, subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.from_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.from_address, to_email, text)
            server.quit()
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

class AWSIntegration:
    """AWS IAM integration for account and access management"""
    
    def __init__(self, access_key: str, secret_key: str, region: str):
        try:
            import boto3
            self.iam = boto3.client(
                'iam',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        except ImportError:
            logger.error("boto3 not installed. Run: pip install boto3")
            self.iam = None
    
    def create_user_account(self, employee: NewEmployee) -> Optional[Dict[str, str]]:
        """Create AWS IAM user account"""
        if not self.iam:
            return None
        
        username = f"{employee.first_name.lower()}.{employee.last_name.lower()}"
        
        try:
            # Create user
            self.iam.create_user(
                UserName=username,
                Tags=[
                    {'Key': 'Department', 'Value': 'Engineering'},
                    {'Key': 'Team', 'Value': employee.team},
                    {'Key': 'Role', 'Value': employee.role},
                    {'Key': 'Manager', 'Value': employee.manager_email}
                ]
            )
            
            # Create access key
            response = self.iam.create_access_key(UserName=username)
            access_key = response['AccessKey']
            
            # Add to appropriate groups based on team
            groups = self._get_groups_for_team(employee.team)
            for group in groups:
                try:
                    self.iam.add_user_to_group(
                        UserName=username,
                        GroupName=group
                    )
                except Exception as e:
                    logger.warning(f"Could not add {username} to group {group}: {e}")
            
            logger.info(f"Created AWS user: {username}")
            
            return {
                'username': username,
                'access_key_id': access_key['AccessKeyId'],
                'secret_access_key': access_key['SecretAccessKey']
            }
            
        except Exception as e:
            logger.error(f"Failed to create AWS user: {e}")
            return None
    
    def _get_groups_for_team(self, team: str) -> List[str]:
        """Get IAM groups based on team"""
        group_mapping = {
            'backend': ['Developers', 'DatabaseReadOnly', 'S3Access'],
            'frontend': ['Developers', 'S3Access'],
            'fullstack': ['Developers', 'DatabaseReadOnly', 'S3Access'],
            'devops': ['Developers', 'PowerUsers', 'EC2Access', 'DatabaseAccess'],
            'data': ['Developers', 'DatabaseAccess', 'S3FullAccess']
        }
        
        return group_mapping.get(team.lower(), ['Developers'])

class OnboardingOrchestrator:
    """Main orchestrator class that coordinates all onboarding activities"""
    
    def __init__(self, config_file: str = "onboarding_config.yaml"):
        self.config = OnboardingConfig(config_file)
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize all service integrations"""
        # GitHub integration
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            self.github = GitHubIntegration(
                token=github_token,
                org=self.config.config['github']['org']
            )
        else:
            logger.warning("GITHUB_TOKEN not set. GitHub integration disabled.")
            self.github = None
        
        # Slack integration
        slack_token = os.getenv('SLACK_BOT_TOKEN')
        if slack_token:
            self.slack = SlackIntegration(token=slack_token)
        else:
            logger.warning("SLACK_BOT_TOKEN not set. Slack integration disabled.")
            self.slack = None
        
        # Jira integration
        jira_username = os.getenv('JIRA_USERNAME')
        jira_token = os.getenv('JIRA_API_TOKEN')
        if jira_username and jira_token:
            self.jira = JiraIntegration(
                url=self.config.config['jira']['url'],
                username=jira_username,
                api_token=jira_token
            )
        else:
            logger.warning("JIRA credentials not set. Jira integration disabled.")
            self.jira = None
        
        # Email integration
        email_username = os.getenv('EMAIL_USERNAME')
        email_password = os.getenv('EMAIL_PASSWORD')
        if email_username and email_password:
            self.email = EmailNotification(
                smtp_server=self.config.config['email']['smtp_server'],
                smtp_port=self.config.config['email']['smtp_port'],
                username=email_username,
                password=email_password,
                from_address=self.config.config['email']['from_address']
            )
        else:
            logger.warning("Email credentials not set. Email notifications disabled.")
            self.email = None
        
        # AWS integration
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        if aws_key and aws_secret:
            self.aws = AWSIntegration(
                access_key=aws_key,
                secret_key=aws_secret,
                region=self.config.config['aws']['region']
            )
        else:
            logger.warning("AWS credentials not set. AWS integration disabled.")
            self.aws = None
    
    def onboard_employee(self, employee: NewEmployee) -> Dict[str, Any]:
        """Main onboarding orchestration method"""
        logger.info(f"Starting onboarding for {employee.first_name} {employee.last_name}")
        
        results = {
            'employee': asdict(employee),
            'timestamp': datetime.now().isoformat(),
            'github': {},
            'slack': {},
            'jira': {},
            'aws': {},
            'email': {},
            'success': True,
            'errors': []
        }
        
        try:
            # Step 1: GitHub setup
            if self.github:
                results['github'] = self._setup_github_access(employee)
            
            # Step 2: Slack setup
            if self.slack and employee.slack_user_id:
                results['slack'] = self._setup_slack_access(employee)
            
            # Step 3: AWS setup
            if self.aws:
                results['aws'] = self._setup_aws_access(employee)
            
            # Step 4: Jira project management
            if self.jira:
                results['jira'] = self._setup_jira_tracking(employee)
            
            # Step 5: Email notifications
            if self.email:
                results['email'] = self._send_email_notifications(employee, results)
            
            # Step 6: Generate onboarding report
            self._generate_onboarding_report(employee, results)
            
            logger.info(f"Onboarding completed for {employee.first_name} {employee.last_name}")
            
        except Exception as e:
            logger.error(f"Onboarding failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
        
        return results
    
    def _setup_github_access(self, employee: NewEmployee) -> Dict[str, Any]:
        """Setup GitHub organization and repository access"""
        github_results = {
            'org_invitation': False,
            'team_assignment': False,
            'repository_access': {},
            'success': True
        }
        
        if not employee.github_username:
            github_results['success'] = False
            github_results['error'] = 'GitHub username not provided'
            return github_results
        
        try:
            # Add to organization
            github_results['org_invitation'] = self.github.add_user_to_org(employee.github_username)
            
            # Add to team
            team_name = f"{employee.team}-team"
            github_results['team_assignment'] = self.github.add_user_to_team(
                employee.github_username, 
                team_name
            )
            
            # Grant repository access based on team
            repositories = self._get_repositories_for_team(employee.team)
            github_results['repository_access'] = self.github.grant_repository_access(
                employee.github_username,
                repositories
            )
            
            # Check overall success
            github_results['success'] = (
                github_results['org_invitation'] and
                github_results['team_assignment'] and
                all(github_results['repository_access'].values())
            )
            
        except Exception as e:
            logger.error(f"GitHub setup failed: {e}")
            github_results['success'] = False
            github_results['error'] = str(e)
        
        return github_results
    
    def _setup_slack_access(self, employee: NewEmployee) -> Dict[str, Any]:
        """Setup Slack channels and notifications"""
        slack_results = {
            'welcome_message': False,
            'channel_invitations': {},
            'team_notification': False,
            'success': True
        }
        
        try:
            # Send welcome message
            slack_results['welcome_message'] = self.slack.send_welcome_message(
                employee.slack_user_id,
                employee
            )
            
            # Add to relevant channels
            slack_results['channel_invitations'] = self.slack.add_user_to_channels(
                employee.slack_user_id,
                employee.team
            )
            
            # Notify team about new member
            team_channel = f"team-{employee.team}"
            slack_results['team_notification'] = self.slack.notify_team_about_new_member(
                team_channel,
                employee
            )
            
            # Check overall success
            slack_results['success'] = (
                slack_results['welcome_message'] and
                slack_results['team_notification'] and
                any(slack_results['channel_invitations'].values())
            )
            
        except Exception as e:
            logger.error(f"Slack setup failed: {e}")
            slack_results['success'] = False
            slack_results['error'] = str(e)
        
        return slack_results
    
    def _setup_aws_access(self, employee: NewEmployee) -> Dict[str, Any]:
        """Setup AWS user account and permissions"""
        aws_results = {
            'user_created': False,
            'credentials': None,
            'success': True
        }
        
        try:
            credentials = self.aws.create_user_account(employee)
            if credentials:
                aws_results['user_created'] = True
                aws_results['credentials'] = {
                    'username': credentials['username'],
                    'access_key_id': credentials['access_key_id']
                    # Note: Secret key should be sent securely, not logged
                }
                aws_results['success'] = True
            else:
                aws_results['success'] = False
                aws_results['error'] = 'Failed to create AWS user'
                
        except Exception as e:
            logger.error(f"AWS setup failed: {e}")
            aws_results['success'] = False
            aws_results['error'] = str(e)
        
        return aws_results
    
    def _setup_jira_tracking(self, employee: NewEmployee) -> Dict[str, Any]:
        """Setup Jira epic and onboarding tasks"""
        jira_results = {
            'epic_created': False,
            'epic_key': None,
            'tasks_created': [],
            'success': True
        }
        
        try:
            # Create onboarding epic
            epic_key = self.jira.create_onboarding_epic(employee)
            if epic_key:
                jira_results['epic_created'] = True
                jira_results['epic_key'] = epic_key
                
                # Create onboarding tasks
                tasks = self.jira.create_onboarding_tasks(epic_key, employee)
                jira_results['tasks_created'] = tasks
                jira_results['success'] = len(tasks) > 0
            else:
                jira_results['success'] = False
                jira_results['error'] = 'Failed to create epic'
                
        except Exception as e:
            logger.error(f"Jira setup failed: {e}")
            jira_results['success'] = False
            jira_results['error'] = str(e)
        
        return jira_results
    
    def _send_email_notifications(self, employee: NewEmployee, results: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notifications to relevant parties"""
        email_results = {
            'welcome_email': False,
            'manager_notification': False,
            'buddy_notification': False,
            'success': True
        }
        
        try:
            # Send welcome email to employee
            email_results['welcome_email'] = self.email.send_welcome_email(employee)
            
            # Send notification to manager
            epic_key = results.get('jira', {}).get('epic_key', 'N/A')
            tasks = results.get('jira', {}).get('tasks_created', [])
            email_results['manager_notification'] = self.email.send_manager_notification(
                employee, epic_key, tasks
            )
            
            # Send notification to buddy if assigned
            if employee.buddy_email:
                email_results['buddy_notification'] = self.email.send_buddy_assignment(
                    employee, employee.buddy_email
                )
            
            email_results['success'] = (
                email_results['welcome_email'] and
                email_results['manager_notification']
            )
            
        except Exception as e:
            logger.error(f"Email notifications failed: {e}")
            email_results['success'] = False
            email_results['error'] = str(e)
        
        return email_results
    
    def _get_repositories_for_team(self, team: str) -> List[str]:
        """Get list of repositories based on team"""
        repo_mapping = {
            'backend': ['api-service', 'database-migrations', 'shared-libraries'],
            'frontend': ['web-app', 'mobile-app', 'design-system'],
            'fullstack': ['api-service', 'web-app', 'shared-libraries'],
            'devops': ['infrastructure', 'deployment-scripts', 'monitoring'],
            'data': ['data-pipeline', 'analytics', 'ml-models']
        }
        
        base_repos = ['documentation', 'onboarding', 'shared-configs']
        team_repos = repo_mapping.get(team.lower(), [])
        
        return base_repos + team_repos
    
    def _generate_onboarding_report(self, employee: NewEmployee, results: Dict[str, Any]):
        """Generate comprehensive onboarding report"""
        report_filename = f"onboarding_report_{employee.first_name}_{employee.last_name}_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Save detailed results
        with open(report_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate summary report
        summary_filename = f"onboarding_summary_{employee.first_name}_{employee.last_name}_{datetime.now().strftime('%Y%m%d')}.md"
        
        summary_content = f"""# Onboarding Summary: {employee.first_name} {employee.last_name}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Role:** {employee.role}
**Team:** {employee.team}
**Manager:** {employee.manager_email}

## Setup Status

### GitHub
- Organization Invitation: {'✅' if results.get('github', {}).get('org_invitation') else '❌'}
- Team Assignment: {'✅' if results.get('github', {}).get('team_assignment') else '❌'}
- Repository Access: {len([r for r in results.get('github', {}).get('repository_access', {}).values() if r])} / {len(results.get('github', {}).get('repository_access', {}))} repositories

### Slack
- Welcome Message: {'✅' if results.get('slack', {}).get('welcome_message') else '❌'}
- Channel Invitations: {len([c for c in results.get('slack', {}).get('channel_invitations', {}).values() if c])} channels
- Team Notification: {'✅' if results.get('slack', {}).get('team_notification') else '❌'}

### AWS
- User Account: {'✅' if results.get('aws', {}).get('user_created') else '❌'}
- Credentials Generated: {'✅' if results.get('aws', {}).get('credentials') else '❌'}

### Jira
- Epic Created: {'✅' if results.get('jira', {}).get('epic_created') else '❌'}
- Epic Key: {results.get('jira', {}).get('epic_key', 'N/A')}
- Tasks Created: {len(results.get('jira', {}).get('tasks_created', []))} tasks

### Email Notifications
- Welcome Email: {'✅' if results.get('email', {}).get('welcome_email') else '❌'}
- Manager Notification: {'✅' if results.get('email', {}).get('manager_notification') else '❌'}
- Buddy Notification: {'✅' if results.get('email', {}).get('buddy_notification') else '❌'}

## Next Steps

1. **Manager:** Review Jira epic and customize timeline as needed
2. **IT:** Verify all account access is working correctly
3. **Buddy:** Reach out to {employee.first_name} for initial setup help
4. **Employee:** Check email for various service invitations

## Issues to Address

"""
        
        # Add any errors or failed setups
        for service, service_results in results.items():
            if isinstance(service_results, dict) and not service_results.get('success', True):
                summary_content += f"- **{service.title()}:** {service_results.get('error', 'Setup failed')}\n"
        
        if all(results.get(service, {}).get('success', True) for service in ['github', 'slack', 'aws', 'jira', 'email'] if service in results):
            summary_content += "No issues detected. All automated setup completed successfully! 🎉\n"
        
        with open(summary_filename, 'w') as f:
            f.write(summary_content)
        
        logger.info(f"Reports generated: {report_filename}, {summary_filename}")

def main():
    """Main CLI interface for onboarding automation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automate employee onboarding process')
    parser.add_argument('--config', default='onboarding_config.yaml', help='Configuration file path')
    parser.add_argument('--employee-file', help='JSON file with employee information')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode for single employee')
    parser.add_argument('--dry-run', action='store_true', help='Preview actions without executing')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = OnboardingOrchestrator(args.config)
    
    if args.employee_file:
        # Batch processing from file
        with open(args.employee_file, 'r') as f:
            employees_data = json.load(f)
        
        for emp_data in employees_data:
            employee = NewEmployee(**emp_data)
            if args.dry_run:
                logger.info(f"DRY RUN: Would onboard {employee.first_name} {employee.last_name}")
            else:
                result = orchestrator.onboard_employee(employee)
                print(f"Onboarding {'successful' if result['success'] else 'failed'} for {employee.first_name}")
    
    elif args.interactive:
        # Interactive mode
        print("🚀 Interactive Onboarding Setup")
        print("=" * 40)
        
        employee = NewEmployee(
            first_name=input("First Name: "),
            last_name=input("Last Name: "),
            email=input("Email: "),
            role=input("Role: "),
            team=input("Team: "),
            start_date=input("Start Date (YYYY-MM-DD): "),
            manager_email=input("Manager Email: "),
            buddy_email=input("Buddy Email (optional): ") or None,
            github_username=input("GitHub Username: ") or None,
            slack_user_id=input("Slack User ID (optional): ") or None
        )
        
        print(f"\n📋 Onboarding Summary:")
        print(f"Name: {employee.first_name} {employee.last_name}")
        print(f"Role: {employee.role}")
        print(f"Team: {employee.team}")
        print(f"Start: {employee.start_date}")
        
        if args.dry_run:
            print("\n🔍 DRY RUN MODE - No actions will be executed")
        
        confirm = input("\nProceed with onboarding? (y/N): ")
        if confirm.lower() == 'y':
            if args.dry_run:
                logger.info(f"DRY RUN: Would onboard {employee.first_name} {employee.last_name}")
            else:
                result = orchestrator.onboard_employee(employee)
                if result['success']:
                    print(f"\n✅ Onboarding completed successfully!")
                    print(f"Check the generated reports for details.")
                else:
                    print(f"\n❌ Onboarding encountered issues:")
                    for error in result.get('errors', []):
                        print(f"  - {error}")
        else:
            print("Onboarding cancelled.")
    
    else:
        parser.print_help()

def create_sample_config():
    """Create sample configuration file"""
    sample_config = {
        'company': {
            'name': 'Your Company',
            'domain': 'company.com',
            'slack_workspace': 'company.slack.com'
        },
        'github': {
            'org': 'your-org',
            'base_url': 'https://api.github.com'
        },
        'jira': {
            'url': 'https://company.atlassian.net',
            'project_key': 'ONBOARD'
        },
        'aws': {
            'region': 'us-west-2',
            'account_id': '123456789012'
        },
        'email': {
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587,
            'from_address': 'engineering@company.com'
        },
        'teams': {
            'backend': {
                'repositories': ['api-service', 'database-migrations'],
                'slack_channels': ['team-backend', 'engineering-general'],
                'aws_groups': ['Developers', 'DatabaseReadOnly']
            },
            'frontend': {
                'repositories': ['web-app', 'design-system'],
                'slack_channels': ['team-frontend', 'engineering-general'],
                'aws_groups': ['Developers', 'S3Access']
            }
        }
    }
    
    with open('onboarding_config.yaml', 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False)
    
    print("Sample configuration created: onboarding_config.yaml")

def create_sample_employee_file():
    """Create sample employee data file"""
    sample_employees = [
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@company.com",
            "role": "Senior Backend Developer",
            "team": "backend",
            "start_date": "2024-06-01",
            "manager_email": "manager@company.com",
            "buddy_email": "buddy@company.com",
            "github_username": "janedoe",
            "slack_user_id": "U1234567890"
        },
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@company.com",
            "role": "Frontend Developer",
            "team": "frontend",
            "start_date": "2024-06-15",
            "manager_email": "manager@company.com",
            "github_username": "johnsmith"
        }
    ]
    
    with open('sample_employees.json', 'w') as f:
        json.dump(sample_employees, f, indent=2)
    
    print("Sample employee file created: sample_employees.json")

if __name__ == "__main__":
    # Check if this is being run to create samples
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "create-samples":
        create_sample_config()
        create_sample_employee_file()
        print("\nSample files created! Edit them with your actual configuration.")
        print("\nRequired environment variables:")
        print("- GITHUB_TOKEN")
        print("- SLACK_BOT_TOKEN") 
        print("- JIRA_USERNAME")
        print("- JIRA_API_TOKEN")
        print("- EMAIL_USERNAME")
        print("- EMAIL_PASSWORD")
        print("- AWS_ACCESS_KEY_ID")
        print("- AWS_SECRET_ACCESS_KEY")
    else:
        main()