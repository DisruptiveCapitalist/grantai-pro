# app.py - Updated Flask app with new pricing and promo code system
"""
GrantAI Pro - Main Flask Application
Updated with new pricing structure, promo codes, and premium features
"""

from flask import Flask, render_template, session, jsonify, request, redirect, url_for
from flask_session import Session
import pymongo
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import logging

# Import services and API blueprints
from services.award_tracker import AwardTracker
from services.competitive_intelligence import CompetitiveIntelligence
from api.awards import init_awards_api
from api.billing import init_billing_api
from config.pricing_plans import PricingCalculator, PRICING_PLANS, get_plan_comparison
from utils.database import init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Initialize Flask-Session
    Session(app)
    
    # MongoDB connection
    try:
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/grantai')
        client = MongoClient(mongo_uri)
        db = client.get_database()
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        raise
    
    # Initialize services
    award_tracker = AwardTracker(db)
    competitive_intelligence = CompetitiveIntelligence(db)
    pricing_calculator = PricingCalculator(db)
    
    # Initialize API blueprints
    init_awards_api(app, db, award_tracker)
    init_billing_api(app, db)
    
    # Initialize database collections and indexes
    init_database(db)
    
    # Helper function to check subscription limits
    def check_subscription_limits(user_id, feature_type):
        """Check if user has access to a feature based on their subscription"""
        try:
            subscription = db.subscriptions.find_one({
                "user_id": user_id,
                "status": {"$in": ["trialing", "active"]}
            })
            
            if not subscription:
                return {"allowed": False, "reason": "No active subscription"}
            
            plan_id = subscription.get('plan_id', 'personal')
            plan_limits = PRICING_PLANS.get(plan_id, {}).get('limits', {})
            
            if feature_type == 'applications':
                limit = plan_limits.get('applications_per_month', 0)
                used = subscription.get('applications_used_this_period', 0)
                
                if limit == "unlimited":
                    return {"allowed": True, "remaining": "unlimited"}
                elif used >= limit:
                    return {"allowed": False, "reason": f"Monthly limit of {limit} applications reached"}
                else:
                    return {"allowed": True, "remaining": limit - used}
            
            elif feature_type == 'competitive_intelligence':
                ci_level = plan_limits.get('competitive_intelligence', 'none')
                return {"allowed": ci_level in ['basic', 'full'], "level": ci_level}
            
            elif feature_type == 'full_writing_service':
                has_service = plan_limits.get('full_writing_service', False)
                return {"allowed": has_service}
            
            return {"allowed": True}
            
        except Exception as e:
            logger.error(f"Error checking subscription limits: {str(e)}")
            return {"allowed": False, "reason": "Error checking limits"}
    
    # Routes
    @app.route('/')
    def home():
        """Homepage with public metrics dashboard"""
        try:
            # Get public metrics for homepage display
            metrics = award_tracker.get_award_metrics()
            success_stories = award_tracker.get_public_success_stories(limit=3)
            
            # Get latest opportunities for homepage preview
            recent_opportunities = list(db.opportunities.find(
                {"is_active": True},
                sort=[("post_date", -1)],
                limit=6
            ))
            
            # Calculate trending stats
            trending_stats = {
                "applications_this_week": db.user_activities.count_documents({
                    "activity_type": "application_started",
                    "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
                }),
                "new_opportunities_today": db.opportunities.count_documents({
                    "discovered_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
                }),
                "active_competitions": competitive_intelligence.get_competition_count()
            }
            
            return render_template('index.html', 
                                 metrics=metrics,
                                 success_stories=success_stories,
                                 recent_opportunities=recent_opportunities,
                                 trending_stats=trending_stats)
        except Exception as e:
            logger.error(f"Error loading homepage: {str(e)}")
            return render_template('index.html', 
                                 metrics={}, 
                                 success_stories=[], 
                                 recent_opportunities=[],
                                 trending_stats={})
    
    @app.route('/pricing')
    def pricing():
        """Pricing page with new structure and promo codes"""
        try:
            # Handle promo code from URL parameter
            promo_code = request.args.get('promo', '').upper()
            
            plans = get_plan_comparison()
            
            return render_template('pricing.html', 
                                 plans=plans,
                                 promo_code=promo_code)
        except Exception as e:
            logger.error(f"Error loading pricing page: {str(e)}")
            return render_template('pricing.html', plans=[], promo_code='')
    
    @app.route('/signup')
    def signup():
        """Signup page with plan selection"""
        try:
            # Get plan from URL parameter
            selected_plan = request.args.get('plan', 'professional')
            promo_code = request.args.get('promo', '').upper()
            
            if selected_plan not in PRICING_PLANS:
                selected_plan = 'professional'
            
            plans = get_plan_comparison()
            
            return render_template('signup.html',
                                 plans=plans,
                                 selected_plan=selected_plan,
                                 promo_code=promo_code)
        except Exception as e:
            logger.error(f"Error loading signup page: {str(e)}")
            return render_template('signup.html', 
                                 plans=[], 
                                 selected_plan='professional',
                                 promo_code='')
    
    @app.route('/dashboard')
    def dashboard():
        """User dashboard with subscription-aware features"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        try:
            user_id = session['user_id']
            
            # Check subscription status
            subscription = db.subscriptions.find_one({
                "user_id": user_id,
                "status": {"$in": ["trialing", "active", "past_due"]}
            })
            
            # Get user's awards
            user_awards = award_tracker.get_user_awards(user_id)
            
            # Get user's applications with competition data
            user_applications = list(db.applications.find(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            ))
            
            # Add competition levels and subscription checks
            for app in user_applications:
                competition_level = competitive_intelligence.get_competition_level(
                    app.get('opportunity_id')
                )
                app['competition_level'] = competition_level
            
            # Get subscription limits
            app_limits = check_subscription_limits(user_id, 'applications')
            ci_access = check_subscription_limits(user_id, 'competitive_intelligence')
            premium_service = check_subscription_limits(user_id, 'full_writing_service')
            
            # Get user statistics
            user_stats = {
                "total_applications": len(user_applications),
                "total_awards": len(user_awards),
                "total_amount_won": sum(award.get('award_amount', 0) for award in user_awards),
                "success_rate": (len(user_awards) / len(user_applications) * 100) if user_applications else 0,
                "applications_this_month": len([
                    app for app in user_applications 
                    if app.get('created_at', datetime.min).replace(tzinfo=None) >= 
                       datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                ]),
                "applications_remaining": app_limits.get('remaining', 0)
            }
            
            # Get recommended opportunities
            recommended_opportunities = list(db.opportunities.find(
                {"is_active": True},
                sort=[("relevance_score", -1)],
                limit=5
            ))
            
            return render_template('dashboard.html',
                                 user_awards=user_awards,
                                 user_applications=user_applications,
                                 user_stats=user_stats,
                                 recommended_opportunities=recommended_opportunities,
                                 subscription=subscription,
                                 subscription_limits={
                                     'applications': app_limits,
                                     'competitive_intelligence': ci_access,
                                     'premium_service': premium_service
                                 })
        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            return render_template('dashboard.html', 
                                 user_awards=[], 
                                 user_applications=[],
                                 user_stats={},
                                 recommended_opportunities=[],
                                 subscription=None,
                                 subscription_limits={})
    
    @app.route('/premium')
    def premium_service():
        """Premium grant writing service page"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        try:
            # Check if user has premium access
            premium_access = check_subscription_limits(session['user_id'], 'full_writing_service')
            
            if not premium_access.get('allowed'):
                return render_template('upgrade_required.html', 
                                     feature='Premium Grant Writing Service',
                                     required_plan='premium')
            
            # Get user's premium applications
            premium_applications = list(db.applications.find({
                "user_id": session['user_id'],
                "service_type": "premium_writing"
            }, sort=[("created_at", -1)]))
            
            return render_template('premium_service.html',
                                 premium_applications=premium_applications)
        except Exception as e:
            logger.error(f"Error loading premium service: {str(e)}")
            return render_template('premium_service.html', premium_applications=[])
    
    @app.route('/api/application/generate', methods=['POST'])
    def generate_application():
        """Generate AI application with subscription limits"""
        try:
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_id = session['user_id']
            
            # Check application limits
            app_limits = check_subscription_limits(user_id, 'applications')
            if not app_limits.get('allowed'):
                return jsonify({
                    'error': 'Application limit reached',
                    'reason': app_limits.get('reason'),
                    'upgrade_required': True
                }), 403
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid request data'}), 400
            
            opportunity_id = data.get('opportunity_id')
            service_type = data.get('service_type', 'standard')  # standard or premium
            
            # Check if premium service is requested
            if service_type == 'premium':
                premium_access = check_subscription_limits(user_id, 'full_writing_service')
                if not premium_access.get('allowed'):
                    return jsonify({
                        'error': 'Premium service not available',
                        'upgrade_required': True,
                        'required_plan': 'premium'
                    }), 403
            
            # Get opportunity details
            opportunity = db.opportunities.find_one({"opportunity_id": opportunity_id})
            if not opportunity:
                return jsonify({'error': 'Opportunity not found'}), 404
            
            # Generate application based on service type
            if service_type == 'premium':
                # Premium service: Full application writing with 8,000+ grant patterns
                application_content = generate_premium_application(opportunity, user_id)
                poc_recommendations = generate_poc_contact_strategy(opportunity)
            else:
                # Standard service: AI assistance
                application_content = generate_standard_application(opportunity, user_id)
                poc_recommendations = None
            
            # Create application record
            application_record = {
                "_id": str(ObjectId()),
                "user_id": user_id,
                "opportunity_id": opportunity_id,
                "service_type": service_type,
                "status": "draft",
                "generated_content": application_content,
                "poc_recommendations": poc_recommendations,
                "success_probability": calculate_success_probability(opportunity, user_id),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            db.applications.insert_one(application_record)
            
            # Update usage counter
            db.subscriptions.update_one(
                {"user_id": user_id, "status": {"$in": ["trialing", "active"]}},
                {"$inc": {"applications_used_this_period": 1}}
            )
            
            # Track activity
            db.user_activities.insert_one({
                "_id": str(ObjectId()),
                "user_id": user_id,
                "activity_type": "application_generated",
                "opportunity_id": opportunity_id,
                "metadata": {
                    "service_type": service_type,
                    "success_probability": application_record["success_probability"]
                },
                "timestamp": datetime.utcnow()
            })
            
            return jsonify({
                'success': True,
                'application_id': application_record["_id"],
                'content': application_content,
                'poc_recommendations': poc_recommendations,
                'success_probability': application_record["success_probability"],
                'applications_remaining': app_limits.get('remaining', 0) - 1
            })
            
        except Exception as e:
            logger.error(f"Error generating application: {str(e)}")
            return jsonify({'error': 'Unable to generate application'}), 500
    
    @app.route('/api/subscription/usage', methods=['GET'])
    def get_subscription_usage():
        """Get current subscription usage"""
        try:
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_id = session['user_id']
            subscription = db.subscriptions.find_one({
                "user_id": user_id,
                "status": {"$in": ["trialing", "active"]}
            })
            
            if not subscription:
                return jsonify({'error': 'No active subscription'}), 404
            
            plan_id = subscription.get('plan_id')
            plan_limits = PRICING_PLANS.get(plan_id, {}).get('limits', {})
            
            usage_data = {
                'plan_id': plan_id,
                'plan_name': PRICING_PLANS.get(plan_id, {}).get('name', 'Unknown'),
                'applications_used': subscription.get('applications_used_this_period', 0),
                'applications_limit': plan_limits.get('applications_per_month', 0),
                'competitive_intelligence_level': plan_limits.get('competitive_intelligence', 'none'),
                'has_premium_service': plan_limits.get('full_writing_service', False),
                'period_start': subscription.get('current_period_start'),
                'period_end': subscription.get('current_period_end')
            }
            
            return jsonify({
                'success': True,
                'usage': usage_data
            })
            
        except Exception as e:
            logger.error(f"Error getting subscription usage: {str(e)}")
            return jsonify({'error': 'Unable to fetch usage data'}), 500
    
    def generate_standard_application(opportunity, user_id):
        """Generate standard AI-assisted application"""
        # This would integrate with your existing AI application generator
        # For now, return a placeholder
        return {
            "executive_summary": "AI-generated executive summary based on successful grant patterns...",
            "project_description": "Detailed project description tailored to opportunity requirements...",
            "methodology": "Research methodology following proven frameworks...",
            "budget_justification": "Budget breakdown with justifications...",
            "evaluation_plan": "Comprehensive evaluation and reporting plan..."
        }
    
    def generate_premium_application(opportunity, user_id):
        """Generate premium full application with 8,000+ grant patterns"""
        # This would use the expanded database of 8,000+ successful grants
        standard_content = generate_standard_application(opportunity, user_id)
        
        # Add premium features
        premium_content = {
            **standard_content,
            "competitive_analysis": "Analysis of competing organizations and differentiation strategy...",
            "success_patterns": "Insights from 8,000+ successful grants in this category...",
            "risk_mitigation": "Comprehensive risk assessment and mitigation strategies...",
            "stakeholder_engagement": "Detailed stakeholder engagement and collaboration plan...",
            "sustainability_plan": "Long-term sustainability and impact plan...",
            "appendices": "Supporting documents and detailed appendices..."
        }
        
        return premium_content
    
    def generate_poc_contact_strategy(opportunity):
        """Generate POC contact recommendations"""
        agency = opportunity.get('agency', 'Unknown Agency')
        
        return {
            "recommended_contacts": [
                {
                    "role": "Program Officer",
                    "contact_info": "Available in opportunity details",
                    "best_time_to_call": "Tuesday-Thursday, 10 AM - 2 PM EST",
                    "suggested_questions": [
                        "What specific outcomes are you most interested in seeing from this grant?",
                        "Are there any recent policy changes that might affect application priorities?",
                        "What common mistakes do you see in applications for this opportunity?",
                        "Are there any unstated preferences for collaboration or partnerships?"
                    ]
                }
            ],
            "conversation_script": f"Hi, I'm calling about {opportunity.get('title', 'the grant opportunity')}. I wanted to ensure our application addresses all of your key priorities. Do you have a few minutes to discuss what you're most hoping to achieve with this funding?",
            "follow_up_strategy": "Send a brief email summarizing the conversation within 24 hours, and include any clarifications they requested in your application."
        }
    
    def calculate_success_probability(opportunity, user_id):
        """Calculate success probability based on multiple factors"""
        # This would use your existing probability calculation logic
        # For now, return a sample calculation
        base_probability = 25.0  # Base industry average
        
        # Adjust based on user's historical success rate
        user_awards = len(award_tracker.get_user_awards(user_id))
        user_applications = db.applications.count_documents({"user_id": user_id})
        
        if user_applications > 0:
            user_success_rate = (user_awards / user_applications) * 100
            if user_success_rate > base_probability:
                base_probability += min(10, user_success_rate - base_probability)
        
        # Adjust based on competition level
        competition_level = competitive_intelligence.get_competition_level(
            opportunity.get('opportunity_id')
        )
        
        if competition_level == "high":
            base_probability *= 0.8
        elif competition_level == "low":
            base_probability *= 1.2
        
        return min(95.0, max(5.0, base_probability))  # Cap between 5% and 95%
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if request.method == 'POST':
            # Handle login logic here
            # This would integrate with your existing auth system
            pass
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """User logout"""
        session.clear()
        return redirect(url_for('home'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return render_template('500.html'), 500
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0', port=5001)
    