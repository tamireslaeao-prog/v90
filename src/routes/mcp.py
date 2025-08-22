#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - MCP Routes
Rotas para integração com MCPs
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

mcp_bp = Blueprint('mcp', __name__)

@mcp_bp.route('/status', methods=['GET'])
def mcp_status():
    """Status dos MCPs disponíveis"""
    try:
        # Verifica status dos MCPs
        mcp_status = {
            'supadata': {
                'available': bool(os.getenv('SUPADATA_MCP_URL')),
                'status': 'configured' if os.getenv('SUPADATA_MCP_URL') else 'not_configured'
            },
            'trendfinder': {
                'available': bool(os.getenv('TRENDFINDER_MCP_URL')),
                'status': 'configured' if os.getenv('TRENDFINDER_MCP_URL') else 'not_configured'
            },
            'sequential_thinking': {
                'available': bool(os.getenv('MCP_SEQUENTIAL_THINKING_URL')),
                'status': 'configured' if os.getenv('MCP_SEQUENTIAL_THINKING_URL') else 'not_configured'
            }
        }
        
        return jsonify({
            "success": True,
            "mcp_status": mcp_status,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status MCP: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@mcp_bp.route('/test/<mcp_name>', methods=['POST'])
def test_mcp(mcp_name):
    """Testa conectividade com MCP específico"""
    try:
        data = request.get_json() or {}
        test_query = data.get('query', 'teste conectividade')
        
        # Testa MCP específico
        if mcp_name == 'supadata':
            from services.supadata_mcp_client import supadata_client
            import asyncio
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    supadata_client.search(test_query, "all")
                )
            finally:
                loop.close()
                
        elif mcp_name == 'trendfinder':
            from services.trendfinder_client import trendfinder_client
            import asyncio
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    trendfinder_client.search(test_query)
                )
            finally:
                loop.close()
                
        else:
            return jsonify({
                "success": False,
                "error": f"MCP {mcp_name} não reconhecido"
            }), 400
        
        return jsonify({
            "success": True,
            "mcp_name": mcp_name,
            "test_result": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar MCP {mcp_name}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "mcp_name": mcp_name
        }), 500