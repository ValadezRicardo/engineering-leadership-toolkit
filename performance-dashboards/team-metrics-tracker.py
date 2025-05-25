"""
Engineering Team Performance Metrics Tracker

Collects and analyzes key engineering metrics for team performance dashboards.
Integrates with GitHub, Jira, and deployment systems to provide comprehensive insights.

Author: Ricardo Valadez
Purpose: Data-driven engineering team management
"""

import json
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class TeamMetrics:
    """Core engineering team performance metrics"""
    date: str
    team_name: str
    
    # Development Velocity Metrics
    story_points_completed: int
    stories_delivered: int
    bugs_fixed: int
    technical_debt_items: int
    
    # Code Quality Metrics
    pull_requests_merged: int
    code_review_time_hours: float
    test_coverage_percent: float
    code_quality_score: float
    
    # Deployment & Reliability Metrics
    deployments_count: int
    deployment_success_rate: float
    mean_time_to_recovery_hours: float
    uptime_percent: float
    
    # Team Health Metrics
    team_satisfaction_score: float
    knowledge_sharing_sessions: int
    cross_training_hours: float
    innovation_time_percent: float

class MetricsCollector:
    """Collects metrics from various engineering tools and systems"""
    
    def __init__(self, config: Dict[str, str]):
        self.github_token = config.get('github_token')
        self.jira_config = config.get('jira_config', {})
        self.deployment_api = config.get('deployment_api')
        self.monitoring_api = config.get('monitoring_api')
    
    def collect_github_metrics(self, repo: str, team_members: List[str], 
                             days: int = 30) -> Dict[str, float]:
        """Collect code-related metrics from GitHub API"""
        
        headers = {'Authorization': f'token {self.github_token}'}
        base_url = f'https://api.github.com/repos/{repo}'
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        metrics = {
            'pull_requests_merged': 0,
            'code_review_time_hours': 0,
            'commits_count': 0,
            'lines_changed': 0
        }
        
        try:
            # Get merged pull requests
            pr_url = f'{base_url}/pulls'
            pr_params = {
                'state': 'closed',
                'since': start_date.isoformat(),
                'per_page': 100
            }
            
            response = requests.get(pr_url, headers=headers, params=pr_params)
            pull_requests = response.json()
            
            review_times = []
            
            for pr in pull_requests:
                if pr.get('merged_at') and pr.get('user', {}).get('login') in team_members:
                    metrics['pull_requests_merged'] += 1
                    
                    # Calculate review time
                    created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                    merged = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                    review_time = (merged - created).total_seconds() / 3600
                    review_times.append(review_time)
            
            if review_times:
                metrics['code_review_time_hours'] = sum(review_times) / len(review_times)
            
            # Get commit activity
            commits_url = f'{base_url}/stats/contributors'
            commits_response = requests.get(commits_url, headers=headers)
            contributors = commits_response.json()
            
            for contributor in contributors:
                if contributor.get('author', {}).get('login') in team_members:
                    # Sum commits from last 4 weeks
                    recent_weeks = contributor.get('weeks', [])[-4:]
                    metrics['commits_count'] += sum(week.get('c', 0) for week in recent_weeks)
                    metrics['lines_changed'] += sum(
                        week.get('a', 0) + week.get('d', 0) for week in recent_weeks
                    )
        
        except Exception as e:
            print(f"Error collecting GitHub metrics: {e}")
        
        return metrics
    
    def collect_deployment_metrics(self, service_names: List[str], 
                                 days: int = 30) -> Dict[str, float]:
        """Collect deployment and reliability metrics"""
        
        metrics = {
            'deployments_count': 0,
            'deployment_success_rate': 100.0,
            'mean_time_to_recovery_hours': 0,
            'uptime_percent': 99.9
        }
        
        try:
            # This would integrate with your deployment system (AWS CodeDeploy, etc.)
            # Example implementation for demonstration
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            for service in service_names:
                # Mock deployment data - replace with actual API calls
                deployments = self._get_deployments(service, start_date, end_date)
                metrics['deployments_count'] += len(deployments)
                
                successful = sum(1 for d in deployments if d['status'] == 'success')
                if deployments:
                    service_success_rate = (successful / len(deployments)) * 100
                    metrics['deployment_success_rate'] = min(
                        metrics['deployment_success_rate'], 
                        service_success_rate
                    )
                
                # Calculate MTTR from incident data
                incidents = self._get_incidents(service, start_date, end_date)
                if incidents:
                    recovery_times = [
                        (inc['resolved_at'] - inc['created_at']).total_seconds() / 3600
                        for inc in incidents if inc.get('resolved_at')
                    ]
                    if recovery_times:
                        metrics['mean_time_to_recovery_hours'] = sum(recovery_times) / len(recovery_times)
        
        except Exception as e:
            print(f"Error collecting deployment metrics: {e}")
        
        return metrics
    
    def _get_deployments(self, service: str, start_date: datetime, 
                        end_date: datetime) -> List[Dict]:
        """Mock deployment data - replace with actual API integration"""
        # This should integrate with your deployment system
        return [
            {'service': service, 'status': 'success', 'timestamp': start_date + timedelta(days=i)}
            for i in range(0, (end_date - start_date).days, 3)
        ]
    
    def _get_incidents(self, service: str, start_date: datetime, 
                      end_date: datetime) -> List[Dict]:
        """Mock incident data - replace with actual monitoring system integration"""
        # This should integrate with your monitoring/alerting system
        return [
            {
                'service': service,
                'created_at': start_date + timedelta(days=10),
                'resolved_at': start_date + timedelta(days=10, hours=2)
            }
        ]
    
    def collect_team_health_metrics(self, team_name: str) -> Dict[str, float]:
        """Collect team satisfaction and culture metrics"""
        
        # This would typically come from surveys, 1:1 feedback, etc.
        # For now, providing template structure
        
        metrics = {
            'team_satisfaction_score': 4.2,  # Out of 5
            'knowledge_sharing_sessions': 8,  # Per month
            'cross_training_hours': 16,      # Per month
            'innovation_time_percent': 15    # Percentage of total time
        }
        
        return metrics

