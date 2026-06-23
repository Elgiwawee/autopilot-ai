# control_plane/services/savings_service.py

from billing.services.savings_service import SavingsService


def build_savings(organization):
    return {
        "organization": organization.id,
        "summary": SavingsService.summary(organization),
    }
