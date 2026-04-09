# ai_engine/services/ai_service.py

from dataclasses import dataclass
from django.utils import timezone
from django.db.models import Avg, Max
from datetime import timedelta

from accounts.models import GlobalSafety
from cloud.models import CloudAccount
from ai_engine.models.recommendation  import Recommendation

@dataclass
class AIStatusDTO:
    state: str
    last_recommendation_at: str | None
    confidence: float
    mode: str | None

    def as_dict(self):
        return {
            "state": self.state,
            "last_recommendation_at": self.last_recommendation_at,
            "confidence": self.confidence,
            "mode": self.mode,
        }


class AIService:

    @classmethod
    def _base_queryset(cls, organization):
        return Recommendation.objects.filter(
            resource__cloud_account__organization=organization
        )

    @classmethod
    def status(
        cls,
        organization,
        cloud: str | None = None,
        region: str | None = None,
    ) -> AIStatusDTO:

        # 1️⃣ Global kill switch
        global_safety = GlobalSafety.objects.first()
        if global_safety and not global_safety.autopilot_enabled:
            return AIStatusDTO(
                state="DISABLED",
                last_recommendation_at=None,
                confidence=0.0,
                mode=None,
            )

        qs = cls._base_queryset(organization)

        if cloud:
            qs = qs.filter(
                resource__cloud_account__provider__slug=cloud
            )

        if region:
            qs = qs.filter(
                resource__cloud_account__region=region
            )

        # 2️⃣ Last recommendation time
        last_rec = qs.aggregate(
            last_time=Max("created_at")
        )["last_time"]

        # 3️⃣ Average confidence
        avg_conf = qs.aggregate(
            avg_conf=Avg("confidence")
        )["avg_conf"] or 0.0

        now = timezone.now()

        # 4️⃣ Determine state
        if not last_rec:
            state = "IDLE"

        elif last_rec < now - timedelta(hours=6):
            state = "STALE"

        else:
            state = "ACTIVE"

        # 5️⃣ Determine autopilot mode (if cloud filtered)
        mode = None
        if cloud:
            account = CloudAccount.objects.filter(
                organization=organization,
                provider__slug=cloud
            ).first()

            if account and hasattr(account, "autopilotsettings"):
                mode = account.autopilotsettings.mode

        return AIStatusDTO(
            state=state,
            last_recommendation_at=last_rec,
            confidence=round(float(avg_conf), 3),
            mode=mode,
        )