import uuid

from flask import Blueprint, abort, redirect, render_template, request, url_for

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
from services.settings_store import (
    delete_setting_by_id,
    get_setting_by_id,
    load_settings,
    parse_setting_form,
    save_settings,
    update_setting_by_id,
)


settings_bp = Blueprint("settings", __name__)


def get_setting_form_options():
    return {
        "bidder_names": BIDDER_NAMES,
        "lead_types": LEAD_TYPES,
        "call_tasks": CALL_TASKS,
        "lead_tasks": LEAD_TASKS,
        "call_pest_options": CALL_PEST_OPTIONS,
        "call_job_type_options": CALL_JOB_TYPE_OPTIONS,
        "lead_material_options": LEAD_MATERIAL_OPTIONS,
        "lead_property_type_options": LEAD_PROPERTY_TYPE_OPTIONS,
        "lead_job_type_options": LEAD_JOB_TYPE_OPTIONS,
    }


@settings_bp.route("/settings")
def settings_index():
    settings = load_settings()

    return render_template(
        "settings_index.html",
        geoid_lists=settings.get("geoid_lists", []),
    )


@settings_bp.route("/settings/new", methods=["GET", "POST"])
def create_setting():
    if request.method == "POST":
        settings = load_settings()

        new_setting = parse_setting_form(request.form)
        new_setting["id"] = str(uuid.uuid4())[:8]

        settings["geoid_lists"].append(new_setting)
        save_settings(settings)

        return redirect(url_for("settings.settings_index"))

    return render_template(
        "setting_form.html",
        mode="create",
        setting=None,
        **get_setting_form_options(),
    )


@settings_bp.route("/settings/<setting_id>/edit", methods=["GET", "POST"])
def edit_setting(setting_id):
    setting = get_setting_by_id(setting_id)

    if setting is None:
        abort(404)

    if request.method == "POST":
        updated_setting = parse_setting_form(request.form)
        updated_setting["id"] = setting_id

        update_setting_by_id(setting_id, updated_setting)

        return redirect(url_for("settings.settings_index"))

    return render_template(
        "setting_form.html",
        mode="edit",
        setting=setting,
        **get_setting_form_options(),
    )


@settings_bp.route("/settings/<setting_id>/delete", methods=["POST"])
def delete_setting(setting_id):
    delete_setting_by_id(setting_id)

    return redirect(url_for("settings.settings_index"))
