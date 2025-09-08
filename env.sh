# GrantAI Pro Environment Configuration
# Copy this file to .env and update with your actual values

# Flask Configuration
SECRET_KEY=your-secret-key-here-generate-a-long-random-string
FLASK_ENV=development
FLASK_DEBUG=true

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/grantai

# For production with MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/grantai?retryWrites=true&w=majority

# Stripe Configuration (get from stripe.com/dashboard)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# External API Keys
GRANTS_GOV_API_KEY=your_grants_gov_api_key_here
SAM_GOV_API_KEY=your_sam_gov_api_key_here

# Email Configuration (for notifications - optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=grantai.log

# Security Configuration
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Feature Flags
COMPETITIVE_INTELLIGENCE_ENABLED=true
AWARD_TRACKING_ENABLED=true
PUBLIC_METRICS_ENABLED=true

# Development Settings
TESTING=false
DEBUG_MODE=true
