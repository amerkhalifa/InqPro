import json
import re
from pathlib import Path

from config.settings_options import (
    BIDDER_NAMES,
    CALL_JOB_TYPE_OPTIONS,
    CALL_PEST_OPTIONS,
    CALL_TASKS,
    LEAD_JOB_TYPE_OPTIONS,
    LEAD_MATERIAL_OPTIONS,
    LEAD_PROPERTY_TYPE_OPTIONS,
    LEAD_TASKS,
    LEAD_TYPES,
)


SETTINGS_PATH = Path("data/file_settings.json")


def load_settings():
    if not SETTINGS_PATH.exists():
        return {"geoid_lists": []}

    with SETTINGS_PATH.open("r") as f:
        return json.load(f)


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SETTINGS_PATH.open("w") as f:
        json.dump(settings, f, indent=4)


def get_setting_by_id(setting_id):
    settings = load_settings()
    geoid_lists = settings.get("geoid_lists", [])

    return next(
        (item for item in geoid_lists if item.get("id") == setting_id),
        None,
    )


def update_setting_by_id(setting_id, updated_setting):
    settings = load_settings()
    geoid_lists = settings.get("geoid_lists", [])

    setting = next(
        (item for item in geoid_lists if item.get("id") == setting_id),
        None,
    )

    if setting is None:
        return False

    index = geoid_lists.index(setting)
    geoid_lists[index] = updated_setting

    save_settings(settings)

    return True


def delete_setting_by_id(setting_id):
    settings = load_settings()

    settings["geoid_lists"] = [
        item
        for item in settings.get("geoid_lists", [])
        if item.get("id") != setting_id
    ]

    save_settings(settings)


def parse_setting_form(form):
    return {
        "name": form.get("name", "").strip(),
        "zip->county": parse_float_or_none(form.get("zip_to_county")),
        "county->state": parse_float_or_none(form.get("county_to_state")),
        "bidders": parse_bidders_from_form(form),
    }


def parse_bidders_from_form(form):
    bidder_indexes = set()
    pattern = re.compile(r"bidders\[(\d+)\]\[(.+?)\]")

    for key in form.keys():
        match = pattern.match(key)

        if match:
            bidder_indexes.add(int(match.group(1)))

    bidders = []

    for index in sorted(bidder_indexes):
        prefix = f"bidders[{index}]"

        bidder_name = form.get(f"{prefix}[name]", "").strip()
        lead_type = form.get(f"{prefix}[lead_type]", "").strip()

        if bidder_name not in BIDDER_NAMES:
            continue

        if lead_type not in LEAD_TYPES:
            continue

        selected_task = form.get(f"{prefix}[tasks]", "").strip()
        allowed_tasks = CALL_TASKS if lead_type == "Calls" else LEAD_TASKS

        tasks = []

        if selected_task and selected_task in allowed_tasks:
            tasks.append(selected_task)

        min_price = parse_float_or_none(form.get(f"{prefix}[min_price]"))
        max_price = parse_float_or_none(form.get(f"{prefix}[max_price]"))

        bidder = {
            "name": bidder_name,
            "lead_type": lead_type,
            "tasks": tasks,
            "min_price": min_price,
            "max_price": max_price,
        }

        if bidder_name == "Internal":
            fs_props = parse_fs_props_from_form(form, prefix, lead_type)

            if fs_props:
                bidder["fs_props"] = fs_props

        bidders.append(bidder)

    return bidders


def parse_fs_props_from_form(form, prefix, lead_type):
    fs_props = {}

    if lead_type == "Calls":
        pest = form.get(f"{prefix}[pest]", "").strip()
        job_type = form.get(f"{prefix}[job_type]", "").strip()

        if pest in CALL_PEST_OPTIONS:
            fs_props["pest"] = pest

        if job_type in CALL_JOB_TYPE_OPTIONS:
            fs_props["job_type"] = job_type

    if lead_type == "Leads":
        material = form.get(f"{prefix}[material]", "").strip()
        property_type = form.get(f"{prefix}[property_type]", "").strip()
        job_type = form.get(f"{prefix}[job_type]", "").strip()

        if material in LEAD_MATERIAL_OPTIONS:
            fs_props["material"] = material

        if property_type in LEAD_PROPERTY_TYPE_OPTIONS:
            fs_props["property_type"] = property_type

        if job_type in LEAD_JOB_TYPE_OPTIONS:
            fs_props["job_type"] = job_type

    return fs_props


def parse_float_or_none(value):
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    return float(value)
