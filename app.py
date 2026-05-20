from pathlib import Path
import json
import re
import uuid

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

SETTINGS_PATH = Path("data/file_settings.json")

BIDDER_NAMES = [
    "Internal",
    "Service Direct",
    "33 Mile Radius",
    "eLocal",
]

LEAD_TYPES = [
    "Calls",
    "Leads",
]

CALL_TASKS = [
    "Air Duct",
    "Appliance Repair",
    "Asbestos Removal",
    "Asbestos Testing",
    "Bathroom Remodel",
    "Biohazard",
    "Cabinets",
    "Chimneys",
    "Concrete Foundation",
    "Concrete Leveling",
    "Decks",
    "Doors",
    "Drainage Channel",
    "Electrician",
    "Excavation",
    "Fencing",
    "Fire Damage",
    "Flooring",
    "Garage Doors",
    "Grading",
    "Gutter Covers",
    "Gutters",
    "HVAC",
    "Hoarding",
    "Holiday Lighting",
    "Kitchen Remodeling",
    "Landscaping",
    "Lawn Mowing",
    "Locksmith",
    "Mold Removal",
    "Mold Testing",
    "Painting",
    "Pest Control",
    "Plumbing",
    "Roofing",
    "Siding",
    "Snow Removal",
    "Solar",
    "Stairlifts",
    "Tree Services",
    "Water Filtration",
    "Water Removal",
    "Waterproofing",
    "Windows",
]

LEAD_TASKS = [
    "Air Conditioning",
    "Air Duct",
    "Appliance Repair",
    "Asbestos Removal",
    "Asbestos Testing",
    "Asphalt Paving",
    "Attic Fan",
    "Backflow Install",
    "Backflow Testing",
    "Bathroom Remodel",
    "Bathtub Install",
    "Bathtub Liner Install",
    "Biohazard",
    "Boiler",
    "Ceiling Fan",
    "Chimneys",
    "Concrete Flatwork",
    "Concrete Floor",
    "Concrete Foundation",
    "Concrete Leveling",
    "Deck Painting",
    "Drain Camera",
    "Drain Unclog",
    "Drainage Channel",
    "Driveway",
    "Electrical Baseboard",
    "Electrical Inspection",
    "Electrical Panel",
    "Electrical Wiring",
    "Electrician",
    "Excavation",
    "Exhaust Fan",
    "Exterior Painting",
    "Faucet Repair",
    "Fence Painting",
    "Fencing",
    "Fire Damage",
    "Flooring",
    "Garage Doors",
    "Gas Piping",
    "Generator",
    "Grading",
    "Gutter Covers",
    "Gutters",
    "HVAC",
    "Heating",
    "Hoarding",
    "Holiday Lighting",
    "Hot Tub",
    "Interior Lighting",
    "Interior Painting",
    "Landscape Design",
    "Landscape Lighting",
    "Landscaping",
    "Lawn Aeration",
    "Lawn Cleanup",
    "Lawn Fertilizing",
    "Lawn Mowing",
    "Lawn Seeding",
    "Lawn Sodding",
    "Leak Detection",
    "Leak Repair",
    "Locksmith",
    "Mold Removal",
    "Mold Testing",
    "Network Wiring",
    "Painting",
    "Parking Lot Striping",
    "Patio",
    "Pavement Painting",
    "Pest Control",
    "Plumbing",
    "Plumbing Remodel",
    "Popcorn Ceiling",
    "Roofing",
    "Septic System",
    "Sewer Main",
    "Shower Install",
    "Siding",
    "Sink Repair",
    "Skylight",
    "Smoke Detector",
    "Snow Removal",
    "Soil Delivery",
    "Solar",
    "Sprinkler System",
    "Stump Removal",
    "Sump Pump",
    "Switches Outlets",
    "Synthetic Grass",
    "Thermostat",
    "Toilet Repair",
    "Tree Protection",
    "Tree Removal",
    "Tree Services",
    "Tree Trimming",
    "Wallpaper",
    "Water Damage",
    "Water Heater",
    "Water Main Repair",
    "Water Removal",
    "Water Treatment",
    "Waterproofing",
    "Weed Control",
    "Well Pump",
    "Windows",
    "Xeriscaping",
    "Yard Drain",
]

