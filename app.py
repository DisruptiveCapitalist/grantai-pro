#!/usr/bin/env python3
"""
GrantAI Pro - Integrated Main Flask App with Competitive Intelligence
Phase 2 Week 4: Frontend Integration with Competition Badges and Real Data
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import json
from functools import wraps
import logging

# Import your existing competitive intelligence
try:
    from services.competitive_intelligence import CompetitiveIntelligenceService
    from api.competitive import competitive_bp
except ImportError:
    print("⚠️ Competitive intelligence modules not found. Please ensure services/ and api/ directories exist.")
    CompetitiveIntelligenceService = None
    competitive_bp = None

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'grantai-pro-secret-key-2025')

# MongoDB Atlas Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://sam_db_user:your_password@cluster0.s7k3hey.mongodb.net/grantai')

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client.grantai
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB Atlas connection successful")
    
    # Initialize collections
    opportunities_collection = db.opportunities
    users_collection = db.users
    applications_collection = db.applications
    competitive_insights_collection = db.competitive_insights
    user_activity_collection = db.user_activity
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("💡 Please check your MONGO_URI environment variable")
    client = None
    db = None
    opportunities_collection = None
    users_collection = None
    applications_collection = None
    competitive_insights_collection = None
    user_activity_collection = None

# Initialize Competitive Intelligence Service
competitive_service = None
if CompetitiveIntelligenceService and db is not None:
    competitive_service = CompetitiveIntelligenceService(MONGO_URI)  # Pass URI string, not db object
    print("✅ Competitive Intelligence Service initialized")

# Register competitive intelligence blueprint if available
if competitive_bp:
    app.register_blueprint(competitive_bp, url_prefix='/api/competitive')
    print("✅ Competitive Intelligence API routes registered")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Subscription tiers and limits
SUBSCRIPTION_LIMITS = {
    'free': {'opportunities_per_month': 50, 'applications_per_month': 3},
    'starter': {'opportunities_per_month': 200, 'applications_per_month': 15},
    'professional': {'opportunities_per_month': 1000, 'applications_per_month': 50},
    'enterprise': {'opportunities_per_month': -1, 'applications_per_month': -1}  # Unlimited
}

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_subscription(user_id):
    """Get user's current subscription tier"""
    if users_collection is None:
        return 'free'
    user = users_collection.find_one({'_id': user_id})
    return user.get('subscription_tier', 'free') if user else 'free'

def calculate_competition_level(opportunity_id):
    """Calculate competition level for an opportunity"""
    if not competitive_service:
        return "unknown"
    
    try:
        competition_data = competitive_service.get_competition_analysis(opportunity_id)
        return competition_data.get('competition_level', 'unknown')
    except:
        return "unknown"

def add_competition_badges(opportunities):
    """Add competition level badges to opportunity list"""
    if not opportunities:
        return opportunities
    
    for opp in opportunities:
        # Get competition level
        competition_level = calculate_competition_level(opp.get('opportunity_id', opp.get('_id')))
        
        # Add badge information
        opp['competition_level'] = competition_level
        opp['competition_badge'] = {
            'high': {'color': 'red', 'text': 'High Competition', 'icon': '🔥'},
            'medium': {'color': 'orange', 'text': 'Medium Competition', 'icon': '⚡'},
            'low': {'color': 'green', 'text': 'Low Competition', 'icon': '🎯'},
            'unknown': {'color': 'gray', 'text': 'Competition Unknown', 'icon': '❓'}
        }.get(competition_level, {'color': 'gray', 'text': 'Unknown', 'icon': '❓'})
    
    return opportunities

