"""
Script to create Django migrations for the Donation model.
Run this after adding the Donation model to models.py
"""

import os
import sys

# Add project to path
sys.path.insert(0, '/Users/evanmounaud/Documents/Antigravity')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

print("✅ Django setup complete")
print("\n📝 To create migrations for Donation model, run:")
print("   python manage.py makemigrations succession_engine")
print("\n📝 Then apply migrations:")
print("   python manage.py migrate")
print("\n💡 Note: The Donation model is configured to use the existing 'donations' table")
print("   with db_table = 'donations', so it won't create a new table.")
