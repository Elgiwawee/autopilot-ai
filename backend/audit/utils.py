# audit/utils.py

import json
import hashlib

def generate_checksum(event):
    payload = json.dumps(
        {
            "event_id": str(event.event_id),
            "before": event.before_state,
            "after": event.after_state,
            "time": event.created_at.isoformat(),
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()
