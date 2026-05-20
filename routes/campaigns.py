from flask import Blueprint, flash, redirect, render_template, request, url_for

from services.campaign_store import (
    build_campaign_from_form,
    create_campaign,
    delete_campaign_by_id,
    get_available_settings,
    get_campaign_by_id,
    get_campaign_summary,
    import_campaigns_from_csv_file,
    list_campaigns,
    update_campaign_by_id,
    validate_campaign,
)


campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")


@campaigns_bp.route("/")
def campaigns_index():
    campaigns = list_campaigns()
    summary = get_campaign_summary(campaigns)

    return render_template(
        "campaigns_index.html",
        campaigns=campaigns,
        total_campaigns=len(campaigns),
        total_engines=len(summary["engines"]),
        total_accounts=len(summary["accounts"]),
        total_mapped_campaigns=len(summary["mapped_campaigns"]),
    )


@campaigns_bp.route("/new", methods=["GET", "POST"])
def create_campaign_page():
    campaign = {
        "id": "",
        "engine": "Google",
        "account_name": "",
        "account_id": "",
        "campaign_name": "",
        "campaign_id": "",
        "setting_id": "",
        "notes": "",
    }

    available_settings = get_available_settings()

    if request.method == "POST":
        campaign = build_campaign_from_form(request.form)
        errors = validate_campaign(campaign)

        if not errors:
            errors = create_campaign(campaign)

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "campaign_form.html",
                mode="create",
                campaign=campaign,
                available_settings=available_settings,
            )

        flash("Campaign created.", "success")
        return redirect(url_for("campaigns.campaigns_index"))

    return render_template(
        "campaign_form.html",
        mode="create",
        campaign=campaign,
        available_settings=available_settings,
    )


@campaigns_bp.route("/<campaign_id>/edit", methods=["GET", "POST"])
def edit_campaign_page(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    available_settings = get_available_settings()

    if campaign is None:
        flash("Campaign not found.", "error")
        return redirect(url_for("campaigns.campaigns_index"))

    if request.method == "POST":
        updated_campaign = build_campaign_from_form(
            request.form,
            existing_id=campaign_id,
        )
        errors = validate_campaign(updated_campaign)

        if not errors:
            errors = update_campaign_by_id(campaign_id, updated_campaign)

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "campaign_form.html",
                mode="edit",
                campaign=updated_campaign,
                available_settings=available_settings,
            )

        flash("Campaign updated.", "success")
        return redirect(url_for("campaigns.campaigns_index"))

    return render_template(
        "campaign_form.html",
        mode="edit",
        campaign=campaign,
        available_settings=available_settings,
    )


@campaigns_bp.route("/<campaign_id>/delete", methods=["POST"])
def delete_campaign_page(campaign_id):
    deleted = delete_campaign_by_id(campaign_id)

    if deleted:
        flash("Campaign deleted.", "success")
    else:
        flash("Campaign not found.", "error")

    return redirect(url_for("campaigns.campaigns_index"))


@campaigns_bp.route("/import-csv", methods=["POST"])
def import_campaigns_csv():
    csv_file = request.files.get("csv_file")

    if not csv_file or not csv_file.filename:
        flash("Please choose a CSV file.", "error")
        return redirect(url_for("campaigns.campaigns_index"))

    added_count, updated_count, skipped_count = import_campaigns_from_csv_file(csv_file)

    flash(
        (
            f"CSV imported. Added {added_count}, "
            f"updated {updated_count}, skipped {skipped_count}."
        ),
        "success",
    )

    return redirect(url_for("campaigns.campaigns_index"))
