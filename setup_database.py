#!/usr/bin/env python3
"""
GrantAI Pro - Database Setup Script
Initializes MongoDB Atlas with required collections and sample data
"""

import os
import json
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, TEXT
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Initialize MongoDB Atlas database with required collections and data"""
    
    print("\n🚀 Setting up GrantAI Pro Database...")
    print("=" * 50)
    
    # Connect to MongoDB Atlas
    MONGO_URI = os.environ.get('MONGO_URI')
    if not MONGO_URI:
        print("❌ Error: MONGO_URI not found in environment variables")
        print("Please check your .env file contains the MongoDB Atlas connection string")
        return False
    
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully")
        
        db = client.grantai
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return False
    
    # Drop existing collections (fresh start)
    print("\n🗑️  Dropping existing collections...")
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"   Dropped: {collection_name}")
    
    print("\n📦 Creating collections with indexes...")
    
    # 1. USERS COLLECTION
    users = db.users
    users.create_index("email", unique=True)
    users.create_index("created_at")
    users.create_index("subscription_tier")
    print("   ✅ users collection created")
    
    # 2. OPPORTUNITIES COLLECTION
    opportunities = db.opportunities
    opportunities.create_index([("title", TEXT), ("description", TEXT)])
    opportunities.create_index("category")
    opportunities.create_index("posted_date")
    opportunities.create_index("deadline")
    opportunities.create_index("funding_amount")
    print("   ✅ opportunities collection created")
    
    # 3. APPLICATIONS COLLECTION
    applications = db.applications
    applications.create_index("user_id")
    applications.create_index("opportunity_id")
    applications.create_index("status")
    applications.create_index("created_at")
    print("   ✅ applications collection created")
    
    # 4. SUBSCRIPTIONS COLLECTION
    subscriptions = db.subscriptions
    subscriptions.create_index("user_id")
    subscriptions.create_index("stripe_subscription_id")
    subscriptions.create_index("status")
    print("   ✅ subscriptions collection created")
    
    # 5. APPLICATION TRACKING COLLECTION
    application_tracking = db.application_tracking
    application_tracking.create_index("opportunity_id")
    application_tracking.create_index("updated_at")
    print("   ✅ application_tracking collection created")
    
    # 6. USER ACTIVITY COLLECTION
    user_activity = db.user_activity
    user_activity.create_index("user_id")
    user_activity.create_index("activity_date")
    user_activity.create_index("activity_type")
    print("   ✅ user_activity collection created")
    
    # 7. COMPETITIVE INSIGHTS COLLECTION
    competitive_insights = db.competitive_insights
    competitive_insights.create_index("opportunity_id")
    competitive_insights.create_index("calculated_at")
    print("   ✅ competitive_insights collection created")
    
    # 8. AWARD VERIFICATION COLLECTION
    award_verification = db.award_verification
    award_verification.create_index("user_id")
    award_verification.create_index("award_number")
    award_verification.create_index("verified_at")
    print("   ✅ award_verification collection created")
    
    # 9. USER ACHIEVEMENTS COLLECTION
    user_achievements = db.user_achievements
    user_achievements.create_index("user_id")
    user_achievements.create_index("achievement_type")
    user_achievements.create_index("earned_at")
    print("   ✅ user_achievements collection created")
    
    # 10. GLOBAL METRICS COLLECTION
    global_metrics = db.global_metrics
    global_metrics.create_index("metric_date")
    global_metrics.create_index("metric_type")
    print("   ✅ global_metrics collection created")
    
    print("\n👤 Creating sample users...")
    
    # Create test users
    sample_users = [
        {
            'email': 'test@grantai.pro',
            'password_hash': generate_password_hash('password123'),
            'first_name': 'Test',
            'last_name': 'User',
            'subscription_tier': 'premium',
            'created_at': datetime.utcnow() - timedelta(days=30),
            'last_login': datetime.utcnow() - timedelta(hours=2),
            'is_active': True,
            'profile': {
                'organization': 'GrantAI Pro',
                'role': 'Test Account',
                'experience_level': 'expert'
            },
            'usage_stats': {
                'applications_generated': 25,
                'opportunities_viewed': 150,
                'last_activity': datetime.utcnow()
            }
        },
        {
            'email': 'demo@grantai.pro',
            'password_hash': generate_password_hash('demo123'),
            'first_name': 'Demo',
            'last_name': 'Account',
            'subscription_tier': 'free',
            'created_at': datetime.utcnow() - timedelta(days=7),
            'last_login': datetime.utcnow() - timedelta(hours=6),
            'is_active': True,
            'profile': {
                'organization': 'Demo Organization',
                'role': 'Grant Writer',
                'experience_level': 'beginner'
            },
            'usage_stats': {
                'applications_generated': 3,
                'opportunities_viewed': 45,
                'last_activity': datetime.utcnow() - timedelta(hours=6)
            }
        }
    ]
    
    users.insert_many(sample_users)
    print(f"   ✅ {len(sample_users)} sample users created")
    
    print("\n💰 Creating sample grant opportunities...")
    
    # Create sample opportunities
    sample_opportunities = [
        {
            'title': 'NSF Research Grant for AI Innovation',
            'agency': 'National Science Foundation',
            'opportunity_number': 'NSF-24-001',
            'category': 'Research & Development',
            'description': 'Supporting innovative artificial intelligence research projects that advance the field and create practical applications for society.',
            'funding_amount': 500000,
            'deadline': datetime.utcnow() + timedelta(days=45),
            'posted_date': datetime.utcnow() - timedelta(days=10),
            'eligibility': ['Universities', 'Research Institutions'],
            'status': 'open',
            'competition_level': 'high',
            'estimated_applicants': 250,
            'historical_success_rate': 15.2,
            'tags': ['AI', 'Machine Learning', 'Research', 'Innovation']
        },
        {
            'title': 'Small Business Innovation Research (SBIR)',
            'agency': 'Department of Defense',
            'opportunity_number': 'DOD-SBIR-24-A',
            'category': 'Small Business',
            'description': 'Phase I funding for small businesses developing innovative technologies for defense applications.',
            'funding_amount': 275000,
            'deadline': datetime.utcnow() + timedelta(days=60),
            'posted_date': datetime.utcnow() - timedelta(days=5),
            'eligibility': ['Small Businesses'],
            'status': 'open',
            'competition_level': 'medium',
            'estimated_applicants': 180,
            'historical_success_rate': 22.8,
            'tags': ['SBIR', 'Defense', 'Innovation', 'Technology']
        },
        {
            'title': 'Community Development Block Grant',
            'agency': 'Department of Housing and Urban Development',
            'opportunity_number': 'HUD-CDBG-24-01',
            'category': 'Community Development',
            'description': 'Annual grants to entitled communities for community development activities.',
            'funding_amount': 1200000,
            'deadline': datetime.utcnow() + timedelta(days=30),
            'posted_date': datetime.utcnow() - timedelta(days=15),
            'eligibility': ['State Governments', 'Local Governments'],
            'status': 'open',
            'competition_level': 'low',
            'estimated_applicants': 75,
            'historical_success_rate': 45.5,
            'tags': ['Community', 'Housing', 'Development', 'Local Government']
        },
        {
            'title': 'NIH Health Innovation Challenge',
            'agency': 'National Institutes of Health',
            'opportunity_number': 'NIH-24-002',
            'category': 'Healthcare',
            'description': 'Supporting breakthrough innovations in health technology and medical research.',
            'funding_amount': 750000,
            'deadline': datetime.utcnow() + timedelta(days=90),
            'posted_date': datetime.utcnow() - timedelta(days=3),
            'eligibility': ['Universities', 'Research Institutions', 'Healthcare Organizations'],
            'status': 'open',
            'competition_level': 'high',
            'estimated_applicants': 320,
            'historical_success_rate': 12.4,
            'tags': ['Healthcare', 'Medical Research', 'Innovation', 'Technology']
        },
        {
            'title': 'Environmental Protection Agency Clean Air Grant',
            'agency': 'Environmental Protection Agency',
            'opportunity_number': 'EPA-CAG-24-01',
            'category': 'Environment',
            'description': 'Funding for projects that improve air quality and reduce environmental pollution.',
            'funding_amount': 350000,
            'deadline': datetime.utcnow() + timedelta(days=75),
            'posted_date': datetime.utcnow() - timedelta(days=8),
            'eligibility': ['Nonprofits', 'Universities', 'State Governments'],
            'status': 'open',
            'competition_level': 'medium',
            'estimated_applicants': 140,
            'historical_success_rate': 28.6,
            'tags': ['Environment', 'Clean Air', 'Pollution', 'Sustainability']
        }
    ]
    
    opportunities.insert_many(sample_opportunities)
    print(f"   ✅ {len(sample_opportunities)} sample opportunities created")
    
    print("\n📝 Creating sample applications...")
    
    # Get user IDs for applications
    test_user = users.find_one({'email': 'test@grantai.pro'})
    demo_user = users.find_one({'email': 'demo@grantai.pro'})
    nsf_opportunity = opportunities.find_one({'opportunity_number': 'NSF-24-001'})
    
    sample_applications = [
        {
            'user_id': str(test_user['_id']),
            'opportunity_id': str(nsf_opportunity['_id']),
            'opportunity_title': nsf_opportunity['title'],
            'status': 'submitted',
            'submitted_at': datetime.utcnow() - timedelta(days=5),
            'created_at': datetime.utcnow() - timedelta(days=7),
            'application_data': {
                'project_title': 'Advanced Neural Networks for Medical Diagnosis',
                'requested_amount': 475000,
                'project_duration': 36,
                'ai_generated': True,
                'confidence_score': 0.87
            },
            'tracking': {
                'last_updated': datetime.utcnow() - timedelta(days=2),
                'status_history': [
                    {'status': 'draft', 'timestamp': datetime.utcnow() - timedelta(days=7)},
                    {'status': 'submitted', 'timestamp': datetime.utcnow() - timedelta(days=5)}
                ]
            }
        }
    ]
    
    applications.insert_many(sample_applications)
    print(f"   ✅ {len(sample_applications)} sample applications created")
    
    print("\n📊 Creating global metrics...")
    
    # Create global metrics
    global_metrics_data = [
        {
            'metric_type': 'daily_stats',
            'metric_date': datetime.utcnow().date(),
            'data': {
                'total_users': 2,
                'total_applications': 1,
                'total_opportunities': 5,
                'total_funding_tracked': 3375000,
                'total_awards': 0,
                'success_rate': 0.0
            },
            'calculated_at': datetime.utcnow()
        }
    ]
    
    global_metrics.insert_many(global_metrics_data)
    print(f"   ✅ Global metrics initialized")
    
    print("\n🔍 Verifying database setup...")
    
    try:
        collections_created = db.list_collection_names()
        expected_collections = [
            'users', 'subscriptions', 'opportunities', 'applications',
            'application_tracking', 'user_activity', 'competitive_insights',
            'award_verification', 'user_achievements', 'global_metrics'
        ]
        
        print(f"   📁 Collections created: {len(collections_created)}")
        for collection in collections_created:
            count = db[collection].count_documents({})
            print(f"      {collection}: {count} documents")
        
        # Test database connection
        db.command('ping')
        print("   ✅ Database connection verified")
        
    except Exception as e:
        print(f"   ❌ Error verifying setup: {e}")
        return False
    
    print("\n🎉 MongoDB Atlas setup completed successfully!")
    print("\n📋 Next Steps:")
    print("   1. Verify your .env file has the correct MONGO_URI")
    print("   2. Run: python app.py")
    print("   3. Visit: http://localhost:5000")
    print("   4. Test login with:")
    print("      Email: test@grantai.pro")
    print("      Password: password123")
    print("   5. Or register a new account")
    
    return True

if __name__ == '__main__':
    setup_database()