CALL_PEST_OPTIONS = [
    "Ants",
    "Bed Bugs",
    "Bees",
    "Birds",
    "Cockroaches",
    "Fleas",
    "Flies",
    "Insects",
    "Mice",
    "Mosquitos",
    "Raccoons",
    "Spiders",
    "Termites",
    "Wasps",
    "Wildlife",
]

CALL_JOB_TYPE_OPTIONS = [
    "Cleaning",
    "Install",
    "Refinish",
    "Repair",
]

LEAD_MATERIAL_OPTIONS = [
    "Asphalt",
    "Barbed Wire",
    "Brick",
    "Carpet",
    "Chainlink",
    "Concrete",
    "Copper",
    "Electric Pet",
    "Epoxy",
    "Gravel",
    "Laminate",
    "Metal",
    "PVC",
    "Pavers",
    "Single Ply",
    "Slate",
    "Spray Foam",
    "Stone",
    "Stucco",
    "Tar Gravel",
    "Tile",
    "Vinyl",
    "Wood",
    "Wrought Iron",
]

LEAD_PROPERTY_TYPE_OPTIONS = [
    "Business",
    "Residence",
]

LEAD_JOB_TYPE_OPTIONS = [
    "Cleaning",
    "Install",
    "Refinish",
    "Repair",
    "Resurface",
    "Sealing",
]


@app.route("/")
def home():
    return redirect(url_for("settings_index"))


@app.route("/settings")
def settings_index():
    settings = load_settings()

    return render_template(
        "settings_index.html",
        geoid_lists=settings.get("geoid_lists", []),
    )


@app.route("/settings/new", methods=["GET", "POST"])
def create_setting():
    if request.method == "POST":
        settings = load_settings()

        new_setting = parse_setting_form(request.form)
        new_setting["id"] = str(uuid.uuid4())[:8]

        settings["geoid_lists"].append(new_setting)
        save_settings(settings)

        return redirect(url_for("settings_index"))

    return render_template(
        "setting_form.html",
        mode="create",
        setting=None,
        bidder_names=BIDDER_NAMES,
        lead_types=LEAD_TYPES,
        call_tasks=CALL_TASKS,
        lead_tasks=LEAD_TASKS,
        call_pest_options=CALL_PEST_OPTIONS,
        call_job_type_options=CALL_JOB_TYPE_OPTIONS,
        lead_material_options=LEAD_MATERIAL_OPTIONS,
        lead_property_type_options=LEAD_PROPERTY_TYPE_OPTIONS,
        lead_job_type_options=LEAD_JOB_TYPE_OPTIONS,
    )


@app.route("/settings/<setting_id>/edit", methods=["GET", "POST"])
def edit_setting(setting_id):
    settings = load_settings()
    geoid_lists = settings.get("geoid_lists", [])

    setting = next(
        (item for item in geoid_lists if item.get("id") == setting_id),
        None,
    )

    if setting is None:
        abort(404)

    if request.method == "POST":
        updated_setting = parse_setting_form(request.form)
        updated_setting["id"] = setting_id

        index = geoid_lists.index(setting)
        geoid_lists[index] = updated_setting

        save_settings(settings)

        return redirect(url_for("settings_index"))

    return render_template(
        "setting_form.html",
        mode="edit",
        setting=setting,
        bidder_names=BIDDER_NAMES,
        lead_types=LEAD_TYPES,
        call_tasks=CALL_TASKS,
        lead_tasks=LEAD_TASKS,
        call_pest_options=CALL_PEST_OPTIONS,
        call_job_type_options=CALL_JOB_TYPE_OPTIONS,
        lead_material_options=LEAD_MATERIAL_OPTIONS,
        lead_property_type_options=LEAD_PROPERTY_TYPE_OPTIONS,
        lead_job_type_options=LEAD_JOB_TYPE_OPTIONS,
    )


@app.route("/settings/<setting_id>/delete", methods=["POST"])
def delete_setting(setting_id):
    settings = load_settings()

    settings["geoid_lists"] = [
        item
        for item in settings.get("geoid_lists", [])
        if item.get("id") != setting_id
    ]

    save_settings(settings)

    return redirect(url_for("settings_index"))


def load_settings():
    if not SETTINGS_PATH.exists():
        return {"geoid_lists": []}

    with SETTINGS_PATH.open("r") as f:
        return json.load(f)


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SETTINGS_PATH.open("w") as f:
        json.dump(settings, f, indent=4)


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


if __name__ == "__main__":
    app.run(debug=True)
