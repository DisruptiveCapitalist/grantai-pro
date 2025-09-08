# utils/database.py
"""
Database initialization and setup for GrantAI Pro award tracking
Creates collections, indexes, and sample data
"""

from datetime import datetime, timedelta
from bson import ObjectId
import logging
import random

logger = logging.getLogger(__name__)

def init_database(db):
    """
    Initialize database collections and indexes for award tracking
    """
    try:
        # Create indexes for performance
        create_indexes(db)
        
        # Insert sample data if collections are empty
        if db.awards.count_documents({}) == 0:
            insert_sample_awards(db)
            logger.info("Sample award data inserted")
        
        # Ensure admin user exists
        ensure_admin_user(db)
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def create_indexes(db):
    """
    Create database indexes for optimal performance
    """
    try:
        # Awards collection indexes
        db.awards.create_index([("user_id", 1)])
        db.awards.create_index([("opportunity_id", 1)])
        db.awards.create_index([("verification_status", 1)])
        db.awards.create_index([("award_date", -1)])
        db.awards.create_index([("reported_date", -1)])
        db.awards.create_index([("is_public", 1), ("verification_status", 1)])
        db.awards.create_index([("award_amount", -1)])
        
        # Applications collection indexes
        db.applications.create_index([("user_id", 1)])
        db.applications.create_index([("opportunity_id", 1)])
        db.applications.create_index([("status", 1)])
        db.applications.create_index([("created_at", -1)])
        
        # Opportunities collection indexes
        db.opportunities.create_index([("opportunity_id", 1)], unique=True)
        db.opportunities.create_index([("is_active", 1)])
        db.opportunities.create_index([("close_date", 1)])
        db.opportunities.create_index([("post_date", -1)])
        db.opportunities.create_index([("agency", 1)])
        db.opportunities.create_index([("category", 1)])
        
        # User activities collection indexes
        db.user_activities.create_index([("user_id", 1)])
        db.user_activities.create_index([("activity_type", 1)])
        db.user_activities.create_index([("timestamp", -1)])
        db.user_activities.create_index([("opportunity_id", 1)])
        
        # Users collection indexes
        db.users.create_index([("email", 1)], unique=True)
        db.users.create_index([("is_active", 1)])
        db.users.create_index([("created_at", -1)])
        
        # Competitive insights collection indexes
        db.competitive_insights.create_index([("opportunity_id", 1)])
        db.competitive_insights.create_index([("insight_type", 1)])
        db.competitive_insights.create_index([("created_at", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        raise

def insert_sample_awards(db):
    """
    Insert sample award data for demonstration
    """
    try:
        sample_awards = [
            {
                "_id": str(ObjectId()),
                "user_id": "sample_user_1",
                "opportunity_id": "DEPT-ED-2024-001",
                "award_number": "ED-24-CO-0157",
                "award_amount": 750000,
                "award_date": datetime.utcnow() - timedelta(days=45),
                "reported_date": datetime.utcnow() - timedelta(days=43),
                "verification_status": "verified",
                "verification_attempts": 1,
                "is_public": True,
                "success_story": "GrantAI Pro's competitive intelligence showed us exactly what reviewers were looking for. We tailored our STEM education proposal and won our largest grant ever!",
                "organization_name": "Metro Community College",
                "project_title": "Advanced STEM Learning Initiative",
                "project_description": "Expanding hands-on STEM education programs in underserved communities",
                "created_at": datetime.utcnow() - timedelta(days=43),
                "updated_at": datetime.utcnow() - timedelta(days=40)
            },
            {
                "_id": str(ObjectId()),
                "user_id": "sample_user_2", 
                "opportunity_id": "DEPT-ENERGY-2024-002",
                "award_number": "DE-24-EE-1234",
                "award_amount": 1200000,
                "award_date": datetime.utcnow() - timedelta(days=30),
                "reported_date": datetime.utcnow() - timedelta(days=28),
                "verification_status": "verified",
                "verification_attempts": 1,
                "is_public": True,
                "success_story": "The AI application generator created a compelling narrative that highlighted our innovative approach to solar energy storage. Reviewers said it was one of the best proposals they'd seen.",
                "organization_name": "Green Energy Solutions Inc.",
                "project_title": "Next-Generation Solar Storage Systems",
                "project_description": "Developing advanced battery systems for residential solar installations",
                "created_at": datetime.utcnow() - timedelta(days=28),
                "updated_at": datetime.utcnow() - timedelta(days=25)
            },
            {
                "_id": str(ObjectId()),
                "user_id": "sample_user_3",
                "opportunity_id": "DEPT-HHS-2024-003", 
                "award_number": "HHS-24-RA-5678",
                "award_amount": 425000,
                "award_date": datetime.utcnow() - timedelta(days=20),
                "reported_date": datetime.utcnow() - timedelta(days=18),
                "verification_status": "verified",
                "verification_attempts": 1,
                "is_public": True,
                "success_story": "GrantAI Pro helped us identify this rural health opportunity that perfectly matched our clinic's mission. The platform guided us through every step of the application process.",
                "organization_name": "Mountain View Health Clinic",
                "project_title": "Rural Healthcare Access Expansion",
                "project_description": "Expanding telehealth services to remote mountain communities",
                "created_at": datetime.utcnow() - timedelta(days=18),
                "updated_at": datetime.utcnow() - timedelta(days=15)
            },
            {
                "_id": str(ObjectId()),
                "user_id": "sample_user_4",
                "opportunity_id": "DEPT-NSF-2024-004",
                "award_number": "NSF-24-DMS-9876",
                "award_amount": 890000,
                "award_date": datetime.utcnow() - timedelta(days=15),
                "reported_date": datetime.utcnow() - timedelta(days=13),
                "verification_status": "verified",
                "verification_attempts": 1,
                "is_public": True,
                "success_story": "The success probability scoring feature helped us focus on the right opportunities. We went from a 12% success rate to 38% after using GrantAI Pro.",
                "organization_name": "Advanced Research Institute",
                "project_title": "AI-Driven Climate Modeling",
                "project_description": "Developing machine learning models for enhanced climate prediction",
                "created_at": datetime.utcnow() - timedelta(days=13),
                "updated_at": datetime.utcnow() - timedelta(days=10)
            },
            {
                "_id": str(ObjectId()),
                "user_id": "sample_user_5",
                "opportunity_id": "DEPT-USDA-2024-005",
                "award_number": "USDA-24-NIFA-1111",
                "award_amount": 320000,
                "award_date": datetime.utcnow() - timedelta(days=10),
                "reported_date": datetime.utcnow() - timedelta(days=8),
                "verification_status": "verified",
                "verification_attempts": 1,
                "is_public": True,
                "success_story": "As a small nonprofit, we never thought we could compete with larger organizations. GrantAI Pro leveled the playing field and helped us craft a winning proposal.",
                "organization_name": "Sustainable Farming Collective",
                "project_title": "Organic Agriculture Training Program",
                "project_description": "Training local farmers in sustainable organic farming practices",
                "created_at": datetime.utcnow() - timedelta(days=8),
                "updated_at": datetime.utcnow() - timedelta(days=5)
            },
            {
                "_id": str(ObjectId()),
                "user_id": "sample_user_6",
                "opportunity_id": "DEPT-DOD-2024-006",
                "award_number": "DOD-24-SBIR-2222",
                "award_amount": 1500000,
                "award_date": datetime.utcnow() - timedelta(days=5),
                "reported_date": datetime.utcnow() - timedelta(days=3),
                "verification_status": "partial_match",
                "verification_attempts": 2,
                "is_public": True,
                "success_story": "The competitive intelligence feature showed us what our competitors were doing wrong. We differentiated our cybersecurity solution and won this Phase II SBIR grant.",
                "organization_name": "CyberDefense Technologies",
                "project_title": "Advanced Threat Detection System",
                "project_description": "AI-powered cybersecurity system for military applications",
                "created_at": datetime.utcnow() - timedelta(days=3),
                "updated_at": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        # Insert sample awards
        db.awards.insert_many(sample_awards)
        
        # Create corresponding sample applications
        sample_applications = []
        for award in sample_awards:
            app = {
                "_id": str(ObjectId()),
                "user_id": award["user_id"],
                "opportunity_id": award["opportunity_id"],
                "status": "awarded",
                "award_amount": award["award_amount"],
                "award_date": award["award_date"],
                "award_number": award["award_number"],
                "submitted_date": award["award_date"] - timedelta(days=90),
                "success_probability": random.randint(75, 95),
                "time_to_complete": random.randint(8, 24),
                "user_satisfaction_score": random.randint(8, 10),
                "created_at": award["award_date"] - timedelta(days=120),
                "updated_at": award["updated_at"]
            }
            sample_applications.append(app)
        
        db.applications.insert_many(sample_applications)
        
        # Create sample user activity for awards
        sample_activities = []
        for award in sample_awards:
            activity = {
                "_id": str(ObjectId()),
                "user_id": award["user_id"],
                "activity_type": "award_reported",
                "opportunity_id": award["opportunity_id"],
                "metadata": {
                    "award_amount": award["award_amount"],
                    "success_type": "grant_award"
                },
                "timestamp": award["reported_date"],
                "session_id": f"award_{award['reported_date'].strftime('%Y%m%d_%H%M%S')}"
            }
            sample_activities.append(activity)
        
        db.user_activities.insert_many(sample_activities)
        
        logger.info(f"Inserted {len(sample_awards)} sample awards with corresponding applications and activities")
        
    except Exception as e:
        logger.error(f"Error inserting sample awards: {str(e)}")
        raise

def ensure_admin_user(db):
    """
    Ensure admin user exists for testing
    """
    try:
        admin_user = db.users.find_one({"email": "admin@grantai.pro"})
        if not admin_user:
            admin_data = {
                "_id": str(ObjectId()),
                "email": "admin@grantai.pro",
                "password_hash": "hashed_password_placeholder",  # In production, use proper hashing
                "first_name": "Admin",
                "last_name": "User",
                "organization_name": "GrantAI Pro",
                "role": "admin",
                "is_active": True,
                "is_admin": True,
                "created_at": datetime.utcnow(),
                "stripe_customer_id": None
            }
            db.users.insert_one(admin_data)
            logger.info("Admin user created")
        
        # Ensure test user exists
        test_user = db.users.find_one({"email": "test@grantai.pro"})
        if not test_user:
            test_data = {
                "_id": str(ObjectId()),
                "email": "test@grantai.pro", 
                "password_hash": "hashed_password_placeholder",  # In production, use proper hashing
                "first_name": "Test",
                "last_name": "User",
                "organization_name": "Test Organization",
                "role": "user",
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.utcnow(),
                "stripe_customer_id": None
            }
            db.users.insert_one(test_data)
            logger.info("Test user created")
            
    except Exception as e:
        logger.error(f"Error ensuring admin user: {str(e)}")
        raise

def verify_database_setup(db):
    """
    Verify that database setup completed successfully
    """
    try:
        # Check collections exist and have data
        collections = {
            "users": db.users.count_documents({}),
            "opportunities": db.opportunities.count_documents({}),
            "applications": db.applications.count_documents({}),
            "awards": db.awards.count_documents({}),
            "user_activities": db.user_activities.count_documents({}),
            "competitive_insights": db.competitive_insights.count_documents({})
        }
        
        logger.info("Database verification:")
        for collection, count in collections.items():
            logger.info(f"  {collection}: {count} documents")
        
        # Verify indexes exist
        for collection_name in collections.keys():
            collection = getattr(db, collection_name)
            indexes = list(collection.list_indexes())
            logger.info(f"  {collection_name} indexes: {len(indexes)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False

def cleanup_test_data(db):
    """
    Clean up test/sample data (use with caution in production)
    """
    try:
        # Remove sample users
        db.users.delete_many({"email": {"$in": ["admin@grantai.pro", "test@grantai.pro"]}})
        
        # Remove sample awards and related data
        sample_user_ids = [f"sample_user_{i}" for i in range(1, 7)]
        db.awards.delete_many({"user_id": {"$in": sample_user_ids}})
        db.applications.delete_many({"user_id": {"$in": sample_user_ids}})
        db.user_activities.delete_many({"user_id": {"$in": sample_user_ids}})
        
        logger.info("Test data cleaned up")
        
    except Exception as e:
        logger.error(f"Error cleaning up test data: {str(e)}")
        raise
    