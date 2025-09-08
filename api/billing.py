# api/billing.py
"""
Billing API with Promo Code Support for GrantAI Pro
Handles subscription creation, promo codes, and pricing calculations
"""

from flask import Blueprint, request, jsonify, session
from config.pricing_plans import PricingCalculator, PRICING_PLANS, get_plan_comparison, get_legal_disclaimers
from datetime import datetime, timedelta
from bson import ObjectId
import stripe
import os
import logging

billing_bp = Blueprint('billing', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def init_billing_api(app, db):
    """Initialize billing API with Flask app and dependencies"""
    
    pricing_calculator = PricingCalculator(db)
    
    @billing_bp.route('/api/pricing/plans', methods=['GET'])
    def get_pricing_plans():
        """
        Get all pricing plans for display on pricing page
        """
        try:
            plans = get_plan_comparison()
            return jsonify({
                'success': True,
                'plans': plans,
                'disclaimers': get_legal_disclaimers()
            })
        except Exception as e:
            logger.error(f"Error getting pricing plans: {str(e)}")
            return jsonify({'error': 'Unable to fetch pricing plans'}), 500
    
    @billing_bp.route('/api/pricing/calculate', methods=['POST'])
    def calculate_pricing():
        """
        Calculate pricing with optional promo code
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid request data'}), 400
            
            plan_id = data.get('plan_id')
            billing_cycle = data.get('billing_cycle', 'monthly')
            promo_code = data.get('promo_code')
            users = int(data.get('users', 1))
            
            if not plan_id or plan_id not in PRICING_PLANS:
                return jsonify({'error': 'Invalid plan selected'}), 400
            
            # Calculate pricing
            pricing = pricing_calculator.get_plan_price(
                plan_id=plan_id,
                billing_cycle=billing_cycle,
                promo_code=promo_code,
                users=users
            )
            
            return jsonify({
                'success': True,
                'pricing': pricing
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error calculating pricing: {str(e)}")
            return jsonify({'error': 'Unable to calculate pricing'}), 500
    
    @billing_bp.route('/api/promo/validate', methods=['POST'])
    def validate_promo_code():
        """
        Validate a promo code for a specific plan
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid request data'}), 400
            
            promo_code = data.get('promo_code', '').strip()
            plan_id = data.get('plan_id')
            
            if not promo_code:
                return jsonify({'error': 'Promo code is required'}), 400
            
            if not plan_id or plan_id not in PRICING_PLANS:
                return jsonify({'error': 'Invalid plan selected'}), 400
            
            # Validate promo code
            validation = pricing_calculator.validate_promo_code(promo_code, plan_id)
            
            return jsonify({
                'success': True,
                'validation': validation
            })
            
        except Exception as e:
            logger.error(f"Error validating promo code: {str(e)}")
            return jsonify({'error': 'Unable to validate promo code'}), 500
    
    @billing_bp.route('/api/subscription/create', methods=['POST'])
    def create_subscription():
        """
        Create a new subscription with Stripe
        """
        try:
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid request data'}), 400
            
            # Extract subscription details
            plan_id = data.get('plan_id')
            billing_cycle = data.get('billing_cycle', 'monthly')
            promo_code = data.get('promo_code')
            users = int(data.get('users', 1))
            payment_method_id = data.get('payment_method_id')
            
            if not plan_id or plan_id not in PRICING_PLANS:
                return jsonify({'error': 'Invalid plan selected'}), 400
            
            if not payment_method_id:
                return jsonify({'error': 'Payment method required'}), 400
            
            # Get user details
            user = db.users.find_one({"_id": session['user_id']})
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Calculate final pricing
            pricing = pricing_calculator.get_plan_price(
                plan_id=plan_id,
                billing_cycle=billing_cycle,
                promo_code=promo_code,
                users=users
            )
            
            # Create or retrieve Stripe customer
            stripe_customer_id = user.get('stripe_customer_id')
            if not stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user['email'],
                    name=f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    metadata={
                        'user_id': session['user_id'],
                        'organization': user.get('organization_name', '')
                    }
                )
                stripe_customer_id = customer.id
                
                # Update user with Stripe customer ID
                db.users.update_one(
                    {"_id": session['user_id']},
                    {"$set": {"stripe_customer_id": stripe_customer_id}}
                )
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer_id
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            # Create subscription in Stripe
            subscription_data = {
                'customer': stripe_customer_id,
                'items': [{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"GrantAI Pro - {pricing['plan_name']}",
                            'description': PRICING_PLANS[plan_id]['description']
                        },
                        'recurring': {
                            'interval': 'month' if billing_cycle == 'monthly' else 'year'
                        },
                        'unit_amount': int(pricing['final_price'] * 100)  # Stripe uses cents
                    },
                    'quantity': users if plan_id in ['team', 'enterprise'] else 1
                }],
                'metadata': {
                    'user_id': session['user_id'],
                    'plan_id': plan_id,
                    'billing_cycle': billing_cycle,
                    'promo_code': promo_code or '',
                    'users': str(users)
                },
                'trial_period_days': 7  # 7-day trial for all plans
            }
            
            # Apply promo code as coupon if applicable
            if promo_code and pricing['discount_amount'] > 0:
                # Create or retrieve Stripe coupon for promo code
                coupon_id = f"promo_{promo_code.lower()}"
                try:
                    stripe.Coupon.retrieve(coupon_id)
                except stripe.error.InvalidRequestError:
                    # Create coupon if it doesn't exist
                    stripe.Coupon.create(
                        id=coupon_id,
                        percent_off=50 if 'BETA50' in promo_code or 'LAUNCH2025' in promo_code else 25,
                        duration='forever' if promo_code == 'BETA50' else 'repeating',
                        duration_in_months=12 if promo_code == 'FOUNDER25' else 6 if promo_code == 'LAUNCH2025' else None,
                        name=f"Promo Code: {promo_code}"
                    )
                
                subscription_data['coupon'] = coupon_id
            
            stripe_subscription = stripe.Subscription.create(**subscription_data)
            
            # Create subscription record in database
            subscription_record = {
                "_id": str(ObjectId()),
                "user_id": session['user_id'],
                "stripe_subscription_id": stripe_subscription.id,
                "stripe_customer_id": stripe_customer_id,
                "plan_id": plan_id,
                "plan_name": pricing['plan_name'],
                "billing_cycle": billing_cycle,
                "users": users,
                "status": "trialing",  # Will be active after trial
                "promo_code": promo_code,
                "discount_amount": pricing['discount_amount'],
                "base_price": pricing['base_price'],
                "final_price": pricing['final_price'],
                "trial_end": datetime.utcnow() + timedelta(days=7),
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow() + timedelta(days=7),
                "applications_used_this_period": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            db.subscriptions.insert_one(subscription_record)
            
            # Track promo code usage if applicable
            if promo_code:
                db.promo_code_usage.insert_one({
                    "_id": str(ObjectId()),
                    "promo_code": promo_code.upper(),
                    "user_id": session['user_id'],
                    "subscription_id": subscription_record["_id"],
                    "used_at": datetime.utcnow()
                })
            
            # Update user subscription status
            db.users.update_one(
                {"_id": session['user_id']},
                {
                    "$set": {
                        "subscription_id": subscription_record["_id"],
                        "plan_id": plan_id,
                        "subscription_status": "trialing",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return jsonify({
                'success': True,
                'subscription_id': subscription_record["_id"],
                'stripe_subscription_id': stripe_subscription.id,
                'trial_end': subscription_record["trial_end"].isoformat(),
                'message': 'Subscription created successfully! Your 7-day trial has started.'
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {str(e)}")
            return jsonify({'error': f'Payment error: {str(e)}'}), 400
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return jsonify({'error': 'Unable to create subscription'}), 500
    
    @billing_bp.route('/api/subscription/current', methods=['GET'])
    def get_current_subscription():
        """
        Get current user's subscription details
        """
        try:
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            subscription = db.subscriptions.find_one({
                "user_id": session['user_id'],
                "status": {"$in": ["trialing", "active", "past_due"]}
            })
            
            if not subscription:
                return jsonify({
                    'success': True,
                    'subscription': None,
                    'message': 'No active subscription found'
                })
            
            # Convert ObjectId and dates for JSON serialization
            subscription['_id'] = str(subscription['_id'])
            for date_field in ['trial_end', 'current_period_start', 'current_period_end', 'created_at', 'updated_at']:
                if subscription.get(date_field):
                    subscription[date_field] = subscription[date_field].isoformat()
            
            # Get plan details
            plan_details = PRICING_PLANS.get(subscription['plan_id'], {})
            subscription['plan_details'] = plan_details
            
            # Calculate usage for current period
            applications_limit = plan_details.get('limits', {}).get('applications_per_month', 0)
            applications_used = subscription.get('applications_used_this_period', 0)
            subscription['usage'] = {
                'applications_used': applications_used,
                'applications_limit': applications_limit,
                'applications_remaining': max(0, applications_limit - applications_used) if applications_limit != "unlimited" else "unlimited"
            }
            
            return jsonify({
                'success': True,
                'subscription': subscription
            })
            
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            return jsonify({'error': 'Unable to fetch subscription details'}), 500
    
    @billing_bp.route('/api/subscription/cancel', methods=['POST'])
    def cancel_subscription():
        """
        Cancel user's subscription
        """
        try:
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            subscription = db.subscriptions.find_one({
                "user_id": session['user_id'],
                "status": {"$in": ["trialing", "active"]}
            })
            
            if not subscription:
                return jsonify({'error': 'No active subscription found'}), 404
            
            # Cancel in Stripe
            stripe.Subscription.modify(
                subscription['stripe_subscription_id'],
                cancel_at_period_end=True
            )
            
            # Update subscription status
            db.subscriptions.update_one(
                {"_id": subscription['_id']},
                {
                    "$set": {
                        "status": "cancelled",
                        "cancelled_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Subscription cancelled successfully. Access will continue until the end of your current billing period.'
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            return jsonify({'error': f'Payment error: {str(e)}'}), 400
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return jsonify({'error': 'Unable to cancel subscription'}), 500
    
    @billing_bp.route('/api/webhook/stripe', methods=['POST'])
    def stripe_webhook():
        """
        Handle Stripe webhooks for subscription updates
        """
        try:
            payload = request.get_data()
            sig_header = request.headers.get('Stripe-Signature')
            endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
            
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            
            # Handle subscription events
            if event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                handle_subscription_updated(db, subscription)
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                handle_subscription_deleted(db, subscription)
            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                handle_payment_succeeded(db, invoice)
            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                handle_payment_failed(db, invoice)
            
            return jsonify({'success': True})
            
        except ValueError as e:
            logger.error(f"Invalid payload in webhook: {str(e)}")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature in webhook: {str(e)}")
            return jsonify({'error': 'Invalid signature'}), 400
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return jsonify({'error': 'Webhook processing failed'}), 500
    
    # Register the blueprint
    app.register_blueprint(billing_bp)
    
    return billing_bp

def handle_subscription_updated(db, stripe_subscription):
    """Handle subscription status updates from Stripe"""
    try:
        db.subscriptions.update_one(
            {"stripe_subscription_id": stripe_subscription['id']},
            {
                "$set": {
                    "status": stripe_subscription['status'],
                    "current_period_start": datetime.fromtimestamp(stripe_subscription['current_period_start']),
                    "current_period_end": datetime.fromtimestamp(stripe_subscription['current_period_end']),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Updated subscription {stripe_subscription['id']} status to {stripe_subscription['status']}")
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")

def handle_subscription_deleted(db, stripe_subscription):
    """Handle subscription cancellation from Stripe"""
    try:
        db.subscriptions.update_one(
            {"stripe_subscription_id": stripe_subscription['id']},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Cancelled subscription {stripe_subscription['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")

def handle_payment_succeeded(db, invoice):
    """Handle successful payment from Stripe"""
    try:
        subscription_id = invoice.get('subscription')
        if subscription_id:
            db.subscriptions.update_one(
                {"stripe_subscription_id": subscription_id},
                {
                    "$set": {
                        "status": "active",
                        "applications_used_this_period": 0,  # Reset usage counter
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Payment succeeded for subscription {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(db, invoice):
    """Handle failed payment from Stripe"""
    try:
        subscription_id = invoice.get('subscription')
        if subscription_id:
            db.subscriptions.update_one(
                {"stripe_subscription_id": subscription_id},
                {
                    "$set": {
                        "status": "past_due",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Payment failed for subscription {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")
        