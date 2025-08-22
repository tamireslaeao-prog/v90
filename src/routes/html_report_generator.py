#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - HTML Report Generator Routes
Geração de relatórios em HTML
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template_string
from pathlib import Path

logger = logging.getLogger(__name__)

html_report_bp = Blueprint('html_report', __name__)

@html_report_bp.route('/generate/<session_id>', methods=['GET'])
def generate_html_report(session_id):
    """Gera relatório HTML da análise"""
    try:
        # Verifica se relatório existe
        report_path = f"analyses_data/{session_id}/relatorio_final.md"
        
        if not os.path.exists(report_path):
            return jsonify({
                "success": False,
                "error": "Relatório não encontrado para esta sessão"
            }), 404

        # Carrega conteúdo do relatório
        with open(report_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Template HTML básico
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Análise - {{ session_id }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }
        h2 { color: #1e40af; margin-top: 30px; }
        h3 { color: #3730a3; }
        .meta { background: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom: 30px; }
        .content { white-space: pre-wrap; }
        @media print {
            body { background: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Relatório de Análise ARQV30</h1>
        <div class="meta">
            <strong>Sessão:</strong> {{ session_id }}<br>
            <strong>Gerado em:</strong> {{ timestamp }}<br>
            <strong>Sistema:</strong> ARQV30 Enhanced v3.0
        </div>
        <div class="content">{{ content }}</div>
    </div>
</body>
</html>
        """

        # Renderiza template
        html_content = render_template_string(
            html_template,
            session_id=session_id,
            timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            content=markdown_content
        )

        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}

    except Exception as e:
        logger.error(f"❌ Erro ao gerar HTML: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500