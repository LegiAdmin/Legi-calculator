from rest_framework import serializers
from succession_engine.models import SimulationScenario, Donation

class SimulationScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationScenario
        fields = ['id', 'name', 'description', 'input_data', 'created_at']
        read_only_fields = ['id', 'created_at']

class DonationSerializer(serializers.ModelSerializer):
    """
    Serializer for Donation model.
    Converts database donations to the format expected by the succession calculator.
    """
    
    class Meta:
        model = Donation
        fields = '__all__'
    
    def to_calculator_format(self):
        """
        Convert Django Donation to Pydantic Donation schema format.
        
        Returns:
            dict: Donation in calculator format
        """
        donation = self.instance
        
        return {
            "id": str(donation.id),
            "donation_type": donation.donation_type,
            "beneficiary_id": str(donation.beneficiary_heir_id) if donation.beneficiary_heir_id else donation.beneficiary_name,
            "donation_date": donation.donation_date.isoformat(),
            "original_value": float(donation.original_value),
            "current_value": float(donation.current_estimated_value) if donation.current_estimated_value else float(donation.original_value),
            "is_reportable": donation.donation_type == "DON_MANUEL",  # Only DON_MANUEL is reportable
            "description": donation.description,
            "notary_act_reference": donation.notary_act_reference,
        }

def get_user_donations_for_calculator(user_id):
    """
    Helper function to get all donations for a user in calculator format.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        list: List of donations in calculator format
    """
    donations = Donation.objects.filter(user_id=user_id)
    return [DonationSerializer(d).to_calculator_format() for d in donations]
