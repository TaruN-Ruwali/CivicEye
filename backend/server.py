from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
from pathlib import Path

# Import backend modules
from backend import model, auth, utils
from backend.config import SECRET_KEY, POTHOLE_MODEL_PATH
from backend.ai.detector_manager import run_all, run_all_for_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent

# --- App Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT_DIR, "frontend")
STATIC_DIR = os.path.join(ROOT_DIR, "frontend")

def create_app():
    app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
    CORS(app)
    app.config["SECRET_KEY"] = SECRET_KEY
    model.init_db()
    model.migrate_db()
    utils.ensure_upload_dir()

    # --- Routes ---

    @app.route("/")
    def home():
        return send_from_directory(TEMPLATES_DIR, "login.html")

    @app.route("/<path:filename>")
    def serve_static(filename):
        return send_from_directory(STATIC_DIR, filename)

    @app.route("/user")
    def serve_user():
        return send_from_directory(TEMPLATES_DIR, "submit.html")

    @app.route("/user/user")
    def serve_user_alias():
        return send_from_directory(TEMPLATES_DIR, "submit.html")

    @app.route("/admin")
    def serve_admin():
        return send_from_directory(TEMPLATES_DIR, "admin.html")

    @app.route("/admin/admin")
    def serve_admin_alias():
        return send_from_directory(TEMPLATES_DIR, "admin.html")

    # --- Auth Routes ---

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")
        if not email or not password:
            return jsonify({"ok": False, "error": "Missing credentials"}), 400
        res = auth.register_user(name, email, password, role)
        code = 200 if res["ok"] else 400
        return jsonify(res), code

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"ok": False, "error": "Missing credentials"}), 400
        res = auth.login_user(email, password)
        code = 200 if res["ok"] else 401
        return jsonify(res), code

    # --- Complaint Routes ---

    @app.route("/complaint/register", methods=["POST"])
    def register_complaint():
        """
        Register a new complaint.
        """
        try:
            # Get form data
            user_id = request.form.get("user_id")
            complaint_type = request.form.get("complaint_type", "garbage")
            address = request.form.get("address")
            description = request.form.get("description", "")
            
            if not user_id:
                return jsonify({"ok": False, "error": "Missing user_id"}), 400
            if not address:
                return jsonify({"ok": False, "error": "Missing address"}), 400
            
            # Handle image upload
            image_path = None
            if "image" in request.files:
                file = request.files["image"]
                if file and file.filename:
                    if not utils.allowed_file(file.filename):
                        return jsonify({"ok": False, "error": "Invalid file type"}), 400
                    image_path = utils.save_upload(file, "complaint")
            
            # Save complaint to database
            complaint_id = model.save_complaint(
                user_id=int(user_id),
                image_path=image_path,
                address=address,
                description=description,
                complaint_type=complaint_type
            )
            
            ai_result_text = None
            if image_path:
                try:
                    # Convert Path to string and properly join paths
                    abs_image_path = str(ROOT_DIR / image_path)
                    # Verify file exists before processing
                    if not os.path.exists(abs_image_path):
                        logger.error(f"Image file not found: {abs_image_path}")
                        model.update_complaint_ai_result(complaint_id, f"AI Error: Image file not found at {abs_image_path}")
                    else:
                        logger.info(f"=== Triggering AI Detection for Complaint {complaint_id} ===")
                        logger.info(f"Image path: {abs_image_path}")
                        
                        # Run all detectors sequentially
                        dets, final = run_all(abs_image_path)
                        
                        # Save individual detector results
                        for d in dets:
                            det_type = d.get("detected_type")
                            det_conf = d.get("confidence", 0.0)
                            det_model = d.get("detector_name")
                            if det_type or det_conf > 0:
                                model.save_ai_detection(complaint_id, det_type, det_conf, det_model, None)
                        
                        # Get final decision
                        label = final.get("detected_type") or "unknown"
                        confidence = float(final.get("confidence", 0.0) or 0.0)
                        error = final.get("error")
                        
                        # Format result text
                        if error:
                            if "model missing" in str(error).lower() or "no detectors available" in str(error).lower():
                                ai_result_text = f"AI Models Missing - Please add model.pt files to detector folders"
                            else:
                                ai_result_text = f"AI Error: {error}"
                        elif label == "unknown":
                            ai_result_text = f"No detection (confidence below threshold or models missing)"
                        else:
                            ai_result_text = f"Detected: {label.replace('_', ' ').title()} ({round(confidence * 100, 1)}%)"
                        
                        # Save final detection result
                        model.save_ai_detection(
                            complaint_id, 
                            label if label != "unknown" else None,
                            confidence if label != "unknown" else 0.0,
                            final.get("detector_name"),
                            ai_result_text
                        )
                        
                        logger.info(f"AI Detection complete: {label} ({confidence:.2%})")
                        logger.info(f"=== AI Detection Complete for Complaint {complaint_id} ===")
                except Exception as ai_e:
                    logger.error(f"AI processing error: {ai_e}", exc_info=True)
                    model.update_complaint_ai_result(complaint_id, f"AI Error: {str(ai_e)}")
            
            return jsonify({"ok": True, "complaint_id": complaint_id})
            
        except Exception as e:
            logger.error(f"Complaint registration error: {e}", exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/complaint/status/<user_id>", methods=["GET"])
    def get_user_complaints_status(user_id):
        try:
            items = model.get_user_complaints(int(user_id))
            # Format items for frontend if necessary (currently model returns dicts)
            return jsonify({"ok": True, "complaints": items})
        except Exception as e:
             return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/complaint/create", methods=["POST"])
    def api_create_complaint():
        try:
            user_id = request.form.get("user_id")
            complaint_type = request.form.get("complaint_type", "garbage")
            address = request.form.get("address")
            description = request.form.get("description", "")
            if not user_id:
                return jsonify({"ok": False, "error": "Missing user_id"}), 400
            if not address:
                return jsonify({"ok": False, "error": "Missing address"}), 400
            image_path = None
            if "image" in request.files:
                file = request.files["image"]
                if file and file.filename:
                    if not utils.allowed_file(file.filename):
                        return jsonify({"ok": False, "error": "Invalid file type"}), 400
                    image_path = utils.save_upload(file, "complaint")
            complaint_id = model.save_complaint(
                user_id=int(user_id),
                image_path=image_path,
                address=address,
                description=description,
                complaint_type=complaint_type
            )
            # Trigger AI detection automatically after image upload
            if image_path:
                try:
                    # Convert Path to string and properly join paths
                    abs_image_path = str(ROOT_DIR / image_path)
                    # Verify file exists before processing
                    if not os.path.exists(abs_image_path):
                        logger.error(f"Image file not found: {abs_image_path}")
                        model.update_complaint_ai_result(complaint_id, f"AI Error: Image file not found at {abs_image_path}")
                    else:
                        logger.info(f"=== Triggering AI Detection for Complaint {complaint_id} ===")
                        logger.info(f"Image path: {abs_image_path}")
                        
                        # Run all detectors sequentially
                        dets, final = run_all(abs_image_path)
                        
                        # Save individual detector results
                        for d in dets:
                            det_type = d.get("detected_type")
                            det_conf = d.get("confidence", 0.0)
                            det_model = d.get("detector_name")
                            if det_type or det_conf > 0:
                                model.save_ai_detection(complaint_id, det_type, det_conf, det_model, None)
                        
                        # Get final decision
                        label = final.get("detected_type") or "unknown"
                        confidence = float(final.get("confidence", 0.0) or 0.0)
                        error = final.get("error")
                        
                        # Format result text
                        if error:
                            if "model missing" in str(error).lower() or "no detectors available" in str(error).lower():
                                ai_result_text = f"AI Models Missing - Please add model.pt files to detector folders"
                            else:
                                ai_result_text = f"AI Error: {error}"
                        elif label == "unknown":
                            ai_result_text = f"No detection (confidence below threshold or models missing)"
                        else:
                            ai_result_text = f"Detected: {label.replace('_', ' ').title()} ({round(confidence * 100, 1)}%)"
                        
                        # Save final detection result
                        model.save_ai_detection(
                            complaint_id, 
                            label if label != "unknown" else None,
                            confidence if label != "unknown" else 0.0,
                            final.get("detector_name"),
                            ai_result_text
                        )
                        
                        logger.info(f"AI Detection complete: {label} ({confidence:.2%})")
                        logger.info(f"=== AI Detection Complete for Complaint {complaint_id} ===")
                except Exception as ai_e:
                    logger.error(f"AI processing error for complaint {complaint_id}: {ai_e}", exc_info=True)
                    model.update_complaint_ai_result(complaint_id, f"AI Error: {str(ai_e)}")
            return jsonify({"ok": True, "complaint_id": complaint_id})
        except Exception as e:
            logger.error(f"Create complaint error: {e}", exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/complaint/<int:complaint_id>", methods=["GET"])
    def api_get_complaint(complaint_id: int):
        item = model.get_complaint_with_ai_result(int(complaint_id))
        if not item:
            return jsonify({"ok": False, "error": "Not found"}), 404
        return jsonify({"ok": True, "item": item})

    @app.route("/my_complaints", methods=["GET"])
    def my_complaints():
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"ok": False, "error": "Missing user_id"}), 400
        items = model.get_user_complaints(int(user_id))
        return jsonify({"ok": True, "items": items})

    # --- Admin Routes ---

    @app.route("/admin/complaints", methods=["GET"])
    def admin_complaints():
        items = model.get_all_complaints()
        return jsonify({"ok": True, "items": items})

    @app.route("/admin/update_status", methods=["POST"])
    def admin_update_status():
        data = request.get_json() or {}
        complaint_id = data.get("complaint_id")
        status = data.get("status")
        admin_id = data.get("admin_id")
        if not complaint_id or not status or not admin_id:
            return jsonify({"ok": False, "error": "Missing fields"}), 400
        
        # Verify admin
        if not auth.is_admin(int(admin_id)):
            return jsonify({"ok": False, "error": "Forbidden"}), 403
            
        ok = model.update_complaint_status(int(complaint_id), status)
        return jsonify({"ok": ok})

    # --- AI Decision APIs ---
    @app.route("/admin/complaint/<int:complaint_id>/ai-result", methods=["GET"])
    def get_ai_result(complaint_id: int):
        """
        Get AI result for a complaint. If AI hasn't run yet, trigger it automatically.
        """
        item = model.get_complaint_with_ai_result(complaint_id)
        if not item:
            return jsonify({"ok": False, "error": "Complaint not found"}), 404
        
        # If AI hasn't been run yet (no ai_detected_type or ai_confidence is None), trigger it
        image_path = item.get("image_path")
        detections_list = []
        
        if image_path and (not item.get("ai_detected_type") or item.get("ai_confidence") is None):
            try:
                abs_image_path = str(ROOT_DIR / image_path)
                if os.path.exists(abs_image_path):
                    logger.info(f"Auto-triggering AI detection for complaint {complaint_id} (no previous result)")
                    dets, final = run_all(abs_image_path)
                    
                    # Save individual detector results and collect for response
                    for d in dets:
                        det_type = d.get("detected_type")
                        det_conf = d.get("confidence", 0.0)
                        det_model = d.get("detector_name")
                        raw = d.get("raw", {})
                        
                        detections_list.append({
                            "detected_type": det_type,
                            "confidence": det_conf,
                            "detector_name": det_model,
                            "label": raw.get("label"),  # What object was actually detected
                            "raw_detections": raw.get("raw_detections", 0)
                        })
                        
                        if det_type or det_conf > 0:
                            model.save_ai_detection(complaint_id, det_type, det_conf, det_model, None)
                    
                    # Get final decision
                    label = final.get("detected_type") or "unknown"
                    confidence = float(final.get("confidence", 0.0) or 0.0)
                    error = final.get("error")
                    
                    # Format result text
                    if error:
                        if "model missing" in str(error).lower() or "no detectors available" in str(error).lower():
                            ai_result_text = f"AI Models Missing - Please add model.pt files to detector folders"
                        else:
                            ai_result_text = f"AI Error: {error}"
                    elif label == "unknown":
                        ai_result_text = f"No detection (confidence below threshold or models missing)"
                    else:
                        ai_result_text = f"Detected: {label.replace('_', ' ').title()} ({round(confidence * 100, 1)}%)"
                    
                    # Save final detection result
                    model.save_ai_detection(
                        complaint_id, 
                        label if label != "unknown" else None,
                        confidence if label != "unknown" else 0.0,
                        final.get("detector_name"),
                        ai_result_text
                    )
                    
                    # Refresh item from database
                    item = model.get_complaint_with_ai_result(complaint_id)
                    item["detections"] = detections_list
            except Exception as e:
                logger.error(f"Error auto-triggering AI detection: {e}", exc_info=True)
        
        # Add detections to response if available
        if detections_list:
            item["detections"] = detections_list
        
        return jsonify({"ok": True, "item": item})

    @app.route("/admin/complaint/<int:complaint_id>/decision", methods=["POST"])
    def post_ai_decision(complaint_id: int):
        try:
            data = request.get_json() or {}
            status = data.get("ai_status")  # 'verified' | 'rejected' | 'pending'
            override_type = data.get("override_type")  # optional new type
            admin_id = data.get("admin_id")
            
            logger.info(f"Decision update request - complaint_id: {complaint_id}, admin_id: {admin_id}, status: {status}")
            
            if not status or not admin_id:
                logger.warning(f"Missing fields - status: {status}, admin_id: {admin_id}")
                return jsonify({"ok": False, "error": "Missing fields"}), 400
            
            # Convert admin_id to int (localStorage returns strings)
            try:
                admin_id_int = int(admin_id)
            except (ValueError, TypeError):
                logger.error(f"Invalid admin_id format: {admin_id}")
                return jsonify({"ok": False, "error": "Invalid admin_id format"}), 400
            
            # Check if user exists and is admin
            user = model.get_user_by_id(admin_id_int)
            if not user:
                logger.warning(f"User not found: {admin_id_int}")
                return jsonify({"ok": False, "error": "User not found"}), 404
            
            logger.info(f"User found - id: {user['id']}, role: {user.get('role')}")
            
            if not auth.is_admin(admin_id_int):
                logger.warning(f"User {admin_id_int} is not an admin. Role: {user.get('role')}")
                return jsonify({"ok": False, "error": "Forbidden: Admin access required"}), 403
            
            ok = model.update_ai_decision(complaint_id, status, override_type, admin_id_int)
            if ok:
                logger.info(f"Successfully updated decision for complaint {complaint_id}")
            else:
                logger.warning(f"Failed to update decision for complaint {complaint_id}")
            return jsonify({"ok": ok})
        except Exception as e:
            logger.error(f"Error in post_ai_decision: {e}", exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/ai/result/<int:complaint_id>", methods=["GET"])
    def api_ai_result(complaint_id: int):
        item = model.get_complaint_with_ai_result(int(complaint_id))
        if not item:
            return jsonify({"ok": False, "error": "Not found"}), 404
        return jsonify({"ok": True, "item": item})

    @app.route("/api/detect/run-all", methods=["POST"])
    def api_run_all():
        data = request.get_json() or {}
        complaint_id = data.get("complaint_id")
        admin_id = data.get("admin_id")
        if not complaint_id:
            return jsonify({"ok": False, "error": "Missing complaint_id"}), 400
        if admin_id and not auth.is_admin(int(admin_id)):
            return jsonify({"ok": False, "error": "Forbidden"}), 403
        item = model.get_complaint_with_ai_result(int(complaint_id))
        if not item:
            return jsonify({"ok": False, "error": "Not found"}), 404
        image_path = item.get("image_path")
        if not image_path:
            return jsonify({"ok": False, "error": "No image"}), 400
        try:
            # Convert Path to string and properly join paths
            abs_image_path = str(ROOT_DIR / image_path)
            # Verify file exists before processing
            if not os.path.exists(abs_image_path):
                logger.error(f"Image file not found: {abs_image_path}")
                return jsonify({"ok": False, "error": f"Image file not found at {abs_image_path}"}), 400
            logger.info(f"Processing AI detection for image: {abs_image_path}")
            dets, final = run_all(abs_image_path)
            for d in dets:
                model.save_ai_detection(int(complaint_id), d.get("detected_type"), d.get("confidence"), d.get("detector_name"), None)
            label = final.get("detected_type") or "unknown"
            confidence = float(final.get("confidence", 0.0))
            ai_result_text = f"Detected: {label.replace('_', ' ').title()} ({round(confidence * 100, 1)}%)"
            model.save_ai_detection(int(complaint_id), label, confidence, final.get("detector_name"), ai_result_text)
            if confidence > 0:
                model.update_complaint_ai_info(int(complaint_id), True, label, confidence)
            else:
                model.update_complaint_ai_info(int(complaint_id), False, None, 0.0)
            model.update_complaint_ai_result(int(complaint_id), ai_result_text)
            return jsonify({"ok": True, "final": final, "detections": dets})
        except Exception as e:
            logger.error(f"Run-all error: {e}", exc_info=True)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/ai/run-detectors", methods=["POST"])
    def api_run_detectors():
        data = request.get_json() or {}
        complaint_id = data.get("complaint_id")
        admin_id = data.get("admin_id")
        if not complaint_id:
            return jsonify({"ok": False, "error": "Missing complaint_id"}), 400
        if admin_id and not auth.is_admin(int(admin_id)):
            return jsonify({"ok": False, "error": "Forbidden"}), 403
        item = model.get_complaint_with_ai_result(int(complaint_id))
        if not item:
            return jsonify({"ok": False, "error": "Not found"}), 404
        image_path = item.get("image_path")
        if not image_path:
            return jsonify({"ok": False, "error": "No image"}), 400
        # Convert Path to string and properly join paths
        abs_image_path = str(ROOT_DIR / image_path)
        # Verify file exists before processing
        if not os.path.exists(abs_image_path):
            logger.error(f"Image file not found: {abs_image_path}")
            return jsonify({"ok": False, "error": f"Image file not found at {abs_image_path}"}), 400
        logger.info(f"Processing AI detection for image: {abs_image_path}")
        res = run_all_for_api(abs_image_path)
        dets = res.get("detections", [])
        final = res.get("final", {})
        for d in dets:
            model.save_ai_detection(int(complaint_id), d.get("detected_type"), d.get("confidence"), d.get("detector_name"), None)
        label = final.get("detected_type") or "unknown"
        confidence = float(final.get("confidence", 0.0))
        ai_result_text = f"Detected: {label.replace('_', ' ').title()} ({round(confidence * 100, 1)}%)"
        model.save_ai_detection(int(complaint_id), label, confidence, final.get("detector_name"), ai_result_text)
        if confidence > 0:
            model.update_complaint_ai_info(int(complaint_id), True, label, confidence)
        else:
            model.update_complaint_ai_info(int(complaint_id), False, None, 0.0)
        model.update_complaint_ai_result(int(complaint_id), ai_result_text)
        return jsonify({"ok": True, "result": res.get("result"), "final": final, "detections": dets})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)
