# ai_engine/storage/snapshots.py

from datetime import timedelta
from django.utils import timezone
from collections import defaultdict

from actions.models import ActionPlan


RETENTION_POLICY = {
    "daily": 7,
    "weekly": 4,
    "monthly": 6,
}


def classify_snapshot(snapshot):
    """
    Classify snapshot into daily / weekly / monthly bucket.
    """
    created = snapshot.created_at
    now = timezone.now()
    age_days = (now - created).days

    if age_days <= 7:
        return "daily"
    elif age_days <= 30:
        return "weekly"
    else:
        return "monthly"


def group_snapshots_by_volume(snapshots):
    grouped = defaultdict(list)

    for snapshot in snapshots:
        grouped[snapshot.volume_id].append(snapshot)

    return grouped


def snapshots_to_delete(snapshots):
    """
    Returns snapshots exceeding retention policy.
    """
    buckets = {
        "daily": [],
        "weekly": [],
        "monthly": [],
    }

    # Sort newest → oldest
    snapshots = sorted(
        snapshots,
        key=lambda s: s.created_at,
        reverse=True
    )

    for snapshot in snapshots:
        bucket = classify_snapshot(snapshot)
        buckets[bucket].append(snapshot)

    deletable = []

    for bucket, allowed in RETENTION_POLICY.items():
        kept = buckets[bucket][:allowed]
        expired = buckets[bucket][allowed:]
        deletable.extend(expired)

    return deletable


def generate_snapshot_delete_plan(snapshot):

    estimated_savings = (
        snapshot.size_gb * 0.05 * 24 * 30
    )

    return ActionPlan.objects.create(
        resource=snapshot.cloud_resource,
        action_type="DELETE_SNAPSHOT",
        estimated_savings=estimated_savings,
        risk_level="medium",
        is_safe=False,
        explanation=(
            "Snapshot exceeds retention policy "
            "(daily=7, weekly=4, monthly=6). "
            "Manual approval required."
        ),
    )


def analyze_snapshots(snapshots):
    """
    Entry point for snapshot lifecycle analysis.
    """
    grouped = group_snapshots_by_volume(snapshots)

    plans = []

    for volume_id, volume_snapshots in grouped.items():
        deletable = snapshots_to_delete(volume_snapshots)

        for snapshot in deletable:
            plan = generate_snapshot_delete_plan(snapshot)
            plans.append(plan)

    return plans


# later we can add:
# - def run_snapshot_lifecycle()