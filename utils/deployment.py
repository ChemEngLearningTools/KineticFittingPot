from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
import zipfile


PUBLIC_CONTACT_EMAIL = "mark29464@gmail.com"

# The public Streamlit deployment deliberately exposes the teaching content and
# built-in simulations while protecting the shared Community Cloud process from
# user-defined workloads that can grow without a useful upper bound.
PUBLIC_CUSTOM_MODEL_LIMITS = {
    "max_upload_bytes": 2 * 1024 * 1024,
    "max_uncompressed_xlsx_bytes": 20 * 1024 * 1024,
    "max_xlsx_members": 100,
    "max_species": 12,
    "max_reactions": 12,
    "max_parameters": 40,
    "max_batch_duration_s": 24 * 60 * 60,
    "max_output_points": 1200,
    "max_function_evaluations": 20_000,
    "max_wall_time_s": 10.0,
}


PUBLIC_FITTING_LIMITS = {
    "max_upload_bytes": 2 * 1024 * 1024,
    "max_species": 12,
    "max_reactions": 12,
    "max_fitted_parameters": 8,
    "max_datasets": 6,
    "max_observations": 500,
    "max_batch_duration_s": 86_400,
    "max_starts": 3,
    "max_nfev_per_start": 150,
    "max_integrations": 3600,
    "max_rhs_evaluations": 400_000,
    "max_wall_time_s": 60.0,
}


def public_fitting_violations(problem) -> list[str]:
    limits = PUBLIC_FITTING_LIMITS
    counts = [(len(problem.model.species_ids), 'max_species', 'species'),
              (len(problem.model.reaction_ids), 'max_reactions', 'reactions'),
              (len(problem.fit_parameter_ids), 'max_fitted_parameters', 'fitted parameters'),
              (len(problem.datasets), 'max_datasets', 'selected datasets'),
              (len(problem.observations) + len(problem.validation_observations), 'max_observations', 'total fit and validation observations'),
              (len(problem.datasets) + len(problem.validation_datasets), 'max_datasets', 'total fit and validation datasets')]
    issues = [f"{label}: {value} exceeds the public limit of {limits[key]}." for value,key,label in counts if value > limits[key]]
    latest = max((o.time_s for o in (*problem.observations, *problem.validation_observations)), default=0)
    if latest > limits['max_batch_duration_s']:
        issues.append(f"Latest experimental time {latest:g} s exceeds the public limit of {limits['max_batch_duration_s']} s.")
    return issues


def public_fitting_limits_markdown() -> str:
    v = PUBLIC_FITTING_LIMITS
    return (f"Up to **{v['max_fitted_parameters']} fitted parameters**, **{v['max_datasets']} datasets**, "
            f"**{v['max_observations']} observations**, **{v['max_species']} species** and "
            f"**{v['max_reactions']} reactions**; maximum upload **{v['max_upload_bytes']//(1024*1024)} MB**. "
            f"Fitting uses **{v['max_starts']} multistart attempts**, up to **{v['max_nfev_per_start']} optimiser evaluations "
            f"per start**, and an overall numerical work budget of **{v['max_integrations']:,} ODE integrations**, "
            f"**{v['max_rhs_evaluations']:,} ODE RHS calls** and a **{v['max_wall_time_s']:.0f}-second hard process timeout**. "
            "Only one public fit runs at a time; requests made while the fitting service is busy must be retried. "
            "These limits do not guarantee convergence.")


def deployment_mode() -> str:
    """Return ``local`` or ``public_cloud`` without requiring secrets.

    ``KINETICFITTINGPOT_MODE`` is an optional explicit override useful for local
    preview/testing. Streamlit Community Cloud checks out apps below ``/mount/src``;
    that filesystem marker provides the normal automatic cloud detection. The
    supported local installation is Windows. Any unrecognised non-Windows host
    fails safe to the restricted mode so a cloud-path change cannot unlock heavy tools.
    """

    override = str(os.getenv("KINETICFITTINGPOT_MODE", "")).strip().lower()
    if override in {"local", "desktop", "development"}:
        return "local"
    if override in {"cloud", "public_cloud", "teaching_cloud", "streamlit_cloud"}:
        return "public_cloud"

    try:
        cwd = Path.cwd().resolve().as_posix().lower()
    except Exception:
        cwd = str(Path.cwd()).replace("\\", "/").lower()
    if cwd == "/mount/src" or cwd.startswith("/mount/src/"):
        return "public_cloud"

    # KineticFittingPot's supported desktop installation is Windows (for example C:\nmjw2\KineticFittingPot).
    # For any unrecognised non-Windows host, fail safe to the restricted mode: a
    # future cloud filesystem change must not accidentally expose heavy fitting.
    if os.name == "nt":
        return "local"
    return "public_cloud"


def is_public_cloud() -> bool:
    return deployment_mode() == "public_cloud"


