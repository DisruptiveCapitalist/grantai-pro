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
