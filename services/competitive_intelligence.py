#!/usr/bin/env python3
"""
GrantAI Pro - Complete Competitive Intelligence Service
Tracks user activity and calculates competition levels for grant opportunities
Phase 2 Week 4: Complete integration with all required methods
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pymongo import MongoClient
from bson import ObjectId
import os
from collections import defaultdict, Counter
from dotenv import load_dotenv

load_dotenv()

class CompetitiveIntelligenceService:
    """Service for tracking competitive intelligence and user activity"""
    
    def __init__(self, mongo_uri: str = None):
        """Initialize the competitive intelligence service"""
        self.mongo_uri = mongo_uri if mongo_uri is not None else os.environ.get('MONGO_URI', 'mongodb://localhost:27017/grantai')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.grantai
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create database indexes for competitive intelligence queries"""
        try:
            # User activity indexes
            self.db.user_activity.create_index([('opportunity_id', 1), ('timestamp', -1)])
            self.db.user_activity.create_index([('user_id', 1), ('timestamp', -1)])
            self.db.user_activity.create_index([('activity_type', 1), ('timestamp', -1)])
            
            # Competitive insights indexes
            self.db.competitive_insights.create_index([('opportunity_id', 1)])
            self.db.competitive_insights.create_index([('competition_level', 1)])
            self.db.competitive_insights.create_index([('updated_at', -1)])
            
            print("✅ Competitive intelligence indexes created")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    def track_user_activity(self, user_id: str, opportunity_id: str, activity_type: str, 
                          organization_type: str = None, organization_size: str = None):
        """Track user activity for competitive intelligence"""
        try:
            # Skip if user_id is None or invalid
            if not user_id:
                print("⚠️ Warning: Cannot track activity for None user_id")
                return
            
            activity = {
                'user_id': user_id,
                'opportunity_id': opportunity_id,
                'activity_type': activity_type,
                'timestamp': datetime.utcnow(),
                'organization_type': organization_type or 'unknown',
                'organization_size': organization_size or 'unknown'
            }
            
            # Only insert if opportunity_id is valid
            if opportunity_id:
                self.db.user_activity.insert_one(activity)
                print(f"📊 Tracked activity: {opportunity_id} on {activity_type} by user {user_id}")
                
                # Update competitive insights
                self._update_competitive_insights(opportunity_id)
            else:
                # Track general activity without opportunity_id
                self.db.user_activity.insert_one(activity)
                print(f"📊 Tracked activity: {opportunity_id} on {activity_type} by user {user_id}")
                
        except Exception as e:
            print(f"❌ Error tracking activity: {e}")
    
    def _update_competitive_insights(self, opportunity_id: str):
        """Update competitive insights for an opportunity"""
        try:
            if not opportunity_id:
                return
                
            # Count different types of activity
            pipeline = [
                {'$match': {'opportunity_id': opportunity_id}},
                {'$group': {
                    '_id': '$activity_type',
                    'count': {'$sum': 1},
                    'unique_users': {'$addToSet': '$user_id'}
                }}
            ]
            
            activity_stats = list(self.db.user_activity.aggregate(pipeline))
            
            # Calculate metrics
            total_interested = 0
            total_started = 0
            total_submitted = 0
            unique_users = set()
            
            for stat in activity_stats:
                activity_type = stat['_id']
                count = stat['count']
                users = set(stat['unique_users'])
                unique_users.update(users)
                
                if activity_type in ['viewed_opportunity', 'viewed_in_list', 'saved_opportunity']:
                    total_interested += count
                elif activity_type in ['started_application', 'clicked_view_details']:
                    total_started += count
                elif activity_type in ['submitted_application']:
                    total_submitted += count
            
            # Determine competition level
            total_users = len(unique_users)
            competition_level = self._calculate_competition_level(total_users, total_interested, total_started)
            
            # Calculate success rate estimate
            success_rate = self._estimate_success_rate(competition_level, total_users)
            
            # Update or create competitive insight
            insight = {
                'opportunity_id': opportunity_id,
                'competition_level': competition_level,
                'total_users_interested': total_users,
                'total_users_started': len([s for s in activity_stats if s['_id'] in ['started_application', 'clicked_view_details']]),
                'total_users_submitted': len([s for s in activity_stats if s['_id'] == 'submitted_application']),
                'estimated_success_rate': success_rate,
                'daily_new_applicants': self._calculate_daily_new_applicants(opportunity_id),
                'weekly_trend': self._calculate_weekly_trend(opportunity_id),
                'updated_at': datetime.utcnow()
            }
            
            self.db.competitive_insights.update_one(
                {'opportunity_id': opportunity_id},
                {'$set': insight},
                upsert=True
            )
            
        except Exception as e:
            print(f"❌ Error updating competitive insights: {e}")
    
    def _calculate_competition_level(self, users: int, interested: int, started: int) -> str:
        """Calculate competition level based on activity metrics"""
        if users >= 100 or interested >= 200:
            return 'high'
        elif users >= 30 or interested >= 75:
            return 'medium'
        elif users >= 10 or interested >= 20:
            return 'low'
        else:
            return 'low'
    
    def _estimate_success_rate(self, competition_level: str, users: int) -> float:
        """Estimate success rate based on competition"""
        base_rates = {
            'high': 0.05,
            'medium': 0.12,
            'low': 0.25
        }
        
        base_rate = base_rates.get(competition_level, 0.15)
        
        # Adjust based on user count
        if users > 200:
            return max(0.02, base_rate * 0.5)
        elif users > 100:
            return max(0.05, base_rate * 0.7)
        elif users < 10:
            return min(0.4, base_rate * 1.5)
        
        return base_rate
    
    def _calculate_daily_new_applicants(self, opportunity_id: str) -> int:
        """Calculate daily new applicants trend"""
        try:
            yesterday = datetime.utcnow() - timedelta(days=1)
            count = self.db.user_activity.count_documents({
                'opportunity_id': opportunity_id,
                'activity_type': {'$in': ['started_application', 'viewed_opportunity']},
                'timestamp': {'$gte': yesterday}
            })
            return count
        except:
            return 0
    
    def _calculate_weekly_trend(self, opportunity_id: str) -> str:
        """Calculate weekly trend direction"""
        try:
            now = datetime.utcnow()
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            recent_count = self.db.user_activity.count_documents({
                'opportunity_id': opportunity_id,
                'timestamp': {'$gte': week_ago}
            })
            
            previous_count = self.db.user_activity.count_documents({
                'opportunity_id': opportunity_id,
                'timestamp': {'$gte': two_weeks_ago, '$lt': week_ago}
            })
            
            if recent_count > previous_count * 1.2:
                return 'increasing'
            elif recent_count < previous_count * 0.8:
                return 'decreasing'
            else:
                return 'stable'
        except:
            return 'stable'
    
    def get_competition_analysis(self, opportunity_id: str) -> Dict:
        """Get detailed competition analysis for an opportunity"""
        try:
            if not opportunity_id:
                return {'competition_level': 'unknown'}
                
            insight = self.db.competitive_insights.find_one({'opportunity_id': opportunity_id})
            
            if insight:
                return {
                    'competition_level': insight.get('competition_level', 'unknown'),
                    'total_users_interested': insight.get('total_users_interested', 0),
                    'total_users_started': insight.get('total_users_started', 0),
                    'total_users_submitted': insight.get('total_users_submitted', 0),
                    'estimated_success_rate': insight.get('estimated_success_rate', 0.15),
                    'daily_new_applicants': insight.get('daily_new_applicants', 0),
                    'weekly_trend': insight.get('weekly_trend', 'stable'),
                    'updated_at': insight.get('updated_at', datetime.utcnow())
                }
            else:
                # Return default values if no data exists
                return {
                    'competition_level': 'unknown',
                    'total_users_interested': 0,
                    'total_users_started': 0,
                    'total_users_submitted': 0,
                    'estimated_success_rate': 0.15,
                    'daily_new_applicants': 0,
                    'weekly_trend': 'stable'
                }
        except Exception as e:
            print(f"❌ Error getting competition analysis: {e}")
            return {'competition_level': 'unknown'}
    
    def get_user_activity_summary(self, user_id: str) -> Dict:
        """Get activity summary for a user"""
        try:
            if not user_id:
                return {}
                
            # Count user activities
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': '$activity_type',
                    'count': {'$sum': 1}
                }}
            ]
            
            activities = list(self.db.user_activity.aggregate(pipeline))
            
            summary = {
                'opportunities_viewed': 0,
                'applications_started': 0,
                'applications_submitted': 0,
                'success_rate': 0.0,
                'rank': None
            }
            
            for activity in activities:
                activity_type = activity['_id']
                count = activity['count']
                
                if activity_type in ['viewed_opportunity', 'viewed_in_list']:
                    summary['opportunities_viewed'] += count
                elif activity_type in ['started_application']:
                    summary['applications_started'] += count
                elif activity_type in ['submitted_application']:
                    summary['applications_submitted'] += count
            
            # Calculate success rate
            if summary['applications_started'] > 0:
                summary['success_rate'] = (summary['applications_submitted'] / summary['applications_started']) * 100
            
            return summary
            
        except Exception as e:
            print(f"❌ Error getting user activity summary: {e}")
            return {}
    
    def get_trending_opportunities(self) -> List[Dict]:
        """Get trending opportunities based on recent activity"""
        try:
            # Get opportunities with most recent activity
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': datetime.utcnow() - timedelta(days=7)},
                        'opportunity_id': {'$ne': None}
                    }
                },
                {
                    '$group': {
                        '_id': '$opportunity_id',
                        'activity_count': {'$sum': 1},
                        'unique_users': {'$addToSet': '$user_id'},
                        'last_activity': {'$max': '$timestamp'}
                    }
                },
                {
                    '$project': {
                        'opportunity_id': '$_id',
                        'activity_count': 1,
                        'total_interest': {'$size': '$unique_users'},
                        'last_activity': 1
                    }
                },
                {'$sort': {'activity_count': -1}},
                {'$limit': 10}
            ]
            
            trending = list(self.db.user_activity.aggregate(pipeline))
            
            # Enrich with opportunity details
            result = []
            for trend in trending:
                opportunity_id = trend['opportunity_id']
                opportunity = self.db.opportunities.find_one({'opportunity_id': opportunity_id})
                
                if opportunity:
                    result.append({
                        'opportunity_id': opportunity_id,
                        'title': opportunity.get('title', 'Unknown Opportunity'),
                        'agency': opportunity.get('agency', 'Unknown Agency'),
                        'activity_increase': min(100, trend['activity_count'] * 5),  # Simulated percentage
                        'total_interest': trend['total_interest'],
                        'last_activity': trend['last_activity']
                    })
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting trending opportunities: {e}")
            return []
    
    def get_global_competition_stats(self) -> Dict:
        """Get global competition statistics"""
        try:
            # Count opportunities by competition level
            pipeline = [
                {
                    '$group': {
                        '_id': '$competition_level',
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            stats = list(self.db.competitive_insights.aggregate(pipeline))
            
            result = {
                'high_competition': 0,
                'medium_competition': 0,
                'low_competition': 0,
                'unknown_competition': 0,
                'avg_success_rate': 0.0
            }
            
            total_opportunities = 0
            total_success_rate = 0.0
            
            for stat in stats:
                level = stat['_id']
                count = stat['count']
                total_opportunities += count
                
                if level == 'high':
                    result['high_competition'] = count
                    total_success_rate += count * 0.08
                elif level == 'medium':
                    result['medium_competition'] = count
                    total_success_rate += count * 0.15
                elif level == 'low':
                    result['low_competition'] = count
                    total_success_rate += count * 0.25
                else:
                    result['unknown_competition'] = count
                    total_success_rate += count * 0.15
            
            if total_opportunities > 0:
                result['avg_success_rate'] = total_success_rate / total_opportunities
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting global competition stats: {e}")
            return {
                'high_competition': 0,
                'medium_competition': 0,
                'low_competition': 0,
                'avg_success_rate': 0.15
            }
    
    def get_user_recommendations(self, user_id: str) -> List[Dict]:
        """Get personalized opportunity recommendations"""
        try:
            if not user_id:
                return []
                
            # Get user's activity patterns
            user_activities = list(self.db.user_activity.find(
                {'user_id': user_id},
                {'opportunity_id': 1, 'activity_type': 1}
            ).limit(50))
            
            if not user_activities:
                return []
            
            # Get opportunities the user has interacted with
            viewed_opportunities = set()
            for activity in user_activities:
                if activity.get('opportunity_id'):
                    viewed_opportunities.add(activity['opportunity_id'])
            
            # Find similar opportunities with low competition
            recommendations = []
            pipeline = [
                {
                    '$match': {
                        'competition_level': {'$in': ['low', 'medium']},
                        'opportunity_id': {'$nin': list(viewed_opportunities)}
                    }
                },
                {'$sort': {'estimated_success_rate': -1}},
                {'$limit': 5}
            ]
            
            insights = list(self.db.competitive_insights.aggregate(pipeline))
            
            for insight in insights:
                opportunity = self.db.opportunities.find_one({
                    'opportunity_id': insight['opportunity_id']
                })
                
                if opportunity:
                    recommendations.append({
                        'opportunity_id': insight['opportunity_id'],
                        'title': opportunity.get('title', 'Unknown'),
                        'agency': opportunity.get('agency', 'Unknown'),
                        'success_probability': insight.get('estimated_success_rate', 0.15),
                        'competition_level': insight.get('competition_level', 'unknown'),
                        'amount_max': opportunity.get('amount_max', 0)
                    })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error getting user recommendations: {e}")
            return []
    
    def get_test_data(self) -> Dict:
        """Get test data for API verification"""
        return {
            'status': 'active',
            'total_opportunities_tracked': self.db.competitive_insights.count_documents({}),
            'total_user_activities': self.db.user_activity.count_documents({}),
            'last_updated': datetime.utcnow().isoformat()
        }
    