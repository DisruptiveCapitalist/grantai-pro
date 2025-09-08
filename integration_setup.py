#!/usr/bin/env python3
"""
GrantAI Pro - Phase 2 Week 4 Integration Setup
Connects competitive intelligence with main app and adds sample data
"""

import os
import sys
import json
from datetime import datetime, timedelta
import random
from pymongo import MongoClient

# Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://sam_db_user:your_password@cluster0.s7k3hey.mongodb.net/grantai')

def connect_to_database():
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(MONGO_URI)
        db = client.grantai
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful")
        return client, db
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None, None

def setup_collections(db):
    """Setup and index collections for optimal performance"""
    print("🏗️ Setting up collections and indexes...")
    
    # Create indexes for competitive intelligence
    collections_indexes = {
        'user_activity': [
            ('user_id', 1),
            ('opportunity_id', 1),
            ('timestamp', -1),
            ('activity_type', 1)
        ],
        'competitive_insights': [
            ('opportunity_id', 1),
            ('updated_at', -1),
            ('competition_level', 1)
        ],
        'opportunities': [
            ('opportunity_id', 1),
            ('agency', 1),
            ('close_date', 1),
            ('amount_max', -1),
            ('is_active', 1)
        ],
        'users': [
            ('email', 1),
            ('subscription_tier', 1),
            ('created_at', -1)
        ]
    }
    
    for collection_name, indexes in collections_indexes.items():
        collection = db[collection_name]
        for index in indexes:
            try:
                collection.create_index(index)
                print(f"  ✅ Created index on {collection_name}.{index[0]}")
            except Exception as e:
                print(f"  ⚠️ Index {collection_name}.{index[0]} may already exist")

def add_sample_opportunities(db):
    """Add sample opportunities with competitive data"""
    print("📊 Adding sample opportunities with competitive intelligence...")
    
    # Sample opportunities based on your test data
    sample_opportunities = [
        {
            'opportunity_id': 'DOD-2026-DARPA-CROSS-DOMAIN',
            'title': 'DARPA Cross-Domain AI Integration',
            'agency': 'Department of Defense',
            'description': 'Advanced AI/ML integration across defense domains with cross-agency coordination capabilities.',
            'amount_min': 1000000,
            'amount_max': 8500000,
            'close_date': datetime.now() + timedelta(days=49),
            'post_date': datetime.now() - timedelta(days=30),
            'source': 'grants.gov',
            'is_active': True,
            'cfda_numbers': '12.910',
            'category': 'Defense Technology',
            'discovery_date': datetime.now() - timedelta(days=25)
        },
        {
            'opportunity_id': 'HHS-2026-CCSQ-AI-PLATFORM',
            'title': 'HHS AI/ML Human Services Platform',
            'agency': 'Department of Health and Human Services',
            'description': 'AI-powered platform for cross-agency human services coordination and resource optimization.',
            'amount_min': 500000,
            'amount_max': 4500000,
            'close_date': datetime.now() + timedelta(days=35),
            'post_date': datetime.now() - timedelta(days=20),
            'source': 'grants.gov',
            'is_active': True,
            'cfda_numbers': '93.600',
            'category': 'Health Technology',
            'discovery_date': datetime.now() - timedelta(days=15)
        },
        {
            'opportunity_id': 'NASA-2026-SBIR-FEDERATED-AI',
            'title': 'NASA Federated AI Multi-Agency',
            'agency': 'National Aeronautics and Space Administration',
            'description': 'Federated learning system for multi-agency space exploration data sharing and analysis.',
            'amount_min': 250000,
            'amount_max': 1750000,
            'close_date': datetime.now() + timedelta(days=42),
            'post_date': datetime.now() - timedelta(days=35),
            'source': 'sbir.gov',
            'is_active': True,
            'cfda_numbers': '43.001',
            'category': 'Space Technology',
            'discovery_date': datetime.now() - timedelta(days=30)
        },
        {
            'opportunity_id': 'HUD-2026-PIH-AI-HOUSING',
            'title': 'HUD AI Housing Cross-Agency Integration',
            'agency': 'Department of Housing and Urban Development',
            'description': 'AI-driven housing assistance program with cross-agency service integration and automated eligibility.',
            'amount_min': 300000,
            'amount_max': 3200000,
            'close_date': datetime.now() + timedelta(days=33),
            'post_date': datetime.now() - timedelta(days=45),
            'source': 'grants.gov',
            'is_active': True,
            'cfda_numbers': '14.850',
            'category': 'Housing Technology',
            'discovery_date': datetime.now() - timedelta(days=40)
        },
        {
            'opportunity_id': 'DOE-2026-EERE-SMART-GRID',
            'title': 'DOE Smart Grid AI Integration',
            'agency': 'Department of Energy',
            'description': 'Machine learning for smart grid optimization and renewable energy integration.',
            'amount_min': 750000,
            'amount_max': 5000000,
            'close_date': datetime.now() + timedelta(days=60),
            'post_date': datetime.now() - timedelta(days=10),
            'source': 'energy.gov',
            'is_active': True,
            'cfda_numbers': '81.087',
            'category': 'Energy Technology',
            'discovery_date': datetime.now() - timedelta(days=5)
        }
    ]
    
    # Insert opportunities
    opportunities_collection = db.opportunities
    for opp in sample_opportunities:
        try:
            opportunities_collection.update_one(
                {'opportunity_id': opp['opportunity_id']},
                {'$set': opp},
                upsert=True
            )
            print(f"  ✅ Added/Updated: {opp['title']}")
        except Exception as e:
            print(f"  ❌ Error adding {opp['title']}: {e}")

