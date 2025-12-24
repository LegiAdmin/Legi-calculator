from typing import List, Dict, Optional, Any
from succession_engine.schemas import CalculationStep, CalculationDecision, DecisionType, HeirExplicabilityBlock

class BusinessLogicTracer:
    """
    Helper to trace business logic execution for user explicability.
    Collects structured pedagogical steps, calculations, and insights.
    Human-First Design: per-heir blocks with plain French narratives.
    """
    def __init__(self):
        self.steps: List[CalculationStep] = []
        self.current_step: Optional[CalculationStep] = None
        
        # Load static content
        from succession_engine.core.educational_content import EDUCATIONAL_CONTENT
        self.content_db = EDUCATIONAL_CONTENT

    def start_step_pedagogical(self, step_number: int, step_id: str) -> None:
        """Begin a new structured calculation step."""
        # Retrieve static content for this step ID
        content = self.content_db.get(step_id, {
            "title": f"Step {step_number}",
            "definition": "N/A",
            "why_it_matters": "N/A",
            "legal_references": []
        })
        
        from succession_engine.schemas import PedagogicalContent, CalculationBlock
        
        self.current_step = CalculationStep(
            step_number=step_number,
            step_id=step_id,
            pedagogy=PedagogicalContent(**content),
            calculation=CalculationBlock(
                description="Initialisation...", 
                sub_steps=[]
            ),
            inputs={},
            outputs={},
            insights=[],
            heir_blocks=[]
        )
        self.steps.append(self.current_step)

    # Alias for backward compatibility during refactor, maps old calls to new
    def start_step(self, step_number: int, step_name: str, description: str) -> None:
        # Infer ID from name or number (Temporary bridge)
        if step_number == 1: sid = "LIQUIDATION"
        elif step_number == 2: sid = "RECONSTITUTION"
        elif step_number == 3: sid = "DEVOLUTION"
        elif step_number == 4: sid = "FISCAL"
        else: sid = "UNKNOWN"
        
        self.start_step_pedagogical(step_number, sid)

    def record_calculation(self, description: str, formula: Optional[str] = None) -> None:
        """Update the technical calculation block."""
        if self.current_step:
            self.current_step.calculation.description = description
            if formula:
                self.current_step.calculation.formula = formula

    def add_sub_step(self, description: str) -> None:
        """Add a granular operation to the calculation block."""
        if self.current_step:
            self.current_step.calculation.sub_steps.append(description)

    def add_insight(self, type: str, message: str) -> None:
        """Add a smart insight (Positive/Warning/Edu)."""
        if self.current_step:
            from succession_engine.schemas import KeyInsight, InsightType
            try:
                itype = InsightType(type)
            except ValueError:
                itype = InsightType.EDUCATIONAL
                
            self.current_step.insights.append(KeyInsight(type=itype, message=message))

    # --- Human-First: Per-Heir Explicability Blocks ---

    def add_heir_block(
        self,
        heir_id: str,
        heir_name: str,
        relationship: str,
        gross_share: float,
        abatement: float,
        taxable_base: float,
        tax_amount: float,
        bracket_details: List[str] = None
    ) -> None:
        """
        Add a self-contained explicability block for one heir's fiscal calculation.
        Generates a plain French narrative automatically.
        """
        if not self.current_step:
            return
        
        # Format values in plain French
        def fmt(val: float) -> str:
            return f"{val:,.0f} €".replace(",", " ")
        
        gross_str = fmt(gross_share)
        abat_str = fmt(abatement)
        tax_str = fmt(taxable_base)
        result_str = fmt(tax_amount) if tax_amount > 0 else "0 € (exonéré)"
        
        # Fix 3: Special handling for spouse exoneration
        is_spouse = relationship.upper() in ["SPOUSE", "PARTNER"]
        
        if is_spouse:
            # Spouse is fully exempt (Art. 796-0 bis CGI)
            abat_str = "Exonération totale"
            narrative = f"{heir_name} est exonéré(e) de droits de succession en tant que conjoint survivant (Art. 796-0 bis CGI). "
            narrative += f"Part reçue : {gross_str}. Aucun impôt."
            result_str = "0 € (conjoint exonéré)"
        elif taxable_base > 0:
            # Build plain French narrative
            narrative = f"{heir_name} reçoit une part brute de {gross_str}. "
            narrative += f"Après application de l'abattement de {abat_str}, "
            narrative += f"une part de {tax_str} est soumise au barème progressif. "
            narrative += f"Droits à payer : {fmt(tax_amount)}."
        else:
            narrative = f"{heir_name} reçoit une part brute de {gross_str}. "
            narrative += f"L'abattement de {abat_str} couvre l'intégralité de sa part. "
            narrative += "Aucun droit de succession à payer."
        
        block = HeirExplicabilityBlock(
            heir_id=heir_id,
            heir_name=heir_name,
            relationship=relationship,
            gross_share=gross_str,
            abatement=abat_str,
            taxable_base=tax_str,
            narrative=narrative,
            tax_result=result_str,
            bracket_details=bracket_details or []
        )
        
        self.current_step.heir_blocks.append(block)

    # --- Legacy methods adapted to new schema ---

    def explain(self, what: str = None, why: str = None) -> None:
        # Mapped to calculation description or ignored if redundancy
        pass 

    def end_step(self, result_summary: str) -> None:
        # Optional: could add summary as an output or insight
        pass

    def add_input(self, key: str, value: Any) -> None:
        """Detail a specific input value used in this step."""
        if self.current_step:
            if isinstance(value, float):
                val_str = f"{value:,.0f} €".replace(",", " ")
            else:
                val_str = str(value)
            self.current_step.inputs[key] = val_str

    def add_output(self, key: str, value: Any) -> None:
        """Detail a specific output value calculated in this step."""
        if self.current_step:
            if isinstance(value, float):
                val_str = f"{value:,.0f} €".replace(",", " ")
            else:
                val_str = str(value)
            self.current_step.outputs[key] = val_str

    def add_decision(self, type: str, description: str, reason: Optional[str] = None) -> None:
        """Map old decisions to sub-steps or insights."""
        if self.current_step:
            # If type is WARNING/CRITICAL -> Insight
            if type in ["WARNING", "CRITICAL"]:
                self.add_insight("WARNING", f"{description}: {reason}")
            # If type is EXCLUDED/INCLUDED -> Calculation Sub-step
            elif type in ["EXCLUDED", "INCLUDED"]:
                 self.add_sub_step(f"{type}: {description} ({reason or ''})")
            # INFO -> Sub-step
            else:
                 self.add_sub_step(f"{description}: {reason or ''}")

    def get_steps(self) -> List[CalculationStep]:
        """Return the list of recorded steps."""
        return self.steps
