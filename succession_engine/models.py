from django.db import models
from django.utils.translation import gettext_lazy as _

class Legislation(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. 'Loi Finances 2024'")
    year = models.IntegerField(default=2024)
    is_active = models.BooleanField(default=False, help_text="Only one legislation should be active at a time.")

    def __str__(self):
        return f"{self.name} ({self.year})"

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate others
            Legislation.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class TaxBracket(models.Model):
    legislation = models.ForeignKey(Legislation, on_delete=models.CASCADE, related_name='tax_brackets')
    relationship = models.CharField(max_length=50, choices=[
        ('CHILD', 'Child/Parent'),
        ('SIBLING', 'Sibling'),
        ('OTHER', 'Other')
    ], default='CHILD')
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Leave empty for infinity")
    rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="e.g. 0.05 for 5%")

    class Meta:
        ordering = ['min_amount']

    def __str__(self):
        return f"{self.relationship} [{self.min_amount} - {self.max_amount or 'Inf'}] : {self.rate*100}%"

class Allowance(models.Model):
    legislation = models.ForeignKey(Legislation, on_delete=models.CASCADE, related_name='allowances')
    relationship = models.CharField(max_length=50, choices=[
        ('CHILD', 'Child/Parent'),
        ('SIBLING', 'Sibling'),
        ('OTHER', 'Other'), # Nephews, etc.
        ('SPOUSE', 'Spouse/Partner')
    ])
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.relationship}: {self.amount}€"

class UsufructScale(models.Model):
    legislation = models.ForeignKey(Legislation, on_delete=models.CASCADE, related_name='usufruct_scales')
    max_age = models.IntegerField()
    rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="e.g. 0.9 for 90%")

    class Meta:
        ordering = ['max_age']

    def __str__(self):
        return f"< {self.max_age} ans : {self.rate*100}%"

class SimulationScenario(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    input_data = models.JSONField(help_text="The SimulationInput JSON payload")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Donation(models.Model):
    """
    Donation model matching the database schema.
    Represents donations made by the deceased to heirs.
    """
    id = models.UUIDField(primary_key=True, default=models.UUIDField().default)
    user_id = models.UUIDField()
    donation_type = models.CharField(max_length=50)  # DON_MANUEL, DONATION_PARTAGE, PRESENT_USAGE
    beneficiary_name = models.CharField(max_length=200)
    beneficiary_heir_id = models.UUIDField(null=True, blank=True)
    beneficiary_relationship = models.CharField(max_length=50, null=True, blank=True)
    donation_date = models.DateField()
    description = models.TextField()
    purpose = models.TextField(null=True, blank=True)
    
    # Valeurs
    original_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Déclaration fiscale
    is_declared_to_tax = models.BooleanField(default=False, null=True, blank=True)
    tax_declaration_date = models.DateField(null=True, blank=True)
    
    # Détails immobilier (si applicable)
    property_address = models.TextField(null=True, blank=True)
    occupation_duration_months = models.IntegerField(null=True, blank=True)
    monthly_rental_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Détails prêt (si applicable)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount_repaid = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    
    # Assurance-vie (si applicable)
    insurance_contract_reference = models.TextField(null=True, blank=True)
    premium_amount_after_70 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Acte notarié
    notary_act_reference = models.TextField(null=True, blank=True)
    notary_signature_date = models.DateField(null=True, blank=True)
    notary_name = models.TextField(null=True, blank=True)
    notary_city = models.TextField(null=True, blank=True)
    notary_details_unknown = models.BooleanField(default=False, null=True, blank=True)
    notary_search_hint = models.TextField(null=True, blank=True)
    
    # Flags
    current_value_unknown = models.BooleanField(default=False, null=True, blank=True)
    
    # Notes
    notes = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donations'
        
    def __str__(self):
        return f"{self.donation_type} - {self.beneficiary_name} ({self.donation_date})"