def add_competitive_intelligence_data(db):
    """Add competitive intelligence data for sample opportunities"""
    print("🔥 Adding competitive intelligence data...")
    
    competitive_data = [
        {
            'opportunity_id': 'DOD-2026-DARPA-CROSS-DOMAIN',
            'competition_level': 'high',
            'total_users_interested': 145,
            'total_users_started': 89,
            'total_users_submitted': 23,
            'estimated_success_rate': 0.08,
            'daily_new_applicants': 12,
            'weekly_trend': 'increasing',
            'similar_opportunities_avg_applicants': 67,
            'updated_at': datetime.now()
        },
        {
            'opportunity_id': 'HHS-2026-CCSQ-AI-PLATFORM',
            'competition_level': 'medium',
            'total_users_interested': 78,
            'total_users_started': 45,
            'total_users_submitted': 12,
            'estimated_success_rate': 0.15,
            'daily_new_applicants': 6,
            'weekly_trend': 'stable',
            'similar_opportunities_avg_applicants': 52,
            'updated_at': datetime.now()
        },
        {
            'opportunity_id': 'NASA-2026-SBIR-FEDERATED-AI',
            'competition_level': 'medium',
            'total_users_interested': 92,
            'total_users_started': 54,
            'total_users_submitted': 18,
            'estimated_success_rate': 0.12,
            'daily_new_applicants': 8,
            'weekly_trend': 'increasing',
            'similar_opportunities_avg_applicants': 43,
            'updated_at': datetime.now()
        },
        {
            'opportunity_id': 'HUD-2026-PIH-AI-HOUSING',
            'competition_level': 'low',
            'total_users_interested': 34,
            'total_users_started': 22,
            'total_users_submitted': 8,
            'estimated_success_rate': 0.24,
            'daily_new_applicants': 3,
            'weekly_trend': 'stable',
            'similar_opportunities_avg_applicants': 28,
            'updated_at': datetime.now()
        },
        {
            'opportunity_id': 'DOE-2026-EERE-SMART-GRID',
            'competition_level': 'low',
            'total_users_interested': 41,
            'total_users_started': 28,
            'total_users_submitted': 9,
            'estimated_success_rate': 0.22,
            'daily_new_applicants': 4,
            'weekly_trend': 'increasing',
            'similar_opportunities_avg_applicants': 31,
            'updated_at': datetime.now()
        }
    ]
    
    # Insert competitive insights
    competitive_insights_collection = db.competitive_insights
    for data in competitive_data:
        try:
            competitive_insights_collection.update_one(
                {'opportunity_id': data['opportunity_id']},
                {'$set': data},
                upsert=True
            )
            print(f"  ✅ Added competitive data for: {data['opportunity_id']} ({data['competition_level']} competition)")
        except Exception as e:
            print(f"  ❌ Error adding competitive data: {e}")

