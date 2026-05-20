import csv
import json
import re
from pathlib import Path

from services.settings_store import load_settings


CAMPAIGNS_PATH = Path("data/campaigns/campaigns.json")

VALID_ENGINES = [
    "Google",
    "Bing",
]


def ensure_campaigns_file():
    CAMPAIGNS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not CAMPAIGNS_PATH.exists():
        save_campaigns({"campaigns": []})


def load_campaigns_data():
    ensure_campaigns_file()

    with CAMPAIGNS_PATH.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {"campaigns": []}

    if not isinstance(data, dict):
        return {"campaigns": []}

    if "campaigns" not in data or not isinstance(data["campaigns"], list):
        data["campaigns"] = []

    for campaign in data["campaigns"]:
        if "setting_id" not in campaign:
            campaign["setting_id"] = ""

    return data


def save_campaigns(data):
    CAMPAIGNS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with CAMPAIGNS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def list_campaigns():
    data = load_campaigns_data()
    campaigns = data.get("campaigns", [])

    return enrich_campaigns_with_setting_names(sort_campaigns(campaigns))


def sort_campaigns(campaigns):
    return sorted(
        campaigns,
        key=lambda campaign: (
            campaign.get("engine", ""),
            campaign.get("account_name", ""),
            campaign.get("campaign_name", ""),
        ),
    )


def get_campaign_by_id(campaign_id):
    campaigns = load_campaigns_data().get("campaigns", [])

    return next(
        (
            campaign
            for campaign in campaigns
            if campaign.get("id") == campaign_id
        ),
        None,
    )


def create_campaign(campaign):
    data = load_campaigns_data()
    campaigns = data.get("campaigns", [])

    existing = get_campaign_by_id(campaign["id"])

    if existing is not None:
        return ["That engine/account/campaign combination already exists."]

    campaigns.append(campaign)
    data["campaigns"] = sort_campaigns(campaigns)
    save_campaigns(data)

    return []


def update_campaign_by_id(campaign_id, updated_campaign):
    data = load_campaigns_data()
    campaigns = data.get("campaigns", [])

    for index, campaign in enumerate(campaigns):
        if campaign.get("id") == campaign_id:
            campaigns[index] = updated_campaign
            data["campaigns"] = sort_campaigns(campaigns)
            save_campaigns(data)
            return []

    return ["Campaign not found."]


def delete_campaign_by_id(campaign_id):
    data = load_campaigns_data()
    campaigns = data.get("campaigns", [])

    filtered_campaigns = [
        campaign
        for campaign in campaigns
        if campaign.get("id") != campaign_id
    ]

    if len(filtered_campaigns) == len(campaigns):
        return False

    data["campaigns"] = sort_campaigns(filtered_campaigns)
    save_campaigns(data)

    return True


def build_campaign_from_form(form, existing_id=None):
    engine = form.get("engine", "").strip()
    account_name = form.get("account_name", "").strip()
    account_id = form.get("account_id", "").strip()
    campaign_name = form.get("campaign_name", "").strip()
    campaign_id = form.get("campaign_id", "").strip()
    setting_id = form.get("setting_id", "").strip()
    notes = form.get("notes", "").strip()

    row_id = existing_id or make_campaign_row_id(
        engine=engine,
        account_id=account_id,
        campaign_id=campaign_id,
    )

    return {
        "id": row_id,
        "engine": engine,
        "account_name": account_name,
        "account_id": account_id,
        "campaign_name": campaign_name,
        "campaign_id": campaign_id,
        "setting_id": setting_id,
        "notes": notes,
    }


def validate_campaign(campaign):
    errors = []

    if campaign.get("engine") not in VALID_ENGINES:
        errors.append("Engine must be Google or Bing.")

    if not campaign.get("account_name"):
        errors.append("Account name is required.")

    if not campaign.get("account_id"):
        errors.append("Account ID is required.")

    if not campaign.get("campaign_name"):
        errors.append("Campaign name is required.")

    if not campaign.get("campaign_id"):
        errors.append("Campaign ID is required.")

    setting_id = campaign.get("setting_id", "")

    if setting_id and setting_id not in get_available_setting_ids():
        errors.append("Selected settings file does not exist.")

    return errors


