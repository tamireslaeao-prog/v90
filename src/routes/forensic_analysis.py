#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Forensic Analysis Routes
Rotas para análise forense com dados reais
"""

import logging
import time
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.enhanced_ai_manager import enhanced_ai_manager
from services.auto_save_manager import salvar_etapa

logger = logging.getLogger(__name__)

forensic_bp = Blueprint('forensic', __name__)

@forensic_bp.route('/execute_forensic', methods=['POST'])
def execute_forensic_analysis():
    """Executa análise forense com dados reais"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Dados da requisição são obrigatórios"}), 400

        # Gera session_id único
        session_id = f"forensic_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

        # Extrai parâmetros
        segmento = data.get('segmento', '').strip()
        produto = data.get('produto', '').strip()
        
        if not segmento:
            return jsonify({"error": "Segmento é obrigatório"}), 400

        # Contexto da análise forense
        context = {
            "segmento": segmento,
            "produto": produto,
            "publico": data.get('publico', '').strip(),
            "analysis_type": "forensic",
            "methodology": "REAL_DATA_FORENSIC"
        }

        # Salva início da análise forense
        salvar_etapa("forensic_analysis_started", {
            "session_id": session_id,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }, categoria="forensic")

        # Executa análise forense em background
        def execute_forensic():
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Busca dados reais para análise forense
                    from services.real_search_orchestrator import real_search_orchestrator
                    
                    search_results = loop.run_until_complete(
                        real_search_orchestrator.execute_massive_real_search(
                            query=f"{segmento} {produto} análise forense mercado",
                            context=context,
                            session_id=session_id
                        )
                    )
                    
                    # Análise forense com IA
                    forensic_prompt = f"""
                    Realize uma análise FORENSE ultra-detalhada do mercado de {segmento}.
                    
                    DADOS COLETADOS:
                    {json.dumps(search_results, indent=2)[:5000]}
                    
                    ANÁLISE FORENSE OBRIGATÓRIA:
                    1. Dissecação completa do mercado
                    2. Identificação de padrões ocultos
                    3. Análise de vulnerabilidades competitivas
                    4. Mapeamento de oportunidades não exploradas
                    5. Predições baseadas em evidências
                    
                    RETORNE JSON estruturado com análise forense completa.
                    """
                    
                    forensic_analysis = loop.run_until_complete(
                        enhanced_ai_manager.generate_with_active_search(
                            prompt=forensic_prompt,
                            context=json.dumps(search_results)[:3000],
                            session_id=session_id
                        )
                    )
                    
                    # Salva resultado forense
                    salvar_etapa("forensic_analysis_complete", {
                        "session_id": session_id,
                        "search_results": search_results,
                        "forensic_analysis": forensic_analysis,
                        "timestamp": datetime.now().isoformat()
                    }, categoria="forensic")
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"❌ Erro na execução forense: {e}")
                salvar_etapa("forensic_analysis_error", {
                    "session_id": session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }, categoria="forensic")

        # Inicia execução em background
        import threading
        thread = threading.Thread(target=execute_forensic, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Análise forense iniciada com dados reais",
            "methodology": "REAL_DATA_FORENSIC",
            "estimated_duration": "5-8 minutos",
            "status_endpoint": f"/forensic/status/{session_id}"
        }), 200

    except Exception as e:
        logger.error(f"❌ Erro na rota forense: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@forensic_bp.route('/status/<session_id>', methods=['GET'])
def get_forensic_status(session_id):
    """Obtém status da análise forense"""
    try:
        # Verifica se análise foi concluída
        import os
        
        if os.path.exists(f"relatorios_intermediarios/forensic/forensic_analysis_complete*{session_id}*"):
            return jsonify({
                "session_id": session_id,
                "status": "completed",
                "message": "Análise forense concluída",
                "timestamp": datetime.now().isoformat()
            }), 200
        elif os.path.exists(f"relatorios_intermediarios/forensic/forensic_analysis_started*{session_id}*"):
            return jsonify({
                "session_id": session_id,
                "status": "running",
                "message": "Análise forense em andamento",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "session_id": session_id,
                "status": "not_found",
                "message": "Sessão não encontrada",
                "timestamp": datetime.now().isoformat()
            }), 404

    except Exception as e:
        logger.error(f"❌ Erro ao obter status forense: {e}")
        return jsonify({
            "session_id": session_id,
            "status": "error",
            "error": str(e)
        }), 500