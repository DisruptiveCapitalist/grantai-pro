#!/usr/bin/env python3
"""
GrantAI Pro - MongoDB Database Setup Script
Creates collections, indexes, and imports initial data
"""

from pymongo import MongoClient
import json
from datetime import datetime, timedelta
import os
from bson import ObjectId

def setup_mongodb():
    """Complete MongoDB setup for GrantAI Pro"""
    
    # Connect to MongoDB
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/grantai')
    client = MongoClient(MONGO_URI)
    db = client.grantai
    
    print("🚀 Setting up GrantAI Pro MongoDB Database")
    print("=" * 50)
    
    # 1. Create Collections and Indexes
    print("📊 Creating collections and indexes...")
    
    try:
        # Users collection
        db.users.create_index([("email", 1)], unique=True)
        print("   ✅ Users collection with email index")
        
        # Subscriptions collection
        db.subscriptions.create_index([("user_id", 1)])
        db.subscriptions.create_index([("stripe_subscription_id", 1)])
        print("   ✅ Subscriptions collection with indexes")
        
        # Opportunities collection
        db.opportunities.create_index([("opportunity_id", 1)], unique=True)
        db.opportunities.create_index([("relevance_score", -1)])
        db.opportunities.create_index([("agency", 1)])
        db.opportunities.create_index([("close_date", 1)])
        print("   ✅ Opportunities collection with indexes")
        
        # Applications collection
        db.applications.create_index([("user_id", 1), ("created_at", -1)])
        db.applications.create_index([("opportunity_id", 1)])
        db.applications.create_index([("status", 1)])
        print("   ✅ Applications collection with indexes")
        
        # Competitive Intelligence collections
        db.application_tracking.create_index([("opportunity_id", 1)])
        db.user_activity.create_index([("opportunity_id", 1)])
        db.user_activity.create_index([("user_id", 1), ("timestamp", -1)])
        db.competitive_insights.create_index([("opportunity_id", 1)])
        print("   ✅ Competitive intelligence collections with indexes")
        
        # Award tracking collections
        db.award_verification.create_index([("application_id", 1)])
        db.user_achievements.create_index([("user_id", 1)])
        db.global_metrics.create_index([("metric_type", 1)])
        print("   ✅ Award tracking collections with indexes")
        
    except Exception as e:
        print(f"   ❌ Error creating indexes: {e}")
        return False
    
    # 2. Insert Sample Opportunities Data
    print("\n📝 Inserting sample opportunities...")
    
    sample_opportunities = [
        {
            'opportunity_id': 'DOD-2024-AI-RESEARCH-001',
            'title': 'Artificial Intelligence Research for Defense Applications',
            'agency': 'Department of Defense',
            'description': 'Research and development of AI technologies for defense applications including machine learning, neural networks, and autonomous systems.',
            'amount_min': 500000,
            'amount_max': 2000000,
            'close_date': datetime.utcnow() + timedelta(days=45),
            'post_date': datetime.utcnow() - timedelta(days=5),
            'source': 'grants.gov',
            'source_url': 'https://www.grants.gov/web/grants/view-opportunity.html?oppId=DOD-2024-AI-RESEARCH-001',
            'relevance_score': 0.85,
            'cfda_numbers': '12.910',
            'category': 'Research and Development',
            'discovered_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'opportunity_id': 'HUD-2024-HOUSING-TECH-002',
            'title': 'Technology Innovation for Affordable Housing Solutions',
            'agency': 'Department of Housing and Urban Development',
            'description': 'Development of innovative technology solutions to improve affordable housing delivery, management, and resident services.',
            'amount_min': 250000,
            'amount_max': 1500000,
            'close_date': datetime.utcnow() + timedelta(days=30),
            'post_date': datetime.utcnow() - timedelta(days=3),
            'source': 'grants.gov',
            'source_url': 'https://www.grants.gov/web/grants/view-opportunity.html?oppId=HUD-2024-HOUSING-TECH-002',
            'relevance_score': 0.78,
            'cfda_numbers': '14.195',
            'category': 'Housing Technology',
            'discovered_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'opportunity_id': 'NSF-2024-COMP-SCI-003',
            'title': 'Computer Science Innovation for Social Impact',
            'agency': 'National Science Foundation',
            'description': 'Research in computer science and information technology with applications for social good and community impact.',
            'amount_min': 100000,
            'amount_max': 800000,
            'close_date': datetime.utcnow() + timedelta(days=60),
            'post_date': datetime.utcnow() - timedelta(days=7),
            'source': 'grants.gov',
            'source_url': 'https://www.grants.gov/web/grants/view-opportunity.html?oppId=NSF-2024-COMP-SCI-003',
            'relevance_score': 0.72,
            'cfda_numbers': '47.070',
            'category': 'Computer Science Research',
            'discovered_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'opportunity_id': 'DARPA-2024-INNOVATION-004',
            'title': 'Breakthrough Technologies for National Security',
            'agency': 'Defense Advanced Research Projects Agency',
            'description': 'Development of revolutionary technologies that provide significant advantages for national security applications.',
            'amount_min': 1000000,
            'amount_max': 5000000,
            'close_date': datetime.utcnow() + timedelta(days=90),
            'post_date': datetime.utcnow() - timedelta(days=10),
            'source': 'sam.gov',
            'source_url': 'https://sam.gov/opp/DARPA-2024-INNOVATION-004',
            'relevance_score': 0.92,
            'cfda_numbers': '12.910',
            'category': 'Advanced Research',
            'discovered_at': datetime.utcnow(),
            'is_active': True
        },
        {
            'opportunity_id': 'NIH-2024-DIGITAL-HEALTH-005',
            'title': 'Digital Health Technologies for Underserved Communities',
            'agency': 'National Institutes of Health',
            'description': 'Development of digital health solutions to improve healthcare access and outcomes in underserved communities.',
            'amount_min': 300000,
            'amount_max': 1200000,
            'close_date': datetime.utcnow() + timedelta(days=75),
            'post_date': datetime.utcnow() - timedelta(days=2),
            'source': 'grants.gov',
            'source_url': 'https://www.grants.gov/web/grants/view-opportunity.html?oppId=NIH-2024-DIGITAL-HEALTH-005',
            'relevance_score': 0.65,
            'cfda_numbers': '93.310',
            'category': 'Digital Health',
            'discovered_at': datetime.utcnow(),
            'is_active': True
        }
    ]
    
    try:
        # Clear existing opportunities for clean start
        db.opportunities.delete_many({})
        
        # Insert sample opportunities
        result = db.opportunities.insert_many(sample_opportunities)
        print(f"   ✅ Inserted {len(result.inserted_ids)} sample opportunities")
        
    except Exception as e:
        print(f"   ❌ Error inserting opportunities: {e}")
        return False
    
    # 3. Create Test User Account
    print("\n👤 Creating test user account...")
    
    try:
        from werkzeug.security import generate_password_hash
        
        # Clear existing test users
        db.users.delete_many({'email': 'test@grantai.pro'})
        db.subscriptions.delete_many({'user_id': {'$exists': True}})
        
        # Create test user
        test_user = {
            'email': 'test@grantai.pro',
            'password_hash': generate_password_hash('password123'),
            'first_name': 'Test',
            'last_name': 'User',
            'organization_name': 'GrantAI Test Organization',
            'role': 'admin',
            'created_at': datetime.utcnow(),
            'is_active': True,
            'stripe_customer_id': None
        }
        
        user_id = db.users.insert_one(test_user).inserted_id
        
        # Create subscription for test user
        test_subscription = {
            'user_id': str(user_id),
            'plan_type': 'professional',
            'status': 'trial',
            'stripe_subscription_id': None,
            'trial_end': datetime.utcnow() + timedelta(days=14),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'applications_used_this_month': 0,
            'profiles_used': 0
        }
        
        db.subscriptions.insert_one(test_subscription)
        
        print("   ✅ Test user created:")
        print("      Email: test@grantai.pro")
        print("      Password: password123")
        print("      Plan: Professional (14-day trial)")
        
    except Exception as e:
        print(f"   ❌ Error creating test user: {e}")
        return False
    
    # 4. Initialize Global Metrics
    print("\n📊 Initializing global metrics...")
    
    try:
        global_metrics = {
            'metric_type': 'global_stats',
            'total_awards_won': 0,
            'total_applications_filed': 0,
            'total_users_active': 1,  # Test user
            'total_organizations': 1,
            'total_time_saved_hours': 0,
            'success_rate': 0.0,
            'average_award_amount': 0,
            'largest_single_award': 0,
            'total_opportunities_discovered': len(sample_opportunities),
            'ai_applications_generated': 0,
            'last_updated': datetime.utcnow(),
            'last_calculation': datetime.utcnow()
        }
        
        db.global_metrics.insert_one(global_metrics)
        print("   ✅ Global metrics initialized")
        
    except Exception as e:
        print(f"   ❌ Error initializing metrics: {e}")
        return False
    
    # 5. Verify Setup
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
    
    print("\n🎉 MongoDB setup completed successfully!")
    print("\n📋 Next Steps:")
    print("   1. Set environment variables (see .env.example)")
    print("   2. Run: python app.py")
    print("   3. Visit: http://localhost:5000")
    print("   4. Login with test@grantai.pro / password123")
    
    return True

