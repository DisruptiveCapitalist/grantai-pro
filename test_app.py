#!/usr/bin/env python3
"""
GrantAI Pro - Test Flask App with Competitive Intelligence
Simple app to test the competitive intelligence APIs
"""

from flask import Flask, render_template_string, jsonify, request, session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our competitive intelligence API
from api.competitive import register_competitive_routes

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'test-secret-key')

# Register competitive intelligence routes
register_competitive_routes(app)

# Simple HTML template for testing
TEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GrantAI Pro - Competitive Intelligence Test</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f7fa;
        }
        .header {
            background: linear-gradient(135deg, #4ecdc4, #44a08d);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
        }
        .test-section {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .test-button {
            background: #4ecdc4;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 14px;
        }
        .test-button:hover {
            background: #44a08d;
        }
        .result {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            font-family: monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        .endpoint {
            color: #6c757d;
            font-size: 12px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 GrantAI Pro - Competitive Intelligence</h1>
        <p>Testing Phase 2 Features</p>
    </div>

    <div class="test-section">
        <h2>📊 API Testing Dashboard</h2>
        <p>Test the competitive intelligence APIs to see them in action!</p>
        
        <div class="endpoint">POST /api/competitive/track</div>
        <button class="test-button" onclick="testTracking()">Track User Activity</button>
        
        <div class="endpoint">GET /api/competitive/test</div>
        <button class="test-button" onclick="testAPI()">Test API</button>
        
        <div class="endpoint">GET /api/competitive/trending</div>
        <button class="test-button" onclick="getTrending()">Get Trending Opportunities</button>
        
        <div class="endpoint">GET /api/competitive/stats/global</div>
        <button class="test-button" onclick="getGlobalStats()">Get Global Stats</button>
        
        <div class="endpoint">GET /api/competitive/recommendations</div>
        <button class="test-button" onclick="getRecommendations()">Get Recommendations</button>
        
        <div class="endpoint">GET /api/competitive/activity/summary</div>
        <button class="test-button" onclick="getActivitySummary()">Get Activity Summary</button>
        
        <button class="test-button" onclick="clearResults()" style="background: #dc3545;">Clear Results</button>
        
        <div id="results" class="result" style="display: none;"></div>
    </div>

    <div class="test-section">
        <h2>🎯 What's Working</h2>
        <ul>
            <li>✅ <strong>MongoDB Atlas Connection</strong> - Connected to cloud database</li>
            <li>✅ <strong>Competitive Intelligence Service</strong> - Core logic working</li>
            <li>✅ <strong>API Endpoints</strong> - All routes registered successfully</li>
            <li>✅ <strong>User Activity Tracking</strong> - Ready to track user behavior</li>
            <li>✅ <strong>Competition Level Calculation</strong> - Algorithm working</li>
            <li>✅ <strong>Trending Analysis</strong> - Can identify hot opportunities</li>
        </ul>
    </div>

    <div class="test-section">
        <h2>🚀 Next Steps (Phase 2 Completion)</h2>
        <ol>
            <li><strong>Test all APIs</strong> using the buttons above</li>
            <li><strong>Add competition badges</strong> to opportunity listings</li>
            <li><strong>Create competitive dashboard</strong> for users</li>
            <li><strong>Integrate with main app</strong> (app.py)</li>
            <li><strong>Add real-time activity tracking</strong> to frontend</li>
        </ol>
    </div>

    <script>
        function showResult(data) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'block';
            resultsDiv.textContent = JSON.stringify(data, null, 2);
        }

        function clearResults() {
            const resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'none';
            resultsDiv.textContent = '';
        }

        async function testAPI() {
            try {
                const response = await fetch('/api/competitive/test');
                const data = await response.json();
                showResult(data);
            } catch (error) {
                showResult({error: 'Failed to test API: ' + error.message});
            }
        }

        async function testTracking() {
            try {
                const response = await fetch('/api/competitive/track', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'view',
                        opportunity_id: 'test_opportunity_' + Date.now(),
                        metadata: {
                            source: 'test_dashboard'
                        }
                    })
                });
                const data = await response.json();
                showResult(data);
            } catch (error) {
                showResult({error: 'Failed to track activity: ' + error.message});
            }
        }

        async function getTrending() {
            try {
                const response = await fetch('/api/competitive/trending?limit=5');
                const data = await response.json();
                showResult(data);
            } catch (error) {
                showResult({error: 'Failed to get trending: ' + error.message});
            }
        }

        async function getGlobalStats() {
            try {
                const response = await fetch('/api/competitive/stats/global');
                const data = await response.json();
                showResult(data);
            } catch (error) {
                showResult({error: 'Failed to get stats: ' + error.message});
            }
        }

        async function getRecommendations() {
            try {
                const response = await fetch('/api/competitive/recommendations?limit=3');
                const data = await response.json();
                showResult(data);
            } catch (error) {
                showResult({error: 'Failed to get recommendations: ' + error.message});
            }
        }

        async function getActivitySummary() {
            try {
                const response = await fetch('/api/competitive/activity/summary?days=7');
                const data = await response.json();
                showResult(data);
            } catch (error) {
                showResult({error: 'Failed to get activity summary: ' + error.message});
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Homepage with API testing interface"""
    return render_template_string(TEST_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'GrantAI Pro Competitive Intelligence is running!',
        'features': [
            'User Activity Tracking',
            'Competition Level Analysis',
            'Trending Opportunity Detection',
            'Personalized Recommendations',
            'Global Statistics'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting GrantAI Pro Test App...")
    print("📊 Competitive Intelligence Features Available:")
    print("   • User activity tracking")
    print("   • Competition level calculation") 
    print("   • Trending opportunity detection")
    print("   • Personalized recommendations")
    print("   • Global competitive statistics")
    print("\n🌐 Open your browser to: http://localhost:5002")
    print("🧪 Use the test buttons to verify all APIs work!")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5002)
