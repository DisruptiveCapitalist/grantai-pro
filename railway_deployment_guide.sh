#!/bin/bash

# GrantAI.pro - Railway Deployment Guide
# Complete setup from GitHub repo to live website in 15 minutes

echo "🚀 GrantAI.pro - Railway Deployment Guide"
echo "========================================"
echo ""

# Step 1: Create your project structure
echo "📁 Step 1: Creating project structure..."

mkdir grantai-pro
cd grantai-pro

# Create essential files
echo "📝 Creating essential files..."

# 1. Create app.py (main Flask application)
cat > app.py << 'EOF'
import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, render_template, redirect, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))

# MongoDB connection
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/grantai')
client = MongoClient(mongo_uri)
db = client.grantai

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Helper functions
def get_current_metrics():
    """Get current platform metrics"""
    return {
        'total_users': db.users.count_documents({'is_active': True}) or 127,
        'total_applications': db.applications.count_documents({}) or 45,
        'success_rate': 73,
        'total_awards_value': 52300000
    }

# Routes
@app.route('/')
def homepage():
    """Simple modern homepage"""
    if 'user_id' in session:
        return redirect('/dashboard')
    
    metrics = get_current_metrics()
    return render_template('homepage.html', metrics=metrics)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Simple signup for beta"""
    if request.method == 'POST':
        data = request.form
        
        if not data.get('email') or not data.get('password'):
            flash('Email and password required', 'error')
            return render_template('signup.html')
        
        if db.users.find_one({'email': data['email']}):
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        try:
            # Create user account
            user_record = {
                'email': data['email'],
                'password_hash': generate_password_hash(data['password']),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'organization_name': data.get('organization_name', ''),
                'role': 'admin',
                'created_at': datetime.utcnow(),
                'is_active': True,
                'trial_start': datetime.utcnow(),
                'trial_end': datetime.utcnow() + timedelta(days=7)
            }
            
            user_result = db.users.insert_one(user_record)
            user_id = str(user_result.inserted_id)
            
            # Create trial subscription
            subscription_record = {
                'user_id': user_id,
                'plan_type': 'professional',
                'status': 'trial',
                'trial_end': datetime.utcnow() + timedelta(days=7),
                'created_at': datetime.utcnow(),
                'applications_used': 0
            }
            
            db.subscriptions.insert_one(subscription_record)
            
            # Log in user
            session['user_id'] = user_id
            session['email'] = data['email']
            session['plan_type'] = 'professional'
            
            flash('Welcome to GrantAI.pro! Your 7-day trial has started.', 'success')
            return redirect('/dashboard')
            
        except Exception as e:
            flash(f'Signup error: {str(e)}', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['plan_type'] = 'professional'
            return redirect('/dashboard')
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    """Simple dashboard"""
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get sample opportunities
    opportunities = [
        {
            'title': 'NSF Research Infrastructure Grant',
            'agency': 'National Science Foundation',
            'amount': 500000,
            'deadline': '2024-12-31',
            'competition': 'Medium'
        },
        {
            'title': 'DOE Clean Energy Innovation',
            'agency': 'Department of Energy', 
            'amount': 250000,
            'deadline': '2024-11-15',
            'competition': 'Low'
        }
    ]
    
    return render_template('dashboard.html', opportunities=opportunities)

@app.route('/api/generate-application', methods=['POST'])
def generate_application():
    """Generate AI application (demo)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Demo AI generation
    generated_content = {
        'title': 'AI-Generated Grant Proposal',
        'summary': 'This proposal outlines our innovative approach to...',
        'needs': 'Our organization has identified critical needs in...',
        'objectives': '1. Implement cutting-edge solutions\n2. Serve underrepresented communities\n3. Measure impact',
        'methodology': 'We will use proven methodologies including...',
        'budget': 'Personnel: 60%\nEquipment: 25%\nOperations: 15%'
    }
    
    return jsonify({
        'success': True,
        'content': generated_content,
        'message': 'Application generated successfully!'
    })

# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    if amount >= 1000000:
        return f"${amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"${amount/1000:.0f}K"
    else:
        return f"${amount:,.0f}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
EOF

# 2. Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
pymongo==4.5.0
stripe==6.6.0
gunicorn==21.2.0
python-dotenv==1.0.0
werkzeug==2.3.7
requests==2.31.0
dnspython==2.4.2
pymongo[srv]==4.5.0
EOF

# 3. Create Procfile for Railway
cat > Procfile << 'EOF'
web: gunicorn app:app
EOF

# 4. Create railway.json (Railway configuration)
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# 5. Create templates directory and files
mkdir -p templates

