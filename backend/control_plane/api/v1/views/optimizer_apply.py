# control_plane/api/v1/views/optimizer_apply.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from control_plane.permissions.member import IsOrganizationMember

from actions.models import (
    ExecutionPlan,
    ActionExecution,
)

from actions.tasks import execute_action


class ApplyOptimizationView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsOrganizationMember,
    ]

    def post(self, request):
        plan_id = request.data.get("id")

        if not plan_id:
            return Response(
                {"error": "Optimization ID required"},
                status=400,
            )

        try:
            plan = ExecutionPlan.objects.get(
                id=plan_id,
                cloud_account__organization=request.organization,
            )

        except ExecutionPlan.DoesNotExist:
            return Response(
                {"error": "Optimization not found"},
                status=404,
            )

        # ---------------------------------------
        # RECOMMENDATIONS ARE INFORMATION ONLY
        # ---------------------------------------

        if plan.action == "RECOMMEND":
            return Response(
                {
                    "message": "This recommendation does not require execution."
                }
            )
        
        # ---------------------------------------
        # EXECUTABLE ACTIONS
        # ---------------------------------------

        execution = ActionExecution.objects.create(
            plan=plan,
            status="planned",
        )

        plan.status = "queued"
        plan.save(update_fields=["status"])

        execute_action.delay(str(execution.id))

        return Response({
            "message": "Execution started",
            "execution_id": str(execution.id),
        })