@app.route('/')
def index():
    """Homepage with public metrics"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    # Get public metrics from database
    public_metrics = {}
    if db is not None:
        try:
            metrics = db.global_metrics.find_one({'metric_type': 'global_stats'})
            if metrics:
                public_metrics = {
                    'total_awards_won': metrics.get('total_awards_won', 0),
                    'total_applications_filed': metrics.get('total_applications_filed', 0),
                    'total_users_active': metrics.get('total_users_active', 0),
                    'success_rate': metrics.get('success_rate', 0),
                    'total_award_value': metrics.get('total_award_value', 0)
                }
        except Exception as e:
            logger.error(f"Error fetching public metrics: {e}")
    
    # Default metrics if none found
    if not public_metrics:
        public_metrics = {
            'total_awards_won': 142,
            'total_applications_filed': 876,
            'total_users_active': 1250,
            'success_rate': 16.2,
            'total_award_value': 48500000
        }
    
    return render_template('index.html', metrics=public_metrics)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        organization = request.form.get('organization')
        
        if not all([email, password, first_name, last_name]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        # Check database connection
        if users_collection is None:
            flash('Database connection error', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if users_collection.find_one({'email': email}):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user_data = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'organization': organization,
            'subscription_tier': 'free',
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        try:
            result = users_collection.insert_one(user_data)
            session['user_id'] = str(result.inserted_id)
            session['user_email'] = email
            session['user_name'] = f"{first_name} {last_name}"
            
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            flash('Registration failed', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check database connection
        if users_collection is None:
            flash('Database connection error', 'error')
            return render_template('login.html')
        
        try:
            user = users_collection.find_one({'email': email})
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = str(user['_id'])
                session['user_email'] = user['email']
                session['user_name'] = f"{user['first_name']} {user['last_name']}"
                session['subscription_tier'] = user.get('subscription_tier', 'free')
                
                # Update last login
                users_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
        except Exception as e:
            logger.error(f"Error during login: {e}")
            flash('Login failed', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with competitive intelligence"""
    user_id = session.get('user_id')
    subscription_tier = session.get('subscription_tier', 'free')
    
    # Get recent opportunities with competition data
    opportunities = []
    if opportunities_collection is not None:
        try:
            # Get recent opportunities (limit based on subscription)
            limit = SUBSCRIPTION_LIMITS[subscription_tier]['opportunities_per_month']
            if limit == -1:  # Unlimited
                limit = 100  # Reasonable default for display
            
            cursor = opportunities_collection.find({'is_active': True}).limit(limit).sort('close_date', 1)
            opportunities = list(cursor)
            
            # Add competition badges
            opportunities = add_competition_badges(opportunities)
            
        except Exception as e:
            logger.error(f"Error fetching opportunities: {e}")
    
    # Get user's recent activity
    recent_activity = []
    if user_activity_collection is not None:
        try:
            cursor = user_activity_collection.find({'user_id': user_id}).limit(10).sort('timestamp', -1)
            recent_activity = list(cursor)
        except Exception as e:
            logger.error(f"Error fetching user activity: {e}")
    
    # Get competitive insights summary
    competitive_summary = {}
    if competitive_service:
        try:
            competitive_summary = competitive_service.get_user_activity_summary(user_id)
        except Exception as e:
            logger.error(f"Error fetching competitive summary: {e}")
    
    return render_template('dashboard.html', 
                         opportunities=opportunities[:20],  # Show top 20
                         recent_activity=recent_activity,
                         competitive_summary=competitive_summary,
                         subscription_tier=subscription_tier,
                         user_name=session.get('user_name'))

@app.route('/opportunities')
@login_required
def opportunities():
    """Opportunities listing with competition indicators"""
    user_id = session.get('user_id')
    subscription_tier = session.get('subscription_tier', 'free')
    
    # Get filter parameters
    agency_filter = request.args.get('agency', '')
    amount_min = request.args.get('amount_min', 0, type=int)
    amount_max = request.args.get('amount_max', 0, type=int)
    competition_filter = request.args.get('competition', '')  # low, medium, high
    
    # Build query
    query = {'is_active': True}
    if agency_filter:
        query['agency'] = {'$regex': agency_filter, '$options': 'i'}
    if amount_min:
        query['amount_min'] = {'$gte': amount_min}
    if amount_max:
        query['amount_max'] = {'$lte': amount_max}
    
    opportunities = []
    if opportunities_collection is not None:
        try:
            # Get opportunities with filters
            limit = SUBSCRIPTION_LIMITS[subscription_tier]['opportunities_per_month']
            if limit == -1:  # Unlimited
                limit = 500  # Higher limit for opportunities page
            
            cursor = opportunities_collection.find(query).limit(limit).sort('close_date', 1)
            opportunities = list(cursor)
            
            # Add competition badges
            opportunities = add_competition_badges(opportunities)
            
            # Filter by competition level if specified
            if competition_filter:
                opportunities = [opp for opp in opportunities if opp.get('competition_level') == competition_filter]
            
            # Track user activity
            if competitive_service:
                competitive_service.track_user_activity(user_id, None, 'viewed_opportunities_list')
                
        except Exception as e:
            logger.error(f"Error fetching filtered opportunities: {e}")
    
    # Get unique agencies for filter dropdown
    agencies = []
    if opportunities_collection is not None:
        try:
            agencies = opportunities_collection.distinct('agency')
        except Exception as e:
            logger.error(f"Error fetching agencies: {e}")
    
    return render_template('opportunities.html',
                         opportunities=opportunities,
                         agencies=agencies,
                         filters={
                             'agency': agency_filter,
                             'amount_min': amount_min,
                             'amount_max': amount_max,
                             'competition': competition_filter
                         })

