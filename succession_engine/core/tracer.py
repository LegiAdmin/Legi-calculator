from typing import List, Dict, Optional, Any
from succession_engine.schemas import CalculationStep, CalculationDecision, DecisionType

class BusinessLogicTracer:
    """
    Helper to trace business logic execution for user explicability.
    Collects steps, inputs, outputs, rules applied, and decisions.
    """
    def __init__(self):
        self.steps: List[CalculationStep] = []
        self.current_step: Optional[CalculationStep] = None

    def start_step(self, step_number: int, step_name: str, description: str) -> None:
        """Begin a new calculation step."""
        # Ensure previous step is closed (though specific end_step is preferred)
        if self.current_step and not self.current_step.result_summary:
            pass # Or log warning
            
        self.current_step = CalculationStep(
            step_number=step_number,
            step_name=step_name,
            description=description,
            result_summary="En cours...",
            what="",
            why="",
            inputs={},
            outputs={},
            decisions=[]
        )
        self.steps.append(self.current_step)

    def end_step(self, result_summary: str) -> None:
        """Finalize the current step with a summary."""
        if self.current_step:
            self.current_step.result_summary = result_summary
            self.current_step = None # Detach

    def explain(self, what: str = None, why: str = None) -> None:
        """Add high-level explanation to the current step (What are we doing? Why?)."""
        if self.current_step:
            if what:
                self.current_step.what = what
            if why:
                self.current_step.why = why

    def add_input(self, key: str, value: Any) -> None:
        """Detail a specific input value used in this step."""
        if self.current_step:
            # Format value if float needed
            if isinstance(value, float):
                val_str = f"{value:,.2f} €".replace(",", " ").replace(".", ",")
            else:
                val_str = str(value)
            self.current_step.inputs[key] = val_str

    def add_output(self, key: str, value: Any) -> None:
        """Detail a specific output value calculated in this step."""
        if self.current_step:
             # Format value if float needed
            if isinstance(value, float):
                val_str = f"{value:,.2f} €".replace(",", " ").replace(".", ",")
            else:
                val_str = str(value)
            self.current_step.outputs[key] = val_str

    def add_decision(self, type: str, description: str, reason: Optional[str] = None) -> None:
        """Record a key decision (e.g., Heir Included/Excluded, Rule Applied)."""
        if self.current_step:
            # Flexible type input, convert to Enum if string
            try:
                dt = DecisionType(type)
            except ValueError:
                dt = DecisionType.INFO

            self.current_step.decisions.append(CalculationDecision(
                type=dt,
                description=description,
                reason=reason
            ))

    def get_steps(self) -> List[CalculationStep]:
        """Return the list of recorded steps."""
        return self.steps
