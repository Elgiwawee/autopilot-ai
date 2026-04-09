from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from control_plane.api.v1.views.overview import OverviewView
from control_plane.api.v1.views.gpus import GPUView
from control_plane.api.v1.views.optimizer import OptimizerView
from control_plane.api.v1.views.audit import AuditLogView
from control_plane.api.v1.views.auth import LoginView, RegisterView
from control_plane.api.v1.views.me import MeView
from control_plane.api.v1.views.global_safety import GlobalSafetyStatusView, ToggleAutopilotView
from control_plane.api.v1.views.cloud_accounts import CloudAccountListCreateView, CloudAccountDetailView
from control_plane.api.v1.views.autopilot_settings import AutopilotSettingsView
from control_plane.api.v1.views.billing_overview import BillingOverviewView
from control_plane.api.v1.views.invoices import InvoiceListView
from control_plane.api.v1.views.invoice_export import InvoiceExportView
from control_plane.api.v1.views.savings import SavingsOverviewView, SavingsTrendView, SavingsRecommendationView
from control_plane.api.v1.views.infra_overview import InfraOverviewView
from control_plane.api.v1.views.infra_regions import RegionsView
from control_plane.api.v1.views.infra_resources import ResourceListView
from control_plane.api.v1.views.infra_cloud_accounts import InfraCloudAccountView
from control_plane.api.v1.views.savings_export import SavingsExportCSVView
from control_plane.api.v1.views.invite import InviteMemberView, ResendInviteView, CancelInviteView, AcceptInviteView, ListInvitesView
from control_plane.api.v1.views.policies import AutopilotPolicyView
from control_plane.api.v1.views.optimizer_apply import ApplyOptimizationView
from control_plane.api.v1.views.autopilot import (
    AutopilotStatusView,
    AutopilotModeView,
    AutopilotRunView,
)
from control_plane.api.v1.views.member import (
    AddMemberView,
    ListMembersView,
    RemoveMemberView,
    UpdateMemberRoleView,
)

urlpatterns = [
    # -------- AUTH --------
    path("v1/auth/register/", RegisterView.as_view()),
    path("v1/auth/login/", LoginView.as_view()),
    path("v1/auth/me/", MeView.as_view()),

    # -------- CORE DASHBOARD --------
    path("v1/overview/", OverviewView.as_view()),
    path("v1/gpus/", GPUView.as_view()),
    path("v1/optimizer/", OptimizerView.as_view()),
    path("v1/savings/overview/", SavingsOverviewView.as_view()),
    path("v1/savings/trend/", SavingsTrendView.as_view()),
    path("v1/savings/recommendations/", SavingsRecommendationView.as_view()),
    path("v1/savings/export/csv/", SavingsExportCSVView.as_view()),


    # -------- GOVERNANCE --------
    path("v1/audit-logs/", AuditLogView.as_view()),
    path("v1/global-safety/", GlobalSafetyStatusView.as_view()),
    path("v1/toggle-autopilot/", ToggleAutopilotView.as_view()),

    # -------- CONFIGURATION --------
    path("v1/cloud-accounts/", CloudAccountListCreateView.as_view()),
    path("v1/cloud-accounts/<uuid:account_id>/", CloudAccountDetailView.as_view()),
    path("v1/autopilot-settings/", AutopilotSettingsView.as_view()),
]
urlpatterns += [
    path("v1/billing/summary/", BillingOverviewView.as_view()),
    path("v1/billing/invoices/", InvoiceListView.as_view()),
    path(
    "v1/billing/invoices/<uuid:invoice_id>/export/<str:fmt>/",
    InvoiceExportView.as_view(),
),
]   

urlpatterns += [
    path("v1/infra/overview/", InfraOverviewView.as_view()),
    path("v1/infra/regions/", RegionsView.as_view()),
    path("v1/infra/resources/", ResourceListView.as_view()),
    path("v1/infra/cloud-accounts/", InfraCloudAccountView.as_view()),
]

urlpatterns += [
    path("v1/autopilot/status/", AutopilotStatusView.as_view()),
    path("v1/autopilot/mode/", AutopilotModeView.as_view()),
    path("v1/autopilot/run/", AutopilotRunView.as_view()),
]

urlpatterns += [
    path("api/token/refresh/", TokenRefreshView.as_view()),
]

urlpatterns += [
    path("v1/policy/", AutopilotPolicyView.as_view()),
]

urlpatterns += [
    path("v1/invite/", InviteMemberView.as_view()),
    path("v1/invites/", ListInvitesView.as_view()),
    path("v1/invite/accept/<uuid:token>/", AcceptInviteView.as_view()),
]
urlpatterns += [
    path("v1/invite/cancel/", CancelInviteView.as_view()),
    path("v1/invite/resend/", ResendInviteView.as_view()),
]

urlpatterns += [
    path("v1/members/", ListMembersView.as_view()),
    path("v1/members/add/", AddMemberView.as_view()),
    path("v1/members/remove/", RemoveMemberView.as_view()),
    path("v1/members/role/", UpdateMemberRoleView.as_view()),
]

urlpatterns += [
    path("v1/optimizer/apply/", ApplyOptimizationView.as_view()),
]