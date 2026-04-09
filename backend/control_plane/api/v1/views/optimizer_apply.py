from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from control_plane.permissions.member import IsOrganizationMember
from actions.models import OptimizationPlan, ActionExecution
from control_plane.services.apply_optimizer import apply_optimization
from actions.tasks import execute_action

class ApplyOptimizationView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        opt_id = request.data.get("id")

        if not opt_id:
            return Response({"error": "Optimization ID required"}, status=400)

        try:
            opt = OptimizationPlan.objects.get(
                id=opt_id,
                cloud_account__organization=request.organization
            )
        except OptimizationPlan.DoesNotExist:
            return Response({"error": "Optimization not found"}, status=404)

        # ✅ CREATE EXECUTION RECORD
        execution = ActionExecution.objects.create(
            action_plan=opt,
            status="pending"
        )

        # ✅ TRIGGER CELERY TASK
        execute_action.delay(execution.id)

        # ✅ UPDATE PLAN STATUS
        opt.status = "IN_PROGRESS"
        opt.save()

        return Response({
            "message": "Execution started",
            "execution_id": execution.id
        })