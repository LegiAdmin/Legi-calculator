from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
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

class SimulateSuccessionView(APIView):
    """
    API View to handle succession calculation requests.
    Accepts input data, triggers the orchestrator, and returns the calculation result.
    """
    
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
            
            # 3. Return Result
            # We convert the Pydantic output model to a dict
            return Response(result.model_dump(), status=status.HTTP_200_OK)
            
        except Exception as e:
            # Handle unexpected errors during calculation
            return Response({"error": "Calculation failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