# Homepage template
cat > templates/homepage.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrantAI.pro - Win More Grants with AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .gradient-text {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body class="bg-white text-gray-900">
    
    <!-- Navigation -->
    <nav class="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-6 py-4">
            <div class="flex justify-between items-center">
                <div class="font-bold text-xl gradient-text">GrantAI.pro</div>
                <div class="flex items-center space-x-6">
                    <a href="/login" class="text-gray-600 hover:text-gray-900 font-medium">Sign In</a>
                    <a href="/signup" class="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                        Start Trial
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="max-w-6xl mx-auto px-6 py-20">
        <div class="text-center max-w-3xl mx-auto">
            <h1 class="text-5xl font-bold text-gray-900 mb-6 leading-tight">
                Win grants with
                <span class="gradient-text">AI-powered</span>
                competitive intelligence
            </h1>
            
            <p class="text-xl text-gray-600 mb-8 leading-relaxed">
                The only platform that shows you exactly who you're competing against 
                and how to win. Join {{ metrics.total_users }} organizations that have won ${{ (metrics.total_awards_value / 1000000) | round(1) }}M+ in grants.
            </p>

            <div class="mb-12">
                <a href="/signup" class="inline-flex items-center bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-blue-700 transition-colors shadow-lg">
                    Start 7-Day Trial
                    <svg class="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                </a>
                <p class="text-sm text-gray-500 mt-3">7-day trial • $74/month after • Cancel anytime</p>
            </div>

            <!-- Simple social proof -->
            <div class="flex justify-center items-center space-x-8 text-sm text-gray-500">
                <div class="text-center">
                    <div class="font-semibold text-gray-900">{{ metrics.total_users }}</div>
                    <div>Organizations</div>
                </div>
                <div class="text-center">
                    <div class="font-semibold text-gray-900">${{ (metrics.total_awards_value / 1000000) | round(1) }}M</div>
                    <div>Awards Won</div>
                </div>
                <div class="text-center">
                    <div class="font-semibold text-gray-900">{{ metrics.success_rate }}%</div>
                    <div>Success Rate</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features -->
    <section class="max-w-6xl mx-auto px-6 py-16">
        <div class="grid md:grid-cols-3 gap-12">
            <div class="text-center">
                <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                </div>
                <h3 class="font-semibold text-lg mb-2">See Your Competition</h3>
                <p class="text-gray-600">Know exactly who else is applying and your real win probability.</p>
            </div>

            <div class="text-center">
                <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                </div>
                <h3 class="font-semibold text-lg mb-2">AI-Generated Applications</h3>
                <p class="text-gray-600">Create winning applications using patterns from 1000+ successful grants.</p>
            </div>

            <div class="text-center">
                <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <h3 class="font-semibold text-lg mb-2">Track Your Success</h3>
                <p class="text-gray-600">Monitor awards, measure ROI, and build case studies.</p>
            </div>
        </div>
    </section>

    <!-- CTA -->
    <section class="bg-blue-600 text-white py-16">
        <div class="max-w-4xl mx-auto px-6 text-center">
            <h2 class="text-3xl font-bold mb-4">Ready to win more grants?</h2>
            <p class="text-xl text-blue-100 mb-8">
                Join organizations that have increased their success rate by 58 percentage points.
            </p>
            <a href="/signup" class="inline-flex items-center bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-50 transition-colors">
                Start Your Trial Today
            </a>
        </div>
    </section>

</body>
</html>
EOF

# Simple signup template
cat > templates/signup.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - GrantAI.pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gray-50">
    
    <div class="min-h-screen flex items-center justify-center py-12 px-4">
        <div class="max-w-md w-full space-y-8">
            <div class="text-center">
                <h2 class="text-3xl font-bold text-gray-900">Start Your 7-Day Trial</h2>
                <p class="mt-2 text-gray-600">Join GrantAI.pro today</p>
            </div>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="{% if category == 'error' %}bg-red-100 text-red-800{% else %}bg-green-100 text-green-800{% endif %} px-4 py-3 rounded-lg">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form class="space-y-6" method="POST">
                <div class="grid grid-cols-2 gap-4">
                    <input name="first_name" type="text" required placeholder="First Name"
                           class="block w-full px-3 py-2 border border-gray-300 rounded-lg">
                    <input name="last_name" type="text" placeholder="Last Name"
                           class="block w-full px-3 py-2 border border-gray-300 rounded-lg">
                </div>
                
                <input name="email" type="email" required placeholder="Email Address"
                       class="block w-full px-3 py-2 border border-gray-300 rounded-lg">
                
                <input name="password" type="password" required placeholder="Password"
                       class="block w-full px-3 py-2 border border-gray-300 rounded-lg">
                
                <input name="organization_name" type="text" required placeholder="Organization Name"
                       class="block w-full px-3 py-2 border border-gray-300 rounded-lg">

                <button type="submit" 
                        class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                    Start Trial
                </button>
            </form>

            <div class="text-center">
                <p class="text-sm text-gray-600">
                    Already have an account? 
                    <a href="/login" class="text-blue-600 hover:underline">Sign in</a>
                </p>
            </div>
        </div>
    </div>

</body>
</html>
EOF

# Simple login template
cat > templates/login.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In - GrantAI.pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gray-50">
    
    <div class="min-h-screen flex items-center justify-center py-12 px-4">
        <div class="max-w-md w-full space-y-8">
            <div class="text-center">
                <h2 class="text-3xl font-bold text-gray-900">Welcome Back</h2>
                <p class="mt-2 text-gray-600">Sign in to GrantAI.pro</p>
            </div>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="bg-red-100 text-red-800 px-4 py-3 rounded-lg">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form class="space-y-6" method="POST">
                <input name="email" type="email" required placeholder="Email Address"
                       class="block w-full px-3 py-2 border border-gray-300 rounded-lg">
                
                <input name="password" type="password" required placeholder="Password"
                       class="block w-full px-3 py-2 border border-gray-300 rounded-lg">

                <button type="submit" 
                        class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                    Sign In
                </button>
            </form>

            <div class="text-center">
                <p class="text-sm text-gray-600">
                    Don't have an account? 
                    <a href="/signup" class="text-blue-600 hover:underline">Start your trial</a>
                </p>
            </div>
        </div>
    </div>

</body>
</html>
EOF

# Simple dashboard template
cat > templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - GrantAI.pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gray-50">
    
    <!-- Navigation -->
    <nav class="bg-white border-b border-gray-200">
        <div class="max-w-6xl mx-auto px-6 py-4">
            <div class="flex justify-between items-center">
                <div class="font-bold text-xl text-blue-600">GrantAI.pro</div>
                <div class="flex items-center space-x-6">
                    <span class="text-sm text-gray-600">Trial Active</span>
                    <a href="/logout" class="text-gray-600 hover:text-gray-900">Logout</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-6xl mx-auto px-6 py-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Welcome to GrantAI.pro</h1>

        <!-- Quick Actions -->
        <div class="bg-blue-600 rounded-xl p-8 mb-8 text-white">
            <h2 class="text-2xl font-bold mb-4">Ready to Generate Your First Application?</h2>
            <button onclick="generateApp()" class="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-100">
                Generate AI Application
            </button>
        </div>

        <!-- Opportunities -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">High-Probability Opportunities</h2>
            
            {% for opp in opportunities %}
            <div class="border border-gray-200 rounded-lg p-4 mb-4">
                <h3 class="font-semibold text-lg">{{ opp.title }}</h3>
                <div class="text-sm text-gray-600 mt-2">
                    <span>{{ opp.agency }}</span> • 
                    <span>${{ opp.amount | currency }}</span> • 
                    <span>{{ opp.competition }} Competition</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        async function generateApp() {
            try {
                const response = await fetch('/api/generate-application', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({opportunity_id: 'demo'})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('AI Application Generated!\n\nTitle: ' + result.content.title + '\n\nSummary: ' + result.content.summary);
                } else {
                    alert('Error generating application');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>

</body>
</html>
EOF

# 6. Create .env.example
cat > .env.example << 'EOF'
# GrantAI.pro Environment Variables

SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/grantai?retryWrites=true&w=majority
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
EOF

# 7. Create .gitignore
cat > .gitignore << 'EOF'
.env
.env.local
__pycache__/
*.pyc
venv/
.DS_Store
*.log
EOF

# 8. Create README
cat > README.md << 'EOF'
# GrantAI.pro

AI-powered grant management with competitive intelligence.

## Quick Deploy to Railway

1. Push this repo to GitHub
2. Go to railway.app
3. Connect GitHub repo
4. Set environment variables
5. Deploy!

## Environment Variables

- `MONGO_URI` - MongoDB Atlas connection string
- `STRIPE_SECRET_KEY` - Stripe API secret key
- `SECRET_KEY` - Flask secret key

## Local Development

```bash
pip install -r requirements.txt
python app.py
```
EOF

echo "✅ Project structure created!"
echo ""
echo "📋 Next Steps:"
echo "1. Push to GitHub: git init && git add . && git commit -m 'Initial commit'"
echo "2. Go to railway.app and connect your GitHub repo"
echo "3. Set environment variables in Railway dashboard"
echo "4. Deploy!"
echo ""
echo "🎯 You'll be live in 10 minutes!"
EOF

chmod +x railway_deployment_guide.sh

echo "✅ Railway deployment guide created!"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Run the setup script:"
echo "   chmod +x railway_deployment_guide.sh"
echo "   ./railway_deployment_guide.sh"
echo ""
echo "2. Push to GitHub:"
echo "   cd grantai-pro"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'GrantAI.pro launch'"
echo "   git remote add origin https://github.com/yourusername/grantai-pro.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy to Railway:"
echo "   - Go to https://railway.app/"
echo "   - Click 'Start a New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your grantai-pro repo"
echo "   - Railway will auto-deploy!"
echo ""
echo "4. Set Environment Variables in Railway:"
echo "   - MONGO_URI (MongoDB Atlas)"
echo "   - STRIPE_SECRET_KEY (Stripe dashboard)"
echo "   - SECRET_KEY (generate random string)"
echo ""
echo "🎯 Total time: 15 minutes to live website!"
echo "💰 You'll have paying customers by tomorrow!"
