"""YugKrit - Authentication & registration routes."""

from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.database import db
from database.models import Organization, University, UniversityDepartment, ULB, NGO, OrganizationDocument
from services import auth_service, student_service
from utils.validators import ValidationError
from utils.permissions import ROLE_DASHBOARD
from utils.helpers import save_uploaded_file

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        try:
            user = auth_service.authenticate(email, password)
            session.clear()
            session["user_id"] = user.id
            session.permanent = True
            flash(f"Welcome back, {user.full_name.split(' ')[0]}!", "success")
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(url_for(ROLE_DASHBOARD.get(user.role_name(), "public.home")))
        except ValidationError as e:
            flash(e.message, "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))


@auth_bp.route("/register")
def register_landing():
    return render_template("auth/register_landing.html")


# --------------------------------------------------------------------------
# University registration (multi-step form, submitted as one POST)
# --------------------------------------------------------------------------
@auth_bp.route("/register/university", methods=["GET", "POST"])
def register_university():
    if request.method == "POST":
        f = request.form
        try:
            org = Organization(
                name=f["institution_name"], org_type="UNIVERSITY",
                official_email=f["official_email"], website=f.get("website"),
                phone=f.get("phone"), address=f.get("address"),
                district=f.get("district"), state=f.get("state"),
                status="PENDING",
            )
            db.session.add(org)
            db.session.flush()

            university = University(
                organization_id=org.id,
                institution_type=f.get("institution_type"),
                aishe_code=f.get("aishe_code"),
                affiliating_university=f.get("affiliating_university"),
                rep_name=f["rep_name"], rep_designation=f.get("rep_designation"),
                rep_email=f.get("rep_email"), rep_phone=f.get("rep_phone"),
            )
            db.session.add(university)
            db.session.flush()

            for dept in ["General"]:
                db.session.add(UniversityDepartment(university_id=university.id, name=dept))

            for file_field, doc_type in [("recognition_certificate", "Recognition Certificate"),
                                          ("registration_proof", "Registration Proof"),
                                          ("authorization_letter", "Authorization Letter")]:
                file = request.files.get(file_field)
                if file and file.filename:
                    name, path, size = save_uploaded_file(file, subfolder="organizations")
                    db.session.add(OrganizationDocument(organization_id=org.id, document_type=doc_type,
                                                         file_name=name, file_path=path, file_size=size))

            db.session.commit()

            auth_service.create_user(f["rep_name"], f["official_email"], f["password"],
                                      "UNIVERSITY_ADMIN", organization_id=org.id, phone=f.get("phone"))

            flash("University registration submitted. Government verification is pending.", "success")
            return redirect(url_for("auth.login"))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please check the form and try again.", "danger")
    return render_template("auth/register_university.html")


# --------------------------------------------------------------------------
# ULB registration
# --------------------------------------------------------------------------
@auth_bp.route("/register/ulb", methods=["GET", "POST"])
def register_ulb():
    if request.method == "POST":
        f = request.form
        try:
            org = Organization(
                name=f["name"], org_type="ULB", official_email=f["official_email"],
                website=f.get("website"), phone=f.get("phone"),
                district=f.get("district"), state=f.get("state"), status="PENDING",
            )
            db.session.add(org)
            db.session.flush()
            ulb = ULB(organization_id=org.id, ulb_type=f.get("ulb_type"),
                      authorized_officer=f["authorized_officer"], designation=f.get("designation"))
            db.session.add(ulb)

            file = request.files.get("document")
            if file and file.filename:
                name, path, size = save_uploaded_file(file, subfolder="organizations")
                db.session.add(OrganizationDocument(organization_id=org.id, document_type="Authorization Document",
                                                     file_name=name, file_path=path, file_size=size))
            db.session.commit()

            auth_service.create_user(f["authorized_officer"], f["official_email"], f["password"],
                                      "ULB_ADMIN", organization_id=org.id, phone=f.get("phone"))
            flash("ULB registration submitted. Government verification is pending.", "success")
            return redirect(url_for("auth.login"))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please check the form and try again.", "danger")
    return render_template("auth/register_ulb.html")


# --------------------------------------------------------------------------
# NGO registration
# --------------------------------------------------------------------------
@auth_bp.route("/register/ngo", methods=["GET", "POST"])
def register_ngo():
    if request.method == "POST":
        f = request.form
        try:
            org = Organization(
                name=f["name"], org_type="NGO", official_email=f["official_email"],
                website=f.get("website"), address=f.get("address"),
                district=f.get("district"), state=f.get("state"), status="PENDING",
            )
            db.session.add(org)
            db.session.flush()
            reg_date = None
            if f.get("registration_date"):
                reg_date = datetime.strptime(f["registration_date"], "%Y-%m-%d").date()
            ngo = NGO(organization_id=org.id, registration_number=f.get("registration_number"),
                      registration_authority=f.get("registration_authority"), registration_date=reg_date,
                      authorized_rep=f["authorized_rep"])
            db.session.add(ngo)

            file = request.files.get("document")
            if file and file.filename:
                name, path, size = save_uploaded_file(file, subfolder="organizations")
                db.session.add(OrganizationDocument(organization_id=org.id, document_type="Registration Document",
                                                     file_name=name, file_path=path, file_size=size))
            db.session.commit()

            auth_service.create_user(f["authorized_rep"], f["official_email"], f["password"],
                                      "NGO_ADMIN", organization_id=org.id)
            flash("NGO registration submitted. Government verification is pending.", "success")
            return redirect(url_for("auth.login"))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please check the form and try again.", "danger")
    return render_template("auth/register_ngo.html")


# --------------------------------------------------------------------------
# Student registration
# --------------------------------------------------------------------------
@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    universities = University.query.join(University.organization).filter_by(status="VERIFIED").all()
    if request.method == "POST":
        f = request.form
        try:
            user = auth_service.create_user(f["full_name"], f["college_email"], f["password"], "STUDENT",
                                              phone=f.get("phone"))
            profile = student_service.activate_student_on_registration(
                user, int(f["institution_id"]), f["registration_number"]
            )
            profile.department = f.get("department")
            profile.course = f.get("course")
            profile.year = f.get("year")
            db.session.commit()

            skills = [s.strip() for s in f.get("skills", "").split(",") if s.strip()]
            from database.models import StudentSkill, StudentInterest
            for s in skills:
                db.session.add(StudentSkill(student_id=profile.id, skill_name=s))
            interests = [s.strip() for s in f.get("interests", "").split(",") if s.strip()]
            for s in interests:
                db.session.add(StudentInterest(student_id=profile.id, interest_name=s))
            db.session.commit()

            session["user_id"] = user.id
            flash("Welcome to YugKrit! Your innovation journey starts now.", "success")
            return redirect(url_for("student.overview"))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception:
            db.session.rollback()
            flash("Registration failed. Please check the form and try again.", "danger")
    return render_template("auth/register_student.html", universities=universities)
