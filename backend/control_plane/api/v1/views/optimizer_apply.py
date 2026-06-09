# control_plane/api/v1/views/optimizer_apply.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from control_plane.permissions.member import IsOrganizationMember

from actions.models import (
    OptimizationPlan,
    ActionExecution,
)

from actions.tasks import execute_action


class ApplyOptimizationView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsOrganizationMember,
    ]

    def post(self, request):
        opt_id = request.data.get("id")

        if not opt_id:
            return Response(
                {"error": "Optimization ID required"},
                status=400,
            )

        try:
            opt = OptimizationPlan.objects.get(
                id=opt_id,
                cloud_account__organization=request.organization,
            )

        except OptimizationPlan.DoesNotExist:
            return Response(
                {"error": "Optimization not found"},
                status=404,
            )

        # ---------------------------------------
        # RECOMMENDATIONS ARE INFORMATION ONLY
        # ---------------------------------------

        if opt.action_type == "RECOMMEND":

            opt.status = "COMPLETED"
            opt.save(update_fields=["status"])

            return Response({
                "message": "Recommendation acknowledged.",
                "optimization_id": opt.id,
            })

        # ---------------------------------------
        # EXECUTABLE ACTIONS
        # ---------------------------------------

        execution = ActionExecution.objects.create(
            optimization=opt,
            status="planned",
        )

        opt.status = "IN_PROGRESS"
        opt.save(update_fields=["status"])

        execute_action.delay(str(execution.id))

        return Response({
            "message": "Execution started",
            "execution_id": str(execution.id),
        })
