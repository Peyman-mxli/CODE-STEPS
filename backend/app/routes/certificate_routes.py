from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.certificate import Certificate
from app.models.course import Course
from app.models.user import User

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

import io


certificate_bp = Blueprint("certificates", __name__)


# ------------------------------------------------
# GET MY CERTIFICATES
# ------------------------------------------------
@certificate_bp.route("/api/my-certificates", methods=["GET"])
@jwt_required()
def my_certificates():

    user_id = get_jwt_identity()

    certs = Certificate.query.filter_by(user_id=user_id).all()

    result = []

    for cert in certs:

        course = Course.query.get(cert.course_id)

        result.append({
            "certificate_id": cert.certificate_id,
            "course_id": cert.course_id,
            "course_title": course.title if course else "Unknown Course",
            "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
            "download_url": f"/api/certificate/download/{cert.certificate_id}",
            "verify_url": f"/api/certificate/{cert.certificate_id}"
        })

    return jsonify(result), 200


# ------------------------------------------------
# VERIFY CERTIFICATE (PUBLIC)
# ------------------------------------------------
@certificate_bp.route("/api/certificate/<certificate_id>", methods=["GET"])
def verify_certificate(certificate_id):

    cert = Certificate.query.filter_by(
        certificate_id=certificate_id
    ).first()

    if not cert:
        return jsonify({
            "error": "Certificate not found"
        }), 404

    course = Course.query.get(cert.course_id)
    user = User.query.get(cert.user_id)

    return jsonify({
        "certificate_id": cert.certificate_id,
        "student": user.username if user else "Unknown",
        "course_id": cert.course_id,
        "course_title": course.title if course else "Unknown Course",
        "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
        "status": "valid"
    }), 200


# ------------------------------------------------
# DOWNLOAD CERTIFICATE PDF
# ------------------------------------------------
@certificate_bp.route("/api/certificate/download/<certificate_id>", methods=["GET"])
@jwt_required()
def download_certificate(certificate_id):

    user_id = get_jwt_identity()

    cert = Certificate.query.filter_by(
        certificate_id=certificate_id
    ).first()

    if not cert:
        return jsonify({"error": "Certificate not found"}), 404

    # prevent downloading other users certificates
    if cert.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(cert.user_id)
    course = Course.query.get(cert.course_id)

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # -----------------------------------
    # Certificate Title
    # -----------------------------------
    pdf.setFont("Helvetica-Bold", 32)
    pdf.drawCentredString(
        width / 2,
        height - 2 * inch,
        "Certificate of Completion"
    )

    # Subtitle
    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        width / 2,
        height - 2.8 * inch,
        "This certifies that"
    )

    # Student name
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2,
        height - 3.6 * inch,
        user.username if user else "Student"
    )

    # Completion text
    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        width / 2,
        height - 4.4 * inch,
        "has successfully completed"
    )

    # Course title
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(
        width / 2,
        height - 5.2 * inch,
        course.title if course else "Course"
    )

    # Certificate ID
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        width / 2,
        height - 6.4 * inch,
        f"Certificate ID: {cert.certificate_id}"
    )

    # Issue date
    if cert.issued_at:
        pdf.drawCentredString(
            width / 2,
            height - 6.8 * inch,
            f"Issued: {cert.issued_at.strftime('%Y-%m-%d')}"
        )

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{cert.certificate_id}.pdf",
        mimetype="application/pdf"
    )