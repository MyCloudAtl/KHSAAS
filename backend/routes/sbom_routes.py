from flask import Blueprint
from controllers.sbom_controller import get_sbom_controller

sbom_bp = Blueprint('sbom', __name__)

sbom_bp.route('/sbom', methods=['POST'])(get_sbom_controller)
