"""
Test script to verify Donation model integration.
"""

import os
import sys
import django

sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from succession_engine.models import Donation
from succession_engine.api.serializers import get_user_donations_for_calculator
import uuid

print("🧪 Testing Donation Model Integration\n")

# Check if table exists and has data
try:
    donation_count = Donation.objects.count()
    print(f"✅ Donation model connected to database")
    print(f"📊 Total donations in DB: {donation_count}\n")
    
    if donation_count > 0:
        # Show first donation
        first_donation = Donation.objects.first()
        print(f"📋 Example donation:")
        print(f"   Type: {first_donation.donation_type}")
        print(f"   Beneficiary: {first_donation.beneficiary_name}")
        print(f"   Value: {first_donation.original_value}€")
        print(f"   Date: {first_donation.donation_date}")
        
        # Test serializer
        print(f"\n🔄 Testing serializer conversion:")
        from succession_engine.api.serializers import DonationSerializer
        serializer = DonationSerializer(first_donation)
        calculator_format = serializer.to_calculator_format()
        print(f"   Calculator format: {calculator_format}")
        
        # Test helper function
        print(f"\n🔍 Testing get_user_donations_for_calculator:")
        user_donations = get_user_donations_for_calculator(first_donation.user_id)
        print(f"   Found {len(user_donations)} donation(s) for user {first_donation.user_id}")
        
    else:
        print("⚠️  No donations in database yet")
        print("💡 You can add donations via the admin or API")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Make sure to run migrations first:")
    print("   python manage.py migrate")
