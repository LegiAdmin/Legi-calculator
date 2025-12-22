import sys
import os
from datetime import date

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Set DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from succession_engine.core.calculator import SuccessionCalculator
from succession_engine.schemas import (
    SimulationInput, Asset, FamilyMember, Wishes, SpecificBequest,
    MatrimonialRegime, HeirRelation, OwnershipMode, AssetOrigin,
    AcceptanceOption
)

def reproduce():
    # Setup
    assets = [
        Asset(
            id="maison",
            estimated_value=200000,
            ownership_mode=OwnershipMode.FULL_OWNERSHIP,
            asset_origin=AssetOrigin.PERSONAL_PROPERTY
        ),
        Asset(
            id="cash",
            estimated_value=100000,
            ownership_mode=OwnershipMode.FULL_OWNERSHIP,
            asset_origin=AssetOrigin.PERSONAL_PROPERTY
        )
    ]
    
    members = [
        FamilyMember(
            id="childA",
            birth_date=date(1990, 1, 1),
            relationship=HeirRelation.CHILD
        ),
        FamilyMember(
            id="childB",
            birth_date=date(1992, 1, 1),
            relationship=HeirRelation.CHILD
        )
    ]
    
    # Bequest: "cash" (100k) given to "childA"
    wishes = Wishes(
        specific_bequests=[
            SpecificBequest(
                asset_id="cash",
                beneficiary_id="childA",
                share_percentage=100.0
            )
        ]
    )
    
    input_data = SimulationInput(
        matrimonial_regime=MatrimonialRegime.SEPARATION,
        assets=assets,
        members=members,
        wishes=wishes
    )
    
    print("--- RUNNING CALCULATOR ---")
    calc = SuccessionCalculator()
    result = calc.run(input_data)
    
    print(f"Total Estate Value: {result.global_metrics.total_estate_value}")
    
    for heir in result.heirs_breakdown:
        print(f"Heir: {heir.id}")
        print(f"  Legal Share Percent: {heir.legal_share_percent}%")
        print(f"  Gross Share Value: {heir.gross_share_value}")
        print(f"  Heir Effective Share Percent: {heir.effective_share_percent:.2f}%")
        print(f"  Received Assets: {[a.asset_id for a in heir.received_assets]}")

    print("\n--- NEW EXPLICABILITY UX ---")
    for step in result.calculation_steps:
        print(f"\n[STEP {step.step_number}] {step.step_id}")
        if step.pedagogy:
            print(f"  📖 TITLE: {step.pedagogy.title}")
            print(f"  📖 DEFINITION: {step.pedagogy.definition}")
            print(f"  📖 WHY: {step.pedagogy.why_it_matters}")
        
        if step.calculation:
            print(f"  ⚙️ CALC: {step.calculation.description}")
            if step.calculation.formula:
                 print(f"  📐 FORMULA: {step.calculation.formula}")
            for sub in step.calculation.sub_steps:
                print(f"     -> {sub}")

        if step.insights:
            for insight in step.insights:
                print(f"  💡 INSIGHT [{insight.type.value}]: {insight.message}")
        
        # Print per-heir blocks (Human-First design)
        if step.heir_blocks:
            print(f"\n  👥 DÉTAIL PAR HÉRITIER:")
            for hb in step.heir_blocks:
                print(f"  ┌── {hb.heir_name} ({hb.relationship})")
                print(f"  │   📝 {hb.narrative}")
                print(f"  │   Part brute: {hb.gross_share} | Abattement: {hb.abatement} | Taxable: {hb.taxable_base}")
                print(f"  └── 💰 Droits: {hb.tax_result}")
                if hb.bracket_details:
                    for bd in hb.bracket_details:
                        print(f"       • {bd}")

if __name__ == "__main__":
    reproduce()
