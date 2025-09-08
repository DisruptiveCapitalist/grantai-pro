# config/pricing_plans.py
"""
Updated Pricing Structure for GrantAI Pro
Includes Premium tier and promo code system
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# Updated Pricing Plans
PRICING_PLANS = {
    "personal": {
        "name": "Personal",
        "description": "For individual grant writers and small nonprofits",
        "monthly_price": 97,
        "annual_price": 78,  # 20% discount
        "features": [
            "15 AI applications per month",
            "Basic competitive intelligence", 
            "Grant discovery & alerts",
            "Email support",
            "Success tracking",
            "Award reporting"
        ],
        "limits": {
            "applications_per_month": 15,
            "users": 1,
            "competitive_intelligence": "basic"
        }
    },
    "professional": {
        "name": "Professional", 
        "description": "For organizations applying to multiple grants",
        "monthly_price": 197,
        "annual_price": 158,  # 20% discount
        "features": [
            "50 AI applications per month",
            "Full competitive intelligence",
            "Success probability scoring",
            "Award tracking & verification", 
            "Priority support",
            "Advanced analytics",
            "POC contact recommendations"
        ],
        "limits": {
            "applications_per_month": 50,
            "users": 1,
            "competitive_intelligence": "full"
        },
        "popular": True
    },
    "premium": {
        "name": "Premium",
        "description": "Full grant writing service with strategic guidance",
        "monthly_price": 497,
        "annual_price": 398,  # 20% discount
        "features": [
            "Everything in Professional",
            "GrantAI writes full applications",
            "8,000+ grant success pattern analysis",
            "Strategic POC consultation scripts",
            "Priority application review",
            "Dedicated success manager",
            "Industry-specific templates",
            "Failure pattern analysis"
        ],
        "limits": {
            "applications_per_month": 100,
            "users": 1,
            "competitive_intelligence": "full",
            "full_writing_service": True
        },
        "premium": True
    },
    "team": {
        "name": "Team",
        "description": "For organizations with multiple grant writers",
        "monthly_price": 297,  # per user
        "annual_price": 238,   # per user, 20% discount
        "features": [
            "Everything in Premium",
            "Team collaboration features",
            "Shared grant libraries", 
            "Role-based permissions",
            "Team performance analytics",
            "Admin dashboard",
            "Bulk application management"
        ],
        "limits": {
            "applications_per_month": 100,  # per user
            "users": "unlimited",
            "minimum_users": 3,
            "competitive_intelligence": "full",
            "full_writing_service": True
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "For large organizations and consultants",
        "monthly_price": 997,  # per user
        "annual_price": 798,   # per user, 20% discount
        "features": [
            "Everything in Team",
            "Unlimited AI applications",
            "API access & integrations",
            "Custom AI training",
            "White-label options", 
            "Dedicated account manager",
            "Custom reporting",
            "SLA guarantees"
        ],
        "limits": {
            "applications_per_month": "unlimited",
            "users": "unlimited",
            "minimum_users": 1,
            "competitive_intelligence": "full",
            "full_writing_service": True,
            "api_access": True,
            "white_label": True
        }
    }
}

# Promo Code System
PROMO_CODES = {
    "BETA50": {
        "name": "Beta User Lifetime Discount",
        "discount_type": "percentage",
        "discount_value": 50,
        "duration": "lifetime",
        "max_uses": 50,
        "valid_until": None,  # No expiration
        "applicable_plans": ["professional", "premium", "team", "enterprise"],
        "description": "50% off for life - Beta user exclusive",
        "active": True
    },
    "FOUNDER25": {
        "name": "Founder's Discount",
        "discount_type": "percentage", 
        "discount_value": 25,
        "duration": "months",
        "duration_months": 12,
        "max_uses": 100,
        "valid_until": datetime.utcnow() + timedelta(days=90),
        "applicable_plans": ["professional", "premium", "team", "enterprise"],
        "description": "25% off first year",
        "active": True
    },
    "LAUNCH2025": {
        "name": "Launch Special",
        "discount_type": "percentage",
        "discount_value": 50, 
        "duration": "months",
        "duration_months": 6,
        "max_uses": 200,
        "valid_until": datetime.utcnow() + timedelta(days=60),
        "applicable_plans": ["personal", "professional", "premium"],
        "description": "50% off first 6 months",
        "active": True
    },
    "NONPROFIT20": {
        "name": "Nonprofit Discount",
        "discount_type": "percentage",
        "discount_value": 20,
        "duration": "lifetime",
        "max_uses": 500,
        "valid_until": None,
        "applicable_plans": ["personal", "professional", "premium"],
        "description": "20% off for verified nonprofits",
        "active": True,
        "requires_verification": True
    }
}

class PricingCalculator:
    """Calculate pricing with promo codes and discounts"""
    
    def __init__(self, db):
        self.db = db
    
    def get_plan_price(self, plan_id: str, billing_cycle: str = "monthly", 
                      promo_code: str = None, users: int = 1) -> Dict:
        """
        Calculate final price for a plan with optional promo code
        """
        try:
            if plan_id not in PRICING_PLANS:
                raise ValueError(f"Invalid plan: {plan_id}")
            
            plan = PRICING_PLANS[plan_id]
            
            # Base price calculation
            if billing_cycle == "annual":
                base_price = plan["annual_price"]
            else:
                base_price = plan["monthly_price"]
            
            # Handle per-user pricing for team/enterprise
            if plan_id in ["team", "enterprise"]:
                min_users = plan["limits"].get("minimum_users", 1)
                users = max(users, min_users)
                base_price = base_price * users
            
            result = {
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "billing_cycle": billing_cycle,
                "users": users,
                "base_price": base_price,
                "discount_amount": 0,
                "final_price": base_price,
                "promo_code": promo_code,
                "discount_description": None,
                "savings_vs_monthly": 0
            }
            
            # Calculate annual savings
            if billing_cycle == "annual":
                monthly_equivalent = plan["monthly_price"] * 12
                if plan_id in ["team", "enterprise"]:
                    monthly_equivalent = monthly_equivalent * users
                result["savings_vs_monthly"] = monthly_equivalent - base_price
            
            # Apply promo code if provided
            if promo_code:
                promo_result = self.apply_promo_code(promo_code, plan_id, base_price)
                if promo_result["valid"]:
                    result.update({
                        "discount_amount": promo_result["discount_amount"],
                        "final_price": promo_result["final_price"],
                        "discount_description": promo_result["description"]
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            raise
    
    def apply_promo_code(self, promo_code: str, plan_id: str, base_price: float) -> Dict:
        """
        Apply promo code and return discount details
        """
        try:
            promo_code = promo_code.upper().strip()
            
            if promo_code not in PROMO_CODES:
                return {"valid": False, "error": "Invalid promo code"}
            
            promo = PROMO_CODES[promo_code]
            
            # Check if promo is active
            if not promo.get("active", False):
                return {"valid": False, "error": "Promo code is inactive"}
            
            # Check if plan is applicable
            if plan_id not in promo.get("applicable_plans", []):
                return {"valid": False, "error": "Promo code not valid for this plan"}
            
            # Check expiration
            if promo.get("valid_until") and datetime.utcnow() > promo["valid_until"]:
                return {"valid": False, "error": "Promo code has expired"}
            
            # Check usage limit
            current_uses = self.get_promo_code_usage(promo_code)
            if current_uses >= promo.get("max_uses", float('inf')):
                return {"valid": False, "error": "Promo code usage limit reached"}
            
            # Calculate discount
            if promo["discount_type"] == "percentage":
                discount_amount = base_price * (promo["discount_value"] / 100)
            else:  # fixed amount
                discount_amount = min(promo["discount_value"], base_price)
            
            final_price = max(0, base_price - discount_amount)
            
            return {
                "valid": True,
                "discount_amount": discount_amount,
                "final_price": final_price,
                "description": promo["description"],
                "duration": promo.get("duration"),
                "duration_months": promo.get("duration_months")
            }
            
        except Exception as e:
            logger.error(f"Error applying promo code: {str(e)}")
            return {"valid": False, "error": "Error processing promo code"}
    
    def get_promo_code_usage(self, promo_code: str) -> int:
        """
        Get current usage count for a promo code
        """
        try:
            count = self.db.subscriptions.count_documents({
                "promo_code": promo_code.upper()
            })
            return count
        except Exception as e:
            logger.error(f"Error getting promo usage: {str(e)}")
            return 0
    
    def validate_promo_code(self, promo_code: str, plan_id: str) -> Dict:
        """
        Validate promo code without applying it
        """
        try:
            result = self.apply_promo_code(promo_code, plan_id, 100)  # Test with $100
            return {
                "valid": result["valid"],
                "error": result.get("error"),
                "description": result.get("description"),
                "discount_value": PROMO_CODES.get(promo_code.upper(), {}).get("discount_value"),
                "discount_type": PROMO_CODES.get(promo_code.upper(), {}).get("discount_type")
            }
        except Exception as e:
            logger.error(f"Error validating promo code: {str(e)}")
            return {"valid": False, "error": "Error validating promo code"}

def get_plan_comparison() -> List[Dict]:
    """
    Get formatted plan comparison for pricing page
    """
    plans = []
    for plan_id, plan_data in PRICING_PLANS.items():
        plan_info = {
            "id": plan_id,
            "name": plan_data["name"],
            "description": plan_data["description"],
            "monthly_price": plan_data["monthly_price"],
            "annual_price": plan_data["annual_price"],
            "features": plan_data["features"],
            "popular": plan_data.get("popular", False),
            "premium": plan_data.get("premium", False),
            "per_user": plan_id in ["team", "enterprise"],
            "minimum_users": plan_data["limits"].get("minimum_users"),
            "cta_text": "Contact Sales" if plan_id == "enterprise" else "Start 7-Day Trial"
        }
        
        # Calculate savings
        monthly_annual = plan_data["monthly_price"] * 12
        annual_savings = monthly_annual - plan_data["annual_price"]
        plan_info["annual_savings"] = annual_savings
        plan_info["savings_percentage"] = round((annual_savings / monthly_annual) * 100)
        
        plans.append(plan_info)
    
    return plans

# Legal disclaimers
LEGAL_DISCLAIMERS = {
    "no_guarantee": "No guarantee of grant award success. Results based on historical patterns, not future promises.",
    "agency_independence": "Grant decisions are made by funding agencies, not GrantAI Pro. Success rates vary by industry, agency, and application quality.",
    "user_responsibility": "User is responsible for accuracy of all submitted information and compliance with grant requirements.",
    "service_nature": "GrantAI Pro provides tools and guidance. Final application review and submission remain user's responsibility.",
    "pattern_analysis": "Success patterns based on analysis of 8,000+ historical grants. Past performance does not guarantee future results."
}

def get_legal_disclaimers() -> Dict:
    """Get legal disclaimers for display"""
    return LEGAL_DISCLAIMERS
