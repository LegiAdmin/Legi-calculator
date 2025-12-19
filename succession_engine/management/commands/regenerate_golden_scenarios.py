"""
Regenerate Golden Scenarios - Snapshot Testing Command

This command regenerates the expected_output fields in golden_scenarios.json
by running the calculator and comparing results.

ARCHITECTURE NOTE (Critique #3 - Maintenance):
- Provides dry-run mode to preview changes
- Requires human validation before applying
- Shows colored diff for easy review
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import termcolors


class Command(BaseCommand):
    help = 'Regenerate expected_output in golden_scenarios.json from current calculator'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without applying',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply changes after confirmation',
        )
        parser.add_argument(
            '--scenario',
            type=str,
            help='Regenerate only a specific scenario ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Apply without confirmation (use with caution)',
        )

    def handle(self, *args, **options):
        from succession_engine.core.calculator import SuccessionCalculator
        from succession_engine.schemas import SimulationInput
        
        scenarios_path = Path(__file__).resolve().parent.parent.parent.parent / 'tests' / 'golden_scenarios.json'
        
        if not scenarios_path.exists():
            raise CommandError(f'File not found: {scenarios_path}')
        
        # Load scenarios
        with open(scenarios_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scenarios = data.get('scenarios', [])
        calculator = SuccessionCalculator()
        
        changes = []
        errors = []
        
        for scenario in scenarios:
            sid = scenario['id']
            
            # Filter if specific scenario requested
            if options['scenario'] and options['scenario'] != sid:
                continue
            
            try:
                # Parse input
                input_data = SimulationInput(**scenario['input'])
                
                # Run calculator
                result = calculator.run(input_data)
                
                # Extract key fields for expected_output
                new_expected = self._extract_expected(result)
                old_expected = scenario.get('expected_output', {})
                
                # Compare
                diff = self._compute_diff(old_expected, new_expected, sid)
                
                if diff:
                    changes.append({
                        'scenario': scenario,
                        'old': old_expected,
                        'new': new_expected,
                        'diff': diff
                    })
                    
            except Exception as e:
                errors.append({'id': sid, 'error': str(e)})
        
        # Show results
        if errors:
            self.stderr.write(self.style.ERROR(f'\n❌ {len(errors)} erreur(s):'))
            for err in errors:
                self.stderr.write(f"  - {err['id']}: {err['error']}")
        
        if not changes:
            self.stdout.write(self.style.SUCCESS('\n✅ Aucun changement détecté'))
            return
        
        # Show changes
        self.stdout.write(self.style.WARNING(f'\n📊 {len(changes)} scénario(s) avec différences:\n'))
        
        for change in changes:
            self._print_diff(change)
        
        # Apply if requested
        if options['apply']:
            if not options['force']:
                confirm = input('\n⚠️  Appliquer ces changements ? (oui/non): ')
                if confirm.lower() != 'oui':
                    self.stdout.write(self.style.NOTICE('Annulé.'))
                    return
            
            # Apply changes
            for change in changes:
                scenario = change['scenario']
                scenario['expected_output'] = change['new']
                scenario['validation'] = {
                    'status': 'REGENERATED',
                    'notes': 'Auto-régénéré par commande, à valider manuellement'
                }
            
            # Save
            with open(scenarios_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ {len(changes)} scénario(s) mis à jour'))
            self.stdout.write(self.style.WARNING('⚠️  N\'oubliez pas de valider manuellement les changements!'))
        
        elif not options['dry_run']:
            self.stdout.write(self.style.NOTICE(
                '\nUtilisez --apply pour appliquer ou --dry-run pour prévisualiser'
            ))

    def _extract_expected(self, result) -> dict:
        """Extract key fields from result for expected_output."""
        expected = {}
        
        # Global metrics
        if hasattr(result, 'global_metrics'):
            gm = result.global_metrics
            expected['total_estate_value'] = round(gm.total_estate_value, 2)
            expected['total_tax_amount'] = round(gm.total_tax_amount, 2)
        
        # Heirs breakdown
        if hasattr(result, 'heirs_breakdown'):
            expected['heirs_breakdown'] = []
            for heir in result.heirs_breakdown:
                heir_data = {'id': heir.id}
                
                if hasattr(heir, 'legal_share_percent') and heir.legal_share_percent:
                    heir_data['legal_share_percent'] = round(heir.legal_share_percent, 2)
                if hasattr(heir, 'gross_share_value') and heir.gross_share_value:
                    heir_data['gross_share_value'] = round(heir.gross_share_value, 2)
                if hasattr(heir, 'abatement_used') and heir.abatement_used:
                    heir_data['abatement_used'] = round(heir.abatement_used, 2)
                if hasattr(heir, 'taxable_base') and heir.taxable_base:
                    heir_data['taxable_base'] = round(heir.taxable_base, 2)
                if hasattr(heir, 'tax_amount') and heir.tax_amount is not None:
                    heir_data['tax_amount'] = round(heir.tax_amount, 2)
                
                expected['heirs_breakdown'].append(heir_data)
        
        return expected

    def _compute_diff(self, old: dict, new: dict, sid: str) -> list:
        """Compute differences between old and new expected output."""
        diffs = []
        
        # Compare numeric fields
        for key in ['total_estate_value', 'total_tax_amount']:
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                diffs.append({
                    'field': key,
                    'old': old_val,
                    'new': new_val
                })
        
        # Compare heirs
        old_heirs = {h['id']: h for h in old.get('heirs_breakdown', [])}
        new_heirs = {h['id']: h for h in new.get('heirs_breakdown', [])}
        
        all_heir_ids = set(old_heirs.keys()) | set(new_heirs.keys())
        
        for heir_id in all_heir_ids:
            old_h = old_heirs.get(heir_id, {})
            new_h = new_heirs.get(heir_id, {})
            
            for key in ['legal_share_percent', 'gross_share_value', 'abatement_used', 'taxable_base', 'tax_amount']:
                old_val = old_h.get(key)
                new_val = new_h.get(key)
                if old_val != new_val:
                    diffs.append({
                        'field': f'{heir_id}.{key}',
                        'old': old_val,
                        'new': new_val
                    })
        
        return diffs

    def _print_diff(self, change: dict):
        """Print a colored diff for a scenario change."""
        scenario = change['scenario']
        self.stdout.write(f"\n📋 {scenario['id']} - {scenario['name']}")
        self.stdout.write('-' * 50)
        
        for diff in change['diff']:
            old_str = f"{diff['old']}" if diff['old'] is not None else "—"
            new_str = f"{diff['new']}" if diff['new'] is not None else "—"
            
            self.stdout.write(f"  {diff['field']}:")
            self.stdout.write(self.style.ERROR(f"    - {old_str}"))
            self.stdout.write(self.style.SUCCESS(f"    + {new_str}"))
