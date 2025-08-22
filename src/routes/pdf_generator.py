#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - PDF Generator Routes
Geração de relatórios em PDF
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from pathlib import Path

logger = logging.getLogger(__name__)

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/generate/<session_id>', methods=['POST'])
def generate_pdf_report(session_id):
    """Gera relatório PDF da análise"""
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

        # Gera PDF usando reportlab
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Define caminho do PDF
            pdf_path = f"analyses_data/{session_id}/relatorio_final.pdf"
            
            # Cria documento PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor='#2563eb'
            )
            
            story.append(Paragraph(f"Relatório de Análise - Sessão {session_id}", title_style))
            story.append(Spacer(1, 12))
            
            # Converte markdown para PDF (versão simplificada)
            lines = markdown_content.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('#'):
                        # Cabeçalho
                        level = len(line) - len(line.lstrip('#'))
                        text = line.lstrip('# ').strip()
                        if level == 1:
                            style = styles['Heading1']
                        elif level == 2:
                            style = styles['Heading2']
                        else:
                            style = styles['Heading3']
                        story.append(Paragraph(text, style))
                        story.append(Spacer(1, 12))
                    else:
                        # Texto normal
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 6))
            
            # Gera PDF
            doc.build(story)
            
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"relatorio_analise_{session_id}.pdf"
            )
            
        except ImportError:
            # Fallback se reportlab não estiver disponível
            return jsonify({
                "success": False,
                "error": "Biblioteca de PDF não disponível. Use download em Markdown."
            }), 500

    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500