def get_campaign_summary(campaigns):
    engines = sorted(
        {
            campaign.get("engine")
            for campaign in campaigns
            if campaign.get("engine")
        }
    )

    accounts = sorted(
        {
            (
                campaign.get("engine", ""),
                campaign.get("account_name", ""),
                campaign.get("account_id", ""),
            )
            for campaign in campaigns
            if campaign.get("account_id")
        }
    )

    mapped_campaigns = [
        campaign
        for campaign in campaigns
        if campaign.get("setting_id")
    ]

    return {
        "engines": engines,
        "accounts": accounts,
        "mapped_campaigns": mapped_campaigns,
    }


def import_campaigns_from_csv_file(csv_file):
    data = load_campaigns_data()
    campaigns = data.get("campaigns", [])

    campaigns_by_id = {
        campaign.get("id"): campaign
        for campaign in campaigns
        if campaign.get("id")
    }

    added_count = 0
    updated_count = 0
    skipped_count = 0

    decoded_lines = (
        line.decode("utf-8-sig")
        for line in csv_file.stream.readlines()
    )

    reader = csv.DictReader(decoded_lines)

    for row in reader:
        campaign = build_campaign_from_csv_row(row)
        errors = validate_campaign(campaign)

        if errors:
            skipped_count += 1
            continue

        campaign_id = campaign["id"]

        if campaign_id in campaigns_by_id:
            existing_setting_id = campaigns_by_id[campaign_id].get("setting_id", "")
            campaign["setting_id"] = existing_setting_id

            campaigns_by_id[campaign_id] = campaign
            updated_count += 1
        else:
            campaigns_by_id[campaign_id] = campaign
            added_count += 1

    data["campaigns"] = sort_campaigns(list(campaigns_by_id.values()))
    save_campaigns(data)

    return added_count, updated_count, skipped_count


def build_campaign_from_csv_row(row):
    engine = str(row.get("Engine", "")).strip()
    account_name = str(row.get("Account Name", "")).strip()
    account_id = str(row.get("Account ID", "")).strip()
    campaign_name = str(row.get("Campaign Name", "")).strip()
    campaign_id = str(row.get("Campaign ID", "")).strip()
    notes = str(row.get("Notes", "")).strip()

    return {
        "id": make_campaign_row_id(
            engine=engine,
            account_id=account_id,
            campaign_id=campaign_id,
        ),
        "engine": engine,
        "account_name": account_name,
        "account_id": account_id,
        "campaign_name": campaign_name,
        "campaign_id": campaign_id,
        "setting_id": "",
        "notes": notes,
    }


def get_available_settings():
    settings_data = load_settings()
    settings = settings_data.get("geoid_lists", [])

    return sorted(
        settings,
        key=lambda setting: setting.get("name", "").lower(),
    )


def get_available_setting_ids():
    return {
        setting.get("id")
        for setting in get_available_settings()
        if setting.get("id")
    }


def get_settings_by_id():
    return {
        setting.get("id"): setting
        for setting in get_available_settings()
        if setting.get("id")
    }


def enrich_campaigns_with_setting_names(campaigns):
    settings_by_id = get_settings_by_id()

    enriched_campaigns = []

    for campaign in campaigns:
        campaign_copy = dict(campaign)

        setting_id = campaign_copy.get("setting_id", "")
        setting = settings_by_id.get(setting_id)

        campaign_copy["setting_name"] = setting.get("name", "") if setting else ""

        enriched_campaigns.append(campaign_copy)

    return enriched_campaigns


def get_campaign_setting_records():
    """
    Backend helper for the actual upload process.

    This gives you one combined list where every campaign row includes
    the full selected settings object.

    Example result:
    [
        {
            "campaign": {...},
            "setting": {...}
        }
    ]
    """
    campaigns = load_campaigns_data().get("campaigns", [])
    settings_by_id = get_settings_by_id()

    records = []

    for campaign in campaigns:
        setting_id = campaign.get("setting_id", "")
        setting = settings_by_id.get(setting_id)

        records.append(
            {
                "campaign": campaign,
                "setting": setting,
            }
        )

    return records


def get_mapped_campaign_setting_records():
    """
    Same as get_campaign_setting_records(), but only campaigns
    that have a valid selected setting.
    """
    return [
        record
        for record in get_campaign_setting_records()
        if record["setting"] is not None
    ]


def make_campaign_row_id(engine, account_id, campaign_id):
    return "-".join(
        [
            slugify(engine),
            slugify(account_id),
            slugify(campaign_id),
        ]
    )


def slugify(value):
    value = str(value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")

    return value or "unknown"
