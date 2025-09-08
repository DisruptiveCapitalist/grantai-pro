#!/usr/bin/env python3
"""
GrantAI Pro - Competitive Intelligence API Endpoints
REST API endpoints for competitive intelligence features
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import sys
import os

# Add the parent directory to the path so we can import our service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.competitive_intelligence import CompetitiveIntelligenceService

# Create Blueprint for competitive intelligence routes
competitive_bp = Blueprint('competitive', __name__, url_prefix='/api/competitive')

# Initialize competitive intelligence service
comp_service = CompetitiveIntelligenceService()

@competitive_bp.route('/track', methods=['POST'])
def track_activity():
    """
    Track user activity for competitive intelligence
    
    POST /api/competitive/track
    Body: {
        "action": "view|save|generate_app|download|share",
        "opportunity_id": "grant_opportunity_id",
        "metadata": { ... optional metadata ... }
    }
    """
    try:
        # Get user from session (for now, use a test user if no session)
        user_id = session.get('user_id', 'test_user')
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        action = data.get('action')
        opportunity_id = data.get('opportunity_id')
        metadata = data.get('metadata', {})
        
        if not action or not opportunity_id:
            return jsonify({'error': 'action and opportunity_id are required'}), 400
        
        # Add session info to metadata
        metadata['session_id'] = session.get('session_id', 'test_session')
        metadata['user_agent'] = request.headers.get('User-Agent', 'Unknown')
        metadata['ip_address'] = request.remote_addr
        
        # Track the activity
        success = comp_service.track_user_activity(
            user_id=str(user_id),
            action=action,
            opportunity_id=opportunity_id,
            metadata=metadata
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Activity tracked successfully'
            })
        else:
            return jsonify({'error': 'Failed to track activity'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/opportunity/<opportunity_id>', methods=['GET'])
def get_competition_data(opportunity_id):
    """
    Get competition data for a specific opportunity
    
    GET /api/competitive/opportunity/{opportunity_id}
    """
    try:
        # Get comprehensive competitive insights
        insights = comp_service.get_competitive_insights(opportunity_id)
        
        if not insights:
            return jsonify({'error': 'No competitive data found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': insights
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/trending', methods=['GET'])
def get_trending_opportunities():
    """
    Get trending grant opportunities
    
    GET /api/competitive/trending?limit=10&days=3
    """
    try:
        limit = int(request.args.get('limit', 10))
        days = int(request.args.get('days', 3))
        
        # Validate parameters
        if limit > 50:
            limit = 50
        if days > 30:
            days = 30
        
        trending = comp_service.get_trending_opportunities(
            limit=limit,
            timeframe_days=days
        )
        
        return jsonify({
            'status': 'success',
            'data': trending,
            'count': len(trending)
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    Get personalized low-competition grant recommendations
    
    GET /api/competitive/recommendations?limit=5
    """
    try:
        user_id = session.get('user_id', 'test_user')
        
        limit = int(request.args.get('limit', 5))
        if limit > 20:
            limit = 20
        
        recommendations = comp_service.recommend_low_competition_grants(
            user_id=str(user_id),
            limit=limit
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/activity/summary', methods=['GET'])
def get_activity_summary():
    """
    Get user's activity summary
    
    GET /api/competitive/activity/summary?days=30
    """
    try:
        user_id = session.get('user_id', 'test_user')
        
        days = int(request.args.get('days', 30))
        if days > 365:
            days = 365
        
        summary = comp_service.get_user_activity_summary(
            user_id=str(user_id),
            days=days
        )
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/competition/level/<opportunity_id>', methods=['GET'])
def get_competition_level(opportunity_id):
    """
    Get just the competition level for an opportunity
    
    GET /api/competitive/competition/level/{opportunity_id}
    """
    try:
        days = int(request.args.get('days', 7))
        
        competition = comp_service.calculate_competition_level(
            opportunity_id=opportunity_id,
            timeframe_days=days
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'opportunity_id': opportunity_id,
                'competition_level': competition.get('competition_level'),
                'score': competition.get('score'),
                'unique_users': competition.get('unique_users'),
                'trending': competition.get('trending', False)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/stats/global', methods=['GET'])
def get_global_stats():
    """
    Get global competitive intelligence statistics
    
    GET /api/competitive/stats/global
    """
    try:
        # Calculate global stats
        total_tracked_opportunities = comp_service.db.competitive_insights.count_documents({})
        high_competition = comp_service.db.competitive_insights.count_documents({
            'competition_level': 'high'
        })
        trending_count = comp_service.db.competitive_insights.count_documents({
            'trending': True
        })
        
        # Activity stats from last 7 days
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent_activities = comp_service.db.user_activity.count_documents({
            'timestamp': {'$gte': cutoff}
        })
        
        active_users = len(comp_service.db.user_activity.distinct('user_id', {
            'timestamp': {'$gte': cutoff}
        }))
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_tracked_opportunities': total_tracked_opportunities,
                'high_competition_opportunities': high_competition,
                'trending_opportunities': trending_count,
                'recent_activities': recent_activities,
                'active_users_7d': active_users,
                'competition_distribution': {
                    'high': comp_service.db.competitive_insights.count_documents({'competition_level': 'high'}),
                    'medium': comp_service.db.competitive_insights.count_documents({'competition_level': 'medium'}),
                    'low': comp_service.db.competitive_insights.count_documents({'competition_level': 'low'})
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@competitive_bp.route('/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    try:
        # Generate some test activity
        test_opportunity = "test_opp_" + str(datetime.now().timestamp())
        
        # Track some test activities
        comp_service.track_user_activity("test_user_1", "view", test_opportunity)
        comp_service.track_user_activity("test_user_2", "save", test_opportunity)
        comp_service.track_user_activity("test_user_1", "generate_app", test_opportunity)
        
        # Get competition level
        competition = comp_service.calculate_competition_level(test_opportunity)
        
        return jsonify({
            'status': 'success',
            'message': 'Competitive Intelligence API is working!',
            'test_data': {
                'test_opportunity': test_opportunity,
                'competition_level': competition['competition_level'],
                'unique_users': competition['unique_users'],
                'total_activities': competition['total_activities']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Test failed: {str(e)}'}), 500


# Utility function to register the blueprint
def register_competitive_routes(app):
    """Register competitive intelligence routes with Flask app"""
    app.register_blueprint(competitive_bp)
    print("✅ Competitive intelligence API routes registered")


if __name__ == "__main__":
    # Test the API endpoints
    print("🧪 Testing Competitive Intelligence API...")
    print("✅ All competitive intelligence API endpoints loaded successfully!")
    print("\n📡 Available endpoints:")
    print("   - GET  /api/competitive/test")
    print("   - POST /api/competitive/track")
    print("   - GET  /api/competitive/trending")
    print("   - GET  /api/competitive/opportunity/{id}")
    print("   - GET  /api/competitive/recommendations")
    print("   - GET  /api/competitive/activity/summary")
    print("   - GET  /api/competitive/stats/global")
    