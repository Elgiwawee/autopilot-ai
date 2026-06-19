from django.core.management.base import BaseCommand

from actions.models import (
    ActionExecution,
    ExecutionPlan,
)


class Command(BaseCommand):
    help = "Populate ActionExecution.plan from legacy optimization mapping"

    def handle(self, *args, **options):

        updated = 0
        skipped = 0

        for execution in ActionExecution.objects.all():

            if execution.plan_id is not None:
                skipped += 1
                continue

            if execution.optimization_id is None:
                skipped += 1
                continue

            try:
                plan = ExecutionPlan.objects.get(
                    legacy_optimization_id=execution.optimization_id
                )

            except ExecutionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"No ExecutionPlan for OptimizationPlan "
                        f"{execution.optimization_id}"
                    )
                )
                continue

            execution.plan = plan
            execution.save(update_fields=["plan"])

            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated={updated}  Skipped={skipped}"
            )
        )