def public_cloud_workbook_violations(workbook_bytes: bytes) -> list[str]:
    """Cheap pre-open checks for public uploads, including XLSX zip-bomb bounds."""

    limits = PUBLIC_CUSTOM_MODEL_LIMITS
    problems: list[str] = []
    if not workbook_bytes:
        return ["The uploaded workbook is empty."]
    if len(workbook_bytes) > limits["max_upload_bytes"]:
        problems.append(
            f"Workbook size is {len(workbook_bytes) / (1024 * 1024):.2f} MB; "
            f"the public-server limit is {limits['max_upload_bytes'] / (1024 * 1024):.0f} MB."
        )
        return problems

    if not zipfile.is_zipfile(BytesIO(workbook_bytes)):
        problems.append("The upload is not a valid .xlsx package.")
        return problems

    try:
        with zipfile.ZipFile(BytesIO(workbook_bytes), "r") as archive:
            members = archive.infolist()
            if len(members) > limits["max_xlsx_members"]:
                problems.append(
                    f"The workbook contains {len(members)} packaged files; the public-server limit is "
                    f"{limits['max_xlsx_members']}."
                )
            unpacked = sum(max(0, int(item.file_size)) for item in members)
            if unpacked > limits["max_uncompressed_xlsx_bytes"]:
                problems.append(
                    f"The workbook expands to {unpacked / (1024 * 1024):.1f} MB; the public-server "
                    f"uncompressed limit is {limits['max_uncompressed_xlsx_bytes'] / (1024 * 1024):.0f} MB."
                )
    except (OSError, zipfile.BadZipFile) as exc:
        problems.append(f"KineticFittingPot could not safely inspect this .xlsx package: {exc}")
    return problems


def public_cloud_model_violations(model) -> list[str]:
    limits = PUBLIC_CUSTOM_MODEL_LIMITS
    checks = [
        (len(model.species_ids), limits["max_species"], "species"),
        (len(model.reaction_ids), limits["max_reactions"], "reactions"),
        (len(model.parameter_ids), limits["max_parameters"], "parameters"),
    ]
    problems = [
        f"This model contains {actual} {label}; the public-server limit is {maximum}."
        for actual, maximum, label in checks
        if actual > maximum
    ]
    if float(model.batch_duration_s) > limits["max_batch_duration_s"]:
        problems.append(
            f"Batch_Duration_s is {float(model.batch_duration_s):g} s; the public-server limit is "
            f"{limits['max_batch_duration_s']:g} s (24 h)."
        )
    if int(model.output_points) > limits["max_output_points"]:
        problems.append(
            f"Output_Points is {int(model.output_points)}; the public-server limit is "
            f"{limits['max_output_points']}."
        )
    return problems


def public_custom_limits_markdown() -> str:
    limits = PUBLIC_CUSTOM_MODEL_LIMITS
    return (
        f"**Public-server limits:** upload ≤ {limits['max_upload_bytes'] // (1024 * 1024)} MB; "
        f"≤ {limits['max_species']} species; ≤ {limits['max_reactions']} reactions; "
        f"≤ {limits['max_parameters']} parameters; Batch_Duration_s ≤ 86,400 s; "
        f"Output_Points ≤ {limits['max_output_points']}; numerical work is stopped after "
        f"{limits['max_function_evaluations']:,} ODE right-hand-side evaluations or approximately "
        f"{limits['max_wall_time_s']:.0f} s of solver wall time."
    )


def render_public_cloud_lock(*, title: str, description: str, section: str, accent: str, kind: str) -> None:
    """Render an intentionally visible lock page for computationally heavy tools."""

    import streamlit as st
    from utils.ui import workspace_header

    workspace_header(title, description, section=section, accent=accent)
    st.warning("This computational workspace is disabled on the public KineticFittingPot server.")

    if kind == "fitting":
        reason = (
            "Kinetic parameter fitting repeatedly integrates dynamic reactor models inside a bounded "
            "multistart nonlinear optimisation. A single fit can require many thousands of ODE solves/evaluations; "
            "several simultaneous public users could exhaust the shared server CPU and memory."
        )
    else:
        reason = (
            "Post-fit diagnostics includes computationally intensive parameter-geometry and profiled-objective "
            "calculations. Profile calculations repeatedly re-optimise the remaining fitted parameters while "
            "solving the dynamic model, so unrestricted public use is not suitable for the shared server."
        )

    st.markdown(
        f"""
        <div class='panel'>
        <b>Why is it locked?</b><br><br>
        {reason}<br><br>
        The <b>Fundamentals</b> material remains available publicly so the complete modelling workflow can still be studied. 
        The numerical fitting and diagnostics workspaces remain fully enabled in the local KineticFittingPot build.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "This is a shared-computing restriction rather than a login or paywall. "
        "For teaching, research or collaboration enquiries about the full local capability, please contact the author."
    )
    st.markdown(f"**Contact:** [{PUBLIC_CONTACT_EMAIL}](mailto:{PUBLIC_CONTACT_EMAIL})")