def add_sample_user_activity(db):
    """Add sample user activity data for testing"""
    print("👥 Adding sample user activity data...")
    
    # Sample user IDs (you can replace with real ones)
    sample_user_ids = ['user_001', 'user_002', 'user_003', 'user_004', 'user_005']
    opportunity_ids = [
        'DOD-2026-DARPA-CROSS-DOMAIN',
        'HHS-2026-CCSQ-AI-PLATFORM', 
        'NASA-2026-SBIR-FEDERATED-AI',
        'HUD-2026-PIH-AI-HOUSING',
        'DOE-2026-EERE-SMART-GRID'
    ]
    
    activity_types = ['viewed_opportunity', 'viewed_in_list', 'started_application', 'saved_opportunity']
    organization_types = ['startup', 'nonprofit', 'university', 'corporation']
    organization_sizes = ['small', 'medium', 'large']
    
    user_activity_collection = db.user_activity
    
    # Generate realistic activity data
    activities = []
    for i in range(200):  # 200 sample activities
        activity = {
            'user_id': random.choice(sample_user_ids),
            'opportunity_id': random.choice(opportunity_ids),
            'activity_type': random.choice(activity_types),
            'timestamp': datetime.now() - timedelta(days=random.randint(1, 30)),
            'organization_type': random.choice(organization_types),
            'organization_size': random.choice(organization_sizes),
            'success_probability': random.uniform(0.1, 0.9)
        }
        activities.append(activity)
    
    try:
        user_activity_collection.insert_many(activities)
        print(f"  ✅ Added {len(activities)} sample user activities")
    except Exception as e:
        print(f"  ❌ Error adding user activities: {e}")

def setup_global_metrics(db):
    """Setup global metrics for public dashboard"""
    print("📈 Setting up global metrics...")
    
    global_metrics = {
        'metric_type': 'global_stats',
        'total_awards_won': 142,
        'total_applications_filed': 876,
        'total_users_active': 1250,
        'total_organizations': 450,
        'total_time_saved_hours': 15680,
        'success_rate': 16.2,
        'average_award_amount': 485000,
        'largest_single_award': 8500000,
        'total_opportunities_discovered': 2847,
        'ai_applications_generated': 1456,
        'total_award_value': 68900000,
        'last_updated': datetime.now(),
        'last_calculation': datetime.now()
    }
    
    try:
        db.global_metrics.update_one(
            {'metric_type': 'global_stats'},
            {'$set': global_metrics},
            upsert=True
        )
        print("  ✅ Global metrics initialized")
    except Exception as e:
        print(f"  ❌ Error setting up global metrics: {e}")

def create_sample_user(db):
    """Create a sample user for testing"""
    print("👤 Creating sample test user...")
    
    from werkzeug.security import generate_password_hash
    
    sample_user = {
        'email': 'test@grantai.pro',
        'password_hash': generate_password_hash('password123'),
        'first_name': 'Test',
        'last_name': 'User',
        'organization': 'GrantAI Pro Demo',
        'subscription_tier': 'professional',
        'created_at': datetime.now(),
        'is_active': True,
        'last_login': datetime.now()
    }
    
    try:
        result = db.users.update_one(
            {'email': sample_user['email']},
            {'$set': sample_user},
            upsert=True
        )
        print("  ✅ Sample user created (email: test@grantai.pro, password: password123)")
        return str(result.upserted_id) if result.upserted_id else "existing_user"
    except Exception as e:
        print(f"  ❌ Error creating sample user: {e}")
        return None

