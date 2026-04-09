# control_plane/services/gpu_service.py

from monitoring.services.gpu_service import GPUService


class GPUInventoryService:

    @classmethod
    def build(
        cls,
        organization,
        cloud: str | None = None,
        region: str | None = None,
    ):
        inventory = GPUService.list(
            organization=organization,
            cloud=cloud,
            region=region,
        )

        total = len(inventory)

        active = sum(1 for g in inventory if g["state"] == "running")
        idle = sum(1 for g in inventory if g["state"] == "stopped")

        # Convert hourly → estimated monthly (730 hours avg)
        monthly_cost = sum(
            g["cost_per_hour"] * 730
            for g in inventory
            if g["cost_per_hour"]
        )

        return {
            "summary": {
                "total": total,
                "active": active,
                "idle": idle,
                "monthly_cost": round(monthly_cost, 2),
            },
            "gpus": inventory,
        }