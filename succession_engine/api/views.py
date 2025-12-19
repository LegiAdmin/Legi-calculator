from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from pydantic import ValidationError

from succession_engine.schemas import SimulationInput, SuccessionOutput
from succession_engine.core.calculator import SuccessionCalculator
from succession_engine.models import SimulationScenario
from succession_engine.api.serializers import SimulationScenarioSerializer

class ScenarioListView(ListCreateAPIView):
    """
    API View to list and create simulation scenarios (Test Batteries).
    """
    queryset = SimulationScenario.objects.all().order_by('-created_at')
    serializer_class = SimulationScenarioSerializer
    permission_classes = [AllowAny]

class SimulateSuccessionView(APIView):
    """
    API View to handle succession calculation requests.
    Accepts input data, triggers the orchestrator, and returns the calculation result.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=SimulationInput,
        responses={200: SuccessionOutput},
        summary="Simulate a succession",
        description="Calculates the succession details (assets, rights, duties) based on the provided simulation input."
    )
    def post(self, request):
        """
        Handles POST requests for succession calculation.
        """
        try:
            # 1. Validate Input with Pydantic
            # We use the Pydantic model directly to validate the JSON payload
            simulation_input = SimulationInput(**request.data)
        except ValidationError as e:
            # Return 400 if validation fails
            return Response({"errors": e.errors()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Run Calculation
            calculator = SuccessionCalculator()
            result = calculator.run(simulation_input)
            
            # 3. Enrich with explanations from rule dictionary (decoupled presentation)
            from succession_engine.services.explainer import explainer
            result_dict = result.model_dump()
            enriched_result = explainer.enrich_output(result_dict)
            
            # 4. Return Enriched Result
            return Response(enriched_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Handle unexpected errors during calculation
            return Response({"error": "Calculation failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoldenScenariosView(APIView):
    """
    API View to serve golden scenarios for testing.
    Returns the golden_scenarios.json content for the simulator to run tests.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: dict},
        summary="Get golden test scenarios",
        description="Returns all golden scenarios for automated and manual testing."
    )
    def get(self, request):
        """
        Returns the golden scenarios from the JSON file.
        """
        import json
        from pathlib import Path
        
        scenarios_path = Path(__file__).parent.parent.parent / 'tests' / 'golden_scenarios.json'
        
        if not scenarios_path.exists():
            return Response(
                {"error": "Golden scenarios file not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                scenarios = json.load(f)
            return Response(scenarios, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to load scenarios: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