def verify_integration(db):
    """Verify that the integration is working correctly"""
    print("🔍 Verifying integration...")
    
    # Check collections exist and have data
    collections_to_check = [
        'opportunities',
        'competitive_insights', 
        'user_activity',
        'global_metrics',
        'users'
    ]
    
    for collection_name in collections_to_check:
        try:
            count = db[collection_name].count_documents({})
            print(f"  ✅ {collection_name}: {count} documents")
        except Exception as e:
            print(f"  ❌ Error checking {collection_name}: {e}")
    
    # Test competitive intelligence queries
    print("\n🧪 Testing competitive intelligence queries...")
    
    try:
        # Test competition level calculation
        high_competition = db.competitive_insights.count_documents({'competition_level': 'high'})
        medium_competition = db.competitive_insights.count_documents({'competition_level': 'medium'})
        low_competition = db.competitive_insights.count_documents({'competition_level': 'low'})
        
        print(f"  📊 Competition levels: High={high_competition}, Medium={medium_competition}, Low={low_competition}")
        
        # Test opportunity with competition data join
        pipeline = [
            {
                '$lookup': {
                    'from': 'competitive_insights',
                    'localField': 'opportunity_id',
                    'foreignField': 'opportunity_id',
                    'as': 'competition_data'
                }
            },
            {'$limit': 1}
        ]
        
        sample_with_competition = list(db.opportunities.aggregate(pipeline))
        if sample_with_competition:
            print("  ✅ Opportunity-Competition data join working")
        else:
            print("  ⚠️ No opportunities with competition data found")
            
    except Exception as e:
        print(f"  ❌ Error testing competitive queries: {e}")

def create_directory_structure():
    """Create necessary directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'services',
        'api',
        'utils'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"  ✅ Created directory: {directory}")
        except Exception as e:
            print(f"  ❌ Error creating {directory}: {e}")

def create_env_template():
    """Create .env template file"""
    print("⚙️ Creating .env template...")
    
    env_template = """# GrantAI Pro Environment Variables
# MongoDB Atlas Connection
MONGO_URI=mongodb+srv://sam_db_user:your_password@cluster0.s7k3hey.mongodb.net/grantai

# Flask Configuration
SECRET_KEY=grantai-pro-secret-key-2025
FLASK_ENV=development

# API Keys (optional)
GRANTS_GOV_API_KEY=your_grants_gov_api_key
SAM_GOV_API_KEY=your_sam_gov_api_key

# Stripe (for future billing integration)
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key

# External Services (optional)
OPENAI_API_KEY=your_openai_api_key
"""
    
    try:
        if not os.path.exists('.env'):
            with open('.env.example', 'w') as f:
                f.write(env_template)
            print("  ✅ Created .env.example template")
        else:
            print("  ℹ️ .env file already exists")
    except Exception as e:
        print(f"  ❌ Error creating .env template: {e}")

def main():
    """Main setup function"""
    print("🚀 GrantAI Pro - Phase 2 Week 4 Integration Setup")
    print("=" * 60)
    
    # Check environment
    if not MONGO_URI or 'your_password' in MONGO_URI:
        print("❌ Please set MONGO_URI environment variable with your actual MongoDB Atlas connection string")
        print("💡 Example: export MONGO_URI='mongodb+srv://user:password@cluster.mongodb.net/grantai'")
        return
    
    # Connect to database
    client, db = connect_to_database()
    if db is None:
        return
    
    try:
        # Setup everything
        create_directory_structure()
        setup_collections(db)
        add_sample_opportunities(db)
        add_competitive_intelligence_data(db)
        add_sample_user_activity(db)
        setup_global_metrics(db)
        sample_user_id = create_sample_user(db)
        create_env_template()
        
        print("\n" + "=" * 60)
        verify_integration(db)
        
        print("\n🎉 Integration setup complete!")
        print("\n📋 Next steps:")
        print("1. Save your templates to the templates/ directory")
        print("2. Run your main Flask app: python app.py")
        print("3. Visit http://localhost:5001 to see the integrated app")
        print("4. Login with: test@grantai.pro / password123")
        print("5. Check the competitive intelligence dashboard")
        
        print("\n🔧 File structure:")
        print("├── app.py (your main Flask app)")
        print("├── templates/ (HTML templates)")
        print("├── services/competitive_intelligence.py (existing)")
        print("├── api/competitive.py (existing)")
        print("└── .env.example (environment template)")
        
        print("\n✨ Features now available:")
        print("• 🏆 Competition badges on all opportunities")
        print("• 📊 Real-time competitive intelligence")
        print("• 🎯 User activity tracking")
        print("• 📈 Competitive dashboard")
        print("• 🔥 Trending opportunities")
        print("• 💡 Success rate predictions")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    main()
    