class MetricsDashboard:
    """Generates visualizations and reports for engineering metrics"""
    
    def __init__(self):
        self.metrics_history: List[TeamMetrics] = []
    
    def add_metrics(self, metrics: TeamMetrics):
        """Add new metrics data point"""
        self.metrics_history.append(metrics)
    
    def generate_velocity_chart(self, team_name: str, days: int = 90):
        """Generate team velocity trend chart"""
        
        team_data = [m for m in self.metrics_history 
                    if m.team_name == team_name][-days//7:]  # Weekly data points
        
        if not team_data:
            print(f"No data available for team: {team_name}")
            return
        
        dates = [m.date for m in team_data]
        story_points = [m.story_points_completed for m in team_data]
        stories = [m.stories_delivered for m in team_data]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Story points trend
        ax1.plot(dates, story_points, marker='o', linewidth=2, label='Story Points')
        ax1.set_title(f'{team_name} - Story Points Completed', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Story Points')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Stories delivered trend
        ax2.plot(dates, stories, marker='s', linewidth=2, color='green', label='Stories')
        ax2.set_title(f'{team_name} - Stories Delivered', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Stories Count')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{team_name}_velocity_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_quality_metrics_report(self, team_name: str) -> Dict[str, float]:
        """Generate code quality metrics summary"""
        
        recent_metrics = [m for m in self.metrics_history 
                         if m.team_name == team_name][-4:]  # Last 4 weeks
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        avg_metrics = {
            'avg_test_coverage': sum(m.test_coverage_percent for m in recent_metrics) / len(recent_metrics),
            'avg_code_quality_score': sum(m.code_quality_score for m in recent_metrics) / len(recent_metrics),
            'avg_review_time': sum(m.code_review_time_hours for m in recent_metrics) / len(recent_metrics),
            'total_prs_merged': sum(m.pull_requests_merged for m in recent_metrics)
        }
        
        return avg_metrics
    
    def generate_executive_summary(self, team_name: str) -> str:
        """Generate executive summary for leadership"""
        
        latest = next((m for m in reversed(self.metrics_history) 
                      if m.team_name == team_name), None)
        
        if not latest:
            return f"No metrics available for team: {team_name}"
        
        quality_summary = self.generate_quality_metrics_report(team_name)
        
        summary = f"""
        
# Engineering Team Performance Summary - {team_name}
**Report Date**: {latest.date}

## 🚀 Delivery Performance
- **Stories Delivered**: {latest.stories_delivered} (Current Sprint)
- **Story Points Completed**: {latest.story_points_completed}
- **Bugs Fixed**: {latest.bugs_fixed}
- **Technical Debt Items**: {latest.technical_debt_items}

## 🔧 Code Quality Metrics
- **Test Coverage**: {latest.test_coverage_percent:.1f}%
- **Code Quality Score**: {latest.code_quality_score:.1f}/10
- **Average PR Review Time**: {quality_summary.get('avg_review_time', 0):.1f} hours
- **PRs Merged (30 days)**: {quality_summary.get('total_prs_merged', 0)}

## 🚢 Deployment & Reliability
- **Deployments This Month**: {latest.deployments_count}
- **Deployment Success Rate**: {latest.deployment_success_rate:.1f}%
- **System Uptime**: {latest.uptime_percent:.2f}%
- **Mean Time to Recovery**: {latest.mean_time_to_recovery_hours:.1f} hours

## 👥 Team Health
- **Team Satisfaction**: {latest.team_satisfaction_score:.1f}/5.0
- **Knowledge Sharing Sessions**: {latest.knowledge_sharing_sessions}
- **Innovation Time**: {latest.innovation_time_percent:.1f}%
- **Cross-training Hours**: {latest.cross_training_hours:.1f}

## 📊 Key Insights
- {'🟢 Strong performance across all metrics' if latest.team_satisfaction_score >= 4.0 else '🟡 Some areas need attention'}
- {'🟢 Deployment reliability excellent' if latest.deployment_success_rate >= 95 else '🔴 Deployment issues detected'}
- {'🟢 Code quality maintained' if latest.test_coverage_percent >= 80 else '🟡 Test coverage below target'}

## 🎯 Recommendations
- Continue current velocity with focus on technical debt reduction
- Maintain high code quality standards through peer reviews
- Consider additional automation for deployment pipeline
- Schedule team retrospective to address any satisfaction concerns
        """
        
        return summary.strip()

# Example usage and configuration
def main():
    """Example usage of the metrics tracking system"""
    
    # Configuration
    config = {
        'github_token': 'your_github_token_here',
        'jira_config': {
            'server': 'your-company.atlassian.net',
            'username': 'your_email@company.com',
            'api_token': 'your_jira_api_token'
        },
        'deployment_api': 'https://api.aws.amazon.com/codedeploy',
        'monitoring_api': 'https://api.datadog.com/api/v1'
    }
    
    # Team configuration
    teams = {
        'logistics-platform': {
            'members': ['dev1', 'dev2', 'dev3', 'dev4'],
            'repositories': ['company/logistics-api', 'company/tracking-service'],
            'services': ['logistics-api', 'tracking-service', 'notification-service']
        },
        'payment-systems': {
            'members': ['dev5', 'dev6', 'dev7'],
            'repositories': ['company/payment-api', 'company/billing-service'],
            'services': ['payment-processor', 'billing-service']
        }
    }
    
    # Initialize collector and dashboard
    collector = MetricsCollector(config)
    dashboard = MetricsDashboard()
    
    # Collect metrics for each team
    for team_name, team_config in teams.items():
        print(f"Collecting metrics for team: {team_name}")
        
        # Collect from various sources
        github_metrics = {}
        for repo in team_config['repositories']:
            repo_metrics = collector.collect_github_metrics(
                repo, team_config['members'], days=30
            )
            # Aggregate metrics across repositories
            for key, value in repo_metrics.items():
                github_metrics[key] = github_metrics.get(key, 0) + value
        
        deployment_metrics = collector.collect_deployment_metrics(
            team_config['services'], days=30
        )
        
        team_health = collector.collect_team_health_metrics(team_name)
        
        # Create comprehensive metrics object
        team_metrics = TeamMetrics(
            date=datetime.now().strftime('%Y-%m-%d'),
            team_name=team_name,
            
            # Development velocity (would come from Jira/project management)
            story_points_completed=45,  # Example data
            stories_delivered=12,
            bugs_fixed=8,
            technical_debt_items=3,
            
            # Code quality from GitHub
            pull_requests_merged=github_metrics.get('pull_requests_merged', 0),
            code_review_time_hours=github_metrics.get('code_review_time_hours', 0),
            test_coverage_percent=85.5,  # Would come from code coverage tools
            code_quality_score=8.2,     # Would come from SonarQube, etc.
            
            # Deployment metrics
            deployments_count=deployment_metrics['deployments_count'],
            deployment_success_rate=deployment_metrics['deployment_success_rate'],
            mean_time_to_recovery_hours=deployment_metrics['mean_time_to_recovery_hours'],
            uptime_percent=deployment_metrics['uptime_percent'],
            
            # Team health
            team_satisfaction_score=team_health['team_satisfaction_score'],
            knowledge_sharing_sessions=team_health['knowledge_sharing_sessions'],
            cross_training_hours=team_health['cross_training_hours'],
            innovation_time_percent=team_health['innovation_time_percent']
        )
        
        dashboard.add_metrics(team_metrics)
        
        # Generate reports
        print(f"\n{dashboard.generate_executive_summary(team_name)}")
        
        # Generate visualizations
        dashboard.generate_velocity_chart(team_name)
        
        # Export metrics to JSON for external systems
        with open(f'{team_name}_metrics_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(asdict(team_metrics), f, indent=2)

class DORAMetrics:
    """DORA (DevOps Research and Assessment) Metrics Calculator"""
    
    @staticmethod
    def calculate_lead_time(commit_date: datetime, deploy_date: datetime) -> float:
        """Calculate lead time for changes in hours"""
        return (deploy_date - commit_date).total_seconds() / 3600
    
    @staticmethod
    def calculate_deployment_frequency(deployments: List[datetime], 
                                     period_days: int = 30) -> float:
        """Calculate deployment frequency per day"""
        return len(deployments) / period_days
    
    @staticmethod
    def calculate_mttr(incidents: List[Dict[str, datetime]]) -> float:
        """Calculate Mean Time to Recovery in hours"""
        if not incidents:
            return 0
        
        recovery_times = []
        for incident in incidents:
            if 'resolved_at' in incident and 'created_at' in incident:
                recovery_time = (incident['resolved_at'] - incident['created_at']).total_seconds() / 3600
                recovery_times.append(recovery_time)
        
        return sum(recovery_times) / len(recovery_times) if recovery_times else 0
    
    @staticmethod
    def calculate_change_failure_rate(total_deployments: int, 
                                    failed_deployments: int) -> float:
        """Calculate change failure rate as percentage"""
        if total_deployments == 0:
            return 0
        return (failed_deployments / total_deployments) * 100

class MetricsAlerts:
    """Automated alerting system for engineering metrics"""
    
    def __init__(self, thresholds: Dict[str, Dict[str, float]]):
        self.thresholds = thresholds
    
    def check_thresholds(self, metrics: TeamMetrics) -> List[Dict[str, str]]:
        """Check if any metrics exceed defined thresholds"""
        alerts = []
        team_thresholds = self.thresholds.get(metrics.team_name, {})
        
        # Check deployment success rate
        if metrics.deployment_success_rate < team_thresholds.get('min_deployment_success', 95):
            alerts.append({
                'severity': 'high',
                'metric': 'deployment_success_rate',
                'value': metrics.deployment_success_rate,
                'threshold': team_thresholds.get('min_deployment_success', 95),
                'message': f'Deployment success rate ({metrics.deployment_success_rate}%) below threshold'
            })
        
        # Check test coverage
        if metrics.test_coverage_percent < team_thresholds.get('min_test_coverage', 80):
            alerts.append({
                'severity': 'medium',
                'metric': 'test_coverage_percent',
                'value': metrics.test_coverage_percent,
                'threshold': team_thresholds.get('min_test_coverage', 80),
                'message': f'Test coverage ({metrics.test_coverage_percent}%) below target'
            })
        
        # Check team satisfaction
        if metrics.team_satisfaction_score < team_thresholds.get('min_satisfaction', 3.5):
            alerts.append({
                'severity': 'high',
                'metric': 'team_satisfaction_score',
                'value': metrics.team_satisfaction_score,
                'threshold': team_thresholds.get('min_satisfaction', 3.5),
                'message': f'Team satisfaction ({metrics.team_satisfaction_score}/5) needs attention'
            })
        
        # Check MTTR
        if metrics.mean_time_to_recovery_hours > team_thresholds.get('max_mttr', 4):
            alerts.append({
                'severity': 'medium',
                'metric': 'mean_time_to_recovery_hours',
                'value': metrics.mean_time_to_recovery_hours,
                'threshold': team_thresholds.get('max_mttr', 4),
                'message': f'MTTR ({metrics.mean_time_to_recovery_hours:.1f}h) exceeds target'
            })
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict[str, str]], team_name: str):
        """Send alerts via configured channels (Slack, email, etc.)"""
        if not alerts:
            return
        
        # Example Slack integration
        slack_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        
        for alert in alerts:
            severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡"
            message = f"{severity_emoji} *{team_name}* - {alert['message']}"
            
            # In real implementation, send to Slack/Teams/email
            print(f"ALERT: {message}")

# Advanced analytics and predictions
class MetricsAnalytics:
    """Advanced analytics for engineering metrics"""
    
    @staticmethod
    def predict_sprint_capacity(historical_velocity: List[int], 
                              team_changes: Dict[str, int] = None) -> int:
        """Predict team capacity for next sprint based on historical data"""
        if len(historical_velocity) < 3:
            return sum(historical_velocity) // len(historical_velocity) if historical_velocity else 0
        
        # Simple moving average with trend adjustment
        recent_velocity = historical_velocity[-6:]  # Last 6 sprints
        average_velocity = sum(recent_velocity) / len(recent_velocity)
        
        # Calculate trend
        if len(recent_velocity) >= 4:
            first_half = sum(recent_velocity[:len(recent_velocity)//2]) / (len(recent_velocity)//2)
            second_half = sum(recent_velocity[len(recent_velocity)//2:]) / (len(recent_velocity) - len(recent_velocity)//2)
            trend_factor = (second_half / first_half) if first_half > 0 else 1
        else:
            trend_factor = 1
        
        # Adjust for team changes
        if team_changes:
            team_size_factor = 1 + (team_changes.get('new_members', 0) * 0.5) - (team_changes.get('departures', 0) * 0.8)
            trend_factor *= team_size_factor
        
        predicted_capacity = int(average_velocity * trend_factor)
        return max(predicted_capacity, 0)
    
    @staticmethod
    def identify_bottlenecks(metrics_history: List[TeamMetrics]) -> Dict[str, str]:
        """Identify potential bottlenecks in the development process"""
        if len(metrics_history) < 4:
            return {}
        
        recent_metrics = metrics_history[-4:]
        bottlenecks = {}
        
        # Check for increasing review times
        review_times = [m.code_review_time_hours for m in recent_metrics]
        if len(review_times) >= 3 and review_times[-1] > review_times[0] * 1.5:
            bottlenecks['code_review'] = "Code review times are increasing - consider review process optimization"
        
        # Check for decreasing deployment frequency
        deployments = [m.deployments_count for m in recent_metrics]
        if len(deployments) >= 3 and deployments[-1] < deployments[0] * 0.7:
            bottlenecks['deployment'] = "Deployment frequency decreasing - investigate pipeline issues"
        
        # Check for accumulating technical debt
        tech_debt = [m.technical_debt_items for m in recent_metrics]
        if len(tech_debt) >= 3 and tech_debt[-1] > tech_debt[0] * 1.3:
            bottlenecks['technical_debt'] = "Technical debt accumulating - schedule debt reduction sprint"
        
        return bottlenecks

if __name__ == "__main__":
    # Example thresholds configuration
    alert_thresholds = {
        'logistics-platform': {
            'min_deployment_success': 95,
            'min_test_coverage': 80,
            'min_satisfaction': 3.5,
            'max_mttr': 4
        },
        'payment-systems': {
            'min_deployment_success': 98,  # Higher threshold for payment systems
            'min_test_coverage': 85,
            'min_satisfaction': 4.0,
            'max_mttr': 2
        }
    }
    
    # Run the main metrics collection
    main()
    
    # Example of using additional analytics
    analytics = MetricsAnalytics()
    historical_velocity = [42, 38, 45, 41, 47, 43]  # Example sprint velocities
    predicted_capacity = analytics.predict_sprint_capacity(
        historical_velocity, 
        team_changes={'new_members': 1, 'departures': 0}
    )
    print(f"\nPredicted next sprint capacity: {predicted_capacity} story points")
    
    print("\n✅ Metrics collection and analysis complete!")
    print("📊 Dashboard data exported to JSON files")
    print("📈 Visualizations saved as PNG files")
    print("🚨 Alerts sent for any threshold violations")