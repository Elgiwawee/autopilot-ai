# control_plane/services/optimizer_service.py

from actions.services.optimizer import list_optimizations



def build_optimizer(organization):
    return {
        "organization": organization.id,
        "optimizations": list_optimizations(
            organization
        ),
    }