def import_existing_grants():
    """Import your existing 876 grants data"""
    
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/grantai')
    client = MongoClient(MONGO_URI)
    db = client.grantai
    
    print("\n📥 Importing existing grants data...")
    
    # Look for existing grants file
    grants_files = [
        'enhanced_collected_awards.json',
        'collected_grants.json',
        'grants_data.json',
        'successful_grants.json'
    ]
    
    grants_data = None
    for filename in grants_files:
        if os.path.exists(filename):
            print(f"   Found grants file: {filename}")
            try:
                with open(filename, 'r') as f:
                    grants_data = json.load(f)
                break
            except Exception as e:
                print(f"   Error reading {filename}: {e}")
                continue
    
    if not grants_data:
        print("   ⚠️  No existing grants file found. Using sample data only.")
        return True
    
    # Process and import grants
    try:
        processed_grants = []
        
        for i, grant in enumerate(grants_data[:100]):  # Import first 100 for testing
            if isinstance(grant, dict):
                processed_grant = {
                    'opportunity_id': grant.get('award_id', f'EXISTING-{i}'),
                    'title': grant.get('award_title', grant.get('title', 'Imported Grant')),
                    'agency': grant.get('agency_name', grant.get('agency', 'Unknown Agency')),
                    'description': grant.get('award_description', grant.get('description', ''))[:1000],
                    'amount_max': grant.get('total_obligated_amount', grant.get('amount', 0)),
                    'amount_min': grant.get('total_obligated_amount', grant.get('amount', 0)) // 2 if grant.get('total_obligated_amount') else 0,
                    'close_date': datetime.utcnow() + timedelta(days=30),  # Default future date
                    'post_date': datetime.utcnow() - timedelta(days=365),  # Default past date
                    'source': 'existing_database',
                    'source_url': grant.get('url', ''),
                    'relevance_score': grant.get('persc_relevance_score', 0.5),
                    'cfda_numbers': grant.get('cfda_number', ''),
                    'category': grant.get('category', 'Imported'),
                    'discovered_at': datetime.utcnow(),
                    'is_active': False  # Mark as historical data
                }
                processed_grants.append(processed_grant)
        
        if processed_grants:
            # Insert grants (skip duplicates)
            inserted_count = 0
            for grant in processed_grants:
                try:
                    db.opportunities.insert_one(grant)
                    inserted_count += 1
                except Exception:
                    # Skip duplicates
                    pass
            
            print(f"   ✅ Imported {inserted_count} historical grants from existing data")
        
    except Exception as e:
        print(f"   ❌ Error importing grants: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Run the setup
    if setup_mongodb():
        # Try to import existing grants
        import_existing_grants()
        
        print("\n" + "=" * 50)
        print("🚀 GrantAI Pro Database Setup Complete!")
        print("   Ready to start development...")
    else:
        print("\n❌ Setup failed. Please check your MongoDB connection.")
