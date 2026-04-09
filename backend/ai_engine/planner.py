# ai_engine/planner.py

from ai_engine.right_sizing import generate_resize_plan
from ai_engine.storage.zombie import is_zombie, generate_delete_plan
from ai_engine.storage.gp3_rules import gp2_to_gp3_candidate
from ai_engine.storage.planner import generate_gp3_plan


def generate_action_plans(resource):

    plans = []

    # instance rightsizing
    resize = generate_resize_plan(resource)
    if resize:
        plans.append(resize)

    # zombie volumes
    if resource.resource_type == "ebs" and is_zombie(resource):
        plans.append(generate_delete_plan(resource))

    # gp2 → gp3 conversion
    if resource.resource_type == "ebs" and gp2_to_gp3_candidate(resource):
        plans.append(generate_gp3_plan(resource))

    return plans