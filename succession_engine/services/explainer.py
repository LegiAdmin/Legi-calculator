"""
ExplainerService - Decouples calculation logic from presentation

This service enriches calculation output with explanations from the rule dictionary,
enabling separation of concerns between business logic and user-facing content.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ExplainerService:
    """
    Service that enriches calculation steps with human-readable explanations.
    
    Decoupling Pattern:
    - Calculator returns rule_ids (e.g., "RULE_RESERVE_2_CHILDREN")
    - ExplainerService maps rule_ids to full explanations (what, why, legal_basis)
    
    Benefits:
    - Change explanations without touching calculation code
    - Support multiple languages (future)
    - Reduce regression risk when updating text
    """
    
    _instance = None
    _dictionary = None
    
    def __new__(cls):
        """Singleton pattern - dictionary loaded once"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_dictionary()
        return cls._instance
    
    @classmethod
    def _load_dictionary(cls, language: str = "fr") -> None:
        """Load rule dictionary from JSON file."""
        dict_path = Path(__file__).parent.parent / "data" / "rule_dictionary.json"
        
        if not dict_path.exists():
            cls._dictionary = {"rules": {}, "exclusion_reasons": {}}
            return
        
        with open(dict_path, "r", encoding="utf-8") as f:
            cls._dictionary = json.load(f)
    
    @classmethod
    def reload_dictionary(cls) -> None:
        """Force reload of dictionary (useful after updates)."""
        cls._load_dictionary()
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a single rule by ID."""
        return self._dictionary.get("rules", {}).get(rule_id)
    
    def get_exclusion_reason(self, reason_id: str) -> str:
        """Get human-readable exclusion reason."""
        return self._dictionary.get("exclusion_reasons", {}).get(reason_id, reason_id)
    
    def enrich_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a calculation step with explanations from rule dictionary.
        
        Input step format:
        {
            "step_number": 1,
            "step_name": "Liquidation",
            "description": "...",
            "result_summary": "...",
            "rule_ids": ["RULE_REGIME_COMMUNAUTE_REDUITE"],  # NEW: list of applied rules
            "excluded_rule_ids": [{"rule_id": "RULE_PRECIPUT", "reason": "NOT_APPLICABLE"}]  # NEW
        }
        
        Output format (enriched):
        {
            "step_number": 1,
            "step_name": "Liquidation",
            "description": "...",
            "result_summary": "...",
            "what": "Application du régime légal...",
            "why": "Les biens acquis pendant le mariage...",
            "legal_basis": ["Art. 1400-1491 Code civil"],
            "applied_rules": [...],
            "excluded_rules": [...]
        }
        """
        enriched = step.copy()
        
        # Extract and enrich applied rules
        rule_ids = step.get("rule_ids", [])
        applied_rules = []
        
        # Aggregate what/why/legal_basis from all applied rules
        whats = []
        whys = []
        legal_bases = []
        
        for rule_id in rule_ids:
            rule = self.get_rule(rule_id)
            if rule:
                applied_rules.append({
                    "rule_id": rule_id,
                    "what": rule.get("what", ""),
                    "why": rule.get("why", ""),
                    "legal_basis": rule.get("legal_basis", [])
                })
                whats.append(rule.get("what", ""))
                whys.append(rule.get("why", ""))
                legal_bases.extend(rule.get("legal_basis", []))
        
        # Set aggregated explanations
        if whats:
            enriched["what"] = whats[0] if len(whats) == 1 else " | ".join(whats)
        if whys:
            enriched["why"] = whys[0] if len(whys) == 1 else " | ".join(whys)
        if legal_bases:
            enriched["legal_basis"] = list(set(legal_bases))  # Deduplicate
        
        enriched["applied_rules"] = applied_rules
        
        # Enrich excluded rules
        excluded_rule_data = step.get("excluded_rule_ids", [])
        excluded_rules = []
        
        for excl in excluded_rule_data:
            rule_id = excl.get("rule_id", "")
            reason_id = excl.get("reason", "")
            rule = self.get_rule(rule_id)
            
            excluded_rules.append({
                "rule_id": rule_id,
                "rule_name": rule.get("what", rule_id) if rule else rule_id,
                "reason": self.get_exclusion_reason(reason_id),
                "explanation": excl.get("explanation", "")
            })
        
        if excluded_rules:
            enriched["excluded_rules"] = excluded_rules
        
        # Clean up intermediate fields
        enriched.pop("rule_ids", None)
        enriched.pop("excluded_rule_ids", None)
        
        return enriched
    
    def enrich_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich full calculation output.
        
        Enriches all calculation_steps with explanations from dictionary.
        """
        enriched_output = output.copy()
        
        steps = enriched_output.get("calculation_steps", [])
        enriched_steps = [self.enrich_step(step) for step in steps]
        enriched_output["calculation_steps"] = enriched_steps
        
        return enriched_output
    
    def enrich_heir_decisions(self, decisions: List[Dict]) -> List[Dict]:
        """
        Enrich heir inclusion/exclusion decisions.
        
        Input:
        [{"id": "child1", "type": "INCLUDED", "rule_id": "RULE_CHILD_HEIR"}]
        
        Output:
        [{"id": "child1", "type": "INCLUDED", "subject": "child1", 
          "reason": "Enfant identifié comme héritier du 1er ordre"}]
        """
        enriched = []
        for decision in decisions:
            rule_id = decision.get("rule_id", "")
            rule = self.get_rule(rule_id)
            
            enriched.append({
                "id": decision.get("id", ""),
                "type": decision.get("type", ""),
                "subject": decision.get("id", ""),
                "reason": rule.get("what", "") if rule else decision.get("reason", ""),
                "legal_basis": rule.get("legal_basis", []) if rule else []
            })
        
        return enriched


# Singleton instance for easy access
explainer = ExplainerService()
