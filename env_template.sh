# GrantAI Pro - Environment Variables
# Copy this file to .env and update with your actual values

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=development

# MongoDB Atlas Configuration
# Replace with your actual MongoDB Atlas connection string
# Format: mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
MONGO_URI=mongodb+srv://sam_db_user:YOUR_PASSWORD@cluster0.s7k3hey.mongodb.net/grantai?retryWrites=true&w=majority

# Payment Processing (Stripe) - Get from Stripe Dashboard
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# External APIs for Grant Discovery
GRANTS_GOV_API_KEY=your_grants_gov_api_key_here
SAM_GOV_API_KEY=your_sam_gov_api_key_here

# Email Configuration (Optional - for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Application Configuration
PORT=5000
DEBUG=True

# Security Configuration
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# ==== IMPORTANT SETUP NOTES ====
# 
# 1. MONGO_URI: 
#    - Log into MongoDB Atlas (cloud.mongodb.com)
#    - Go to your cluster: cluster0.s7k3hey.mongodb.net
#    - Click "Connect" → "Connect your application"
#    - Copy the connection string and replace YOUR_PASSWORD with your actual password
#
# 2. SECRET_KEY:
#    - Generate a secure random key: python -c "import secrets; print(secrets.token_hex(32))"
#    - Replace the value above with your generated key
#
# 3. Stripe Keys (for billing - can be left as test keys for now):
#    - Sign up at stripe.com
#    - Get test keys from the Stripe Dashboard
#    - For production, replace with live keys
#
# 4. External API Keys (optional for Phase 1):
#    - Grants.gov: https://www.grants.gov/grantsws/rest
#    - SAM.gov: https://open.gsa.gov/api/entity-api/
#    - These are needed for live grant discovery in Phase 1 Week 2
