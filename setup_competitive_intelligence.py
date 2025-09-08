#!/usr/bin/env python3
"""
GrantAI Pro - Competitive Intelligence Setup Script
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
import json
from dotenv import load_dotenv

load_dotenv()

def setup_competitive_intelligence():
    print("🚀 Setting up GrantAI Pro Competitive Intelligence...")
    print("=" * 60)
    
    # Connect to MongoDB
    print("\n📁 Connecting to MongoDB...")
    
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/grantai')
    print(f"   Using URI: {MONGO_URI[:50]}...")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.grantai
        
        # Test connection
        db.command('ping')
        print("   ✅ Connected to MongoDB Atlas successfully!")
        
        # Create basic collections
        collections_to_create = [
            'user_activity',
            'competitive_insights',
            'application_tracking'
        ]
        
        for collection_name in collections_to_create:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"   ✅ Created collection: {collection_name}")
            else:
                print(f"   ℹ️ Collection already exists: {collection_name}")
        
        # Create directories
        directories = ['services', 'api', 'templates']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"   ✅ Created directory: {directory}")
        
        print("\n🎉 Basic setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GrantAI Pro - Competitive Intelligence Setup")
    success = setup_competitive_intelligence()
    
    if success:
        print("\n✅ Setup completed!")
    else:
        print("\n❌ Setup failed.")