@app.route('/opportunity/<opportunity_id>')
@login_required
def opportunity_detail(opportunity_id):
    """Detailed opportunity view with competitive analysis"""
    user_id = session.get('user_id')
    
    opportunity = None
    competitive_analysis = {}
    
    if opportunities_collection is not None:
        try:
            opportunity = opportunities_collection.find_one({'opportunity_id': opportunity_id})
            if not opportunity:
                opportunity = opportunities_collection.find_one({'_id': opportunity_id})
            
            if opportunity:
                # Add competition badge
                opportunity = add_competition_badges([opportunity])[0]
                
                # Get detailed competitive analysis
                if competitive_service:
                    competitive_analysis = competitive_service.get_competition_analysis(opportunity_id)
                    
                    # Track that user viewed this opportunity
                    competitive_service.track_user_activity(user_id, opportunity_id, 'viewed_opportunity')
                    
        except Exception as e:
            logger.error(f"Error fetching opportunity detail: {e}")
    
    if not opportunity:
        flash('Opportunity not found', 'error')
        return redirect(url_for('opportunities'))
    
    return render_template('opportunity_detail.html',
                         opportunity=opportunity,
                         competitive_analysis=competitive_analysis)

@app.route('/competitive-dashboard')
@login_required
def competitive_dashboard():
    """Competitive intelligence dashboard"""
    user_id = session.get('user_id')
    
    dashboard_data = {}
    if competitive_service:
        try:
            # Get comprehensive competitive analytics
            dashboard_data = {
                'user_summary': competitive_service.get_user_activity_summary(user_id),
                'trending_opportunities': competitive_service.get_trending_opportunities(),
                'competition_stats': competitive_service.get_global_competition_stats(),
                'success_predictions': competitive_service.get_user_recommendations(user_id)
            }
        except Exception as e:
            logger.error(f"Error fetching competitive dashboard data: {e}")
    
    return render_template('competitive_dashboard.html', data=dashboard_data)

# API Routes
@app.route('/api/opportunities/competition/<opportunity_id>')
@login_required
def api_opportunity_competition(opportunity_id):
    """API endpoint for opportunity competition data"""
    if not competitive_service:
        return jsonify({'error': 'Competitive intelligence not available'}), 503
    
    try:
        competition_data = competitive_service.get_competition_analysis(opportunity_id)
        return jsonify(competition_data)
    except Exception as e:
        logger.error(f"Error fetching competition data: {e}")
        return jsonify({'error': 'Failed to fetch competition data'}), 500

@app.route('/api/track-activity', methods=['POST'])
@login_required
def api_track_activity():
    """API endpoint to track user activity"""
    if not competitive_service:
        return jsonify({'error': 'Activity tracking not available'}), 503
    
    user_id = session.get('user_id')
    data = request.get_json()
    
    opportunity_id = data.get('opportunity_id')
    activity_type = data.get('activity_type')
    
    if not activity_type:
        return jsonify({'error': 'Activity type required'}), 400
    
    try:
        competitive_service.track_user_activity(user_id, opportunity_id, activity_type)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error tracking activity: {e}")
        return jsonify({'error': 'Failed to track activity'}), 500

# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    """Format currency"""
    if not amount:
        return "Not specified"
    return f"${amount:,.0f}"

@app.template_filter('days_until')
def days_until_filter(date_string):
    """Calculate days until a date"""
    if not date_string:
        return "Unknown"
    
    try:
        if isinstance(date_string, str):
            target_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            target_date = date_string
        
        days_diff = (target_date - datetime.now()).days
        
        if days_diff < 0:
            return "Closed"
        elif days_diff == 0:
            return "Today"
        elif days_diff == 1:
            return "Tomorrow"
        else:
            return f"{days_diff} days"
    except:
        return "Unknown"

if __name__ == '__main__':
    print("🚀 Starting GrantAI Pro - Integrated Application")
    print("📊 Phase 2 Week 4: Competitive Intelligence Frontend Integration")
    print("🏆 Features: Competition badges, real-time tracking, competitive dashboard")
    
    if not client:
        print("⚠️ Warning: Running without database connection")
    else:
        print("✅ MongoDB Atlas connected")
    
    if not competitive_service:
        print("⚠️ Warning: Competitive intelligence service not available")
    else:
        print("✅ Competitive intelligence active")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
    