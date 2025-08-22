#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Content Quality Validator
Validador de qualidade de conteúdo extraído
"""

import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ContentQualityValidator:
    """Validador de qualidade de conteúdo"""

    def __init__(self):
        """Inicializa o validador"""
        self.min_content_length = 100
        self.quality_thresholds = {
            'excellent': 90,
            'good': 70,
            'fair': 50,
            'poor': 30
        }
        
        logger.info("✅ Content Quality Validator inicializado")

    def validate_content(self, content: str, url: str) -> Dict[str, Any]:
        """Valida qualidade do conteúdo extraído"""
        if not content:
            return {
                'valid': False,
                'quality_score': 0,
                'quality_level': 'invalid',
                'issues': ['Conteúdo vazio'],
                'url': url
            }

        validation_result = {
            'valid': True,
            'quality_score': 0,
            'quality_level': 'poor',
            'issues': [],
            'strengths': [],
            'url': url,
            'content_length': len(content),
            'word_count': len(content.split())
        }

        # Testes de qualidade
        score = 0
        
        # 1. Comprimento adequado (25 pontos)
        if len(content) >= 2000:
            score += 25
            validation_result['strengths'].append('Conteúdo extenso')
        elif len(content) >= 1000:
            score += 20
            validation_result['strengths'].append('Conteúdo substancial')
        elif len(content) >= 500:
            score += 15
        elif len(content) >= self.min_content_length:
            score += 10
        else:
            validation_result['issues'].append('Conteúdo muito curto')

        # 2. Densidade de informação (25 pontos)
        words = content.split()
        if len(words) >= 300:
            score += 25
            validation_result['strengths'].append('Alta densidade de palavras')
        elif len(words) >= 150:
            score += 20
        elif len(words) >= 75:
            score += 15
        else:
            validation_result['issues'].append('Baixa densidade de palavras')

        # 3. Presença de dados estruturados (20 pontos)
        data_patterns = [
            r'\d+%',  # Percentuais
            r'R\$\s*[\d,\.]+',  # Valores monetários
            r'\d+\s*(mil|milhão|bilhão)',  # Números grandes
            r'20(2[3-9]|[3-9]\d)',  # Anos recentes
            r'\d+\s*(empresas|clientes|usuários)'  # Quantidades
        ]
        
        data_matches = 0
        for pattern in data_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            data_matches += matches
        
        if data_matches >= 10:
            score += 20
            validation_result['strengths'].append('Rico em dados numéricos')
        elif data_matches >= 5:
            score += 15
        elif data_matches >= 2:
            score += 10
        else:
            validation_result['issues'].append('Poucos dados estruturados')

        # 4. Qualidade da fonte (15 pontos)
        domain = urlparse(url).netloc.lower()
        
        if any(trusted in domain for trusted in [
            'gov.br', 'edu.br', 'org.br', 'ibge.gov.br', 'sebrae.com.br'
        ]):
            score += 15
            validation_result['strengths'].append('Fonte oficial/confiável')
        elif any(news in domain for news in [
            'g1.globo.com', 'exame.com', 'valor.globo.com', 'estadao.com.br'
        ]):
            score += 12
            validation_result['strengths'].append('Fonte jornalística confiável')
        elif domain.endswith('.com.br'):
            score += 8
        else:
            score += 5

        # 5. Relevância do conteúdo (15 pontos)
        relevance_keywords = [
            'mercado', 'negócio', 'empresa', 'crescimento', 'oportunidade',
            'tendência', 'análise', 'dados', 'pesquisa', 'estudo'
        ]
        
        content_lower = content.lower()
        relevance_matches = sum(1 for keyword in relevance_keywords 
                              if keyword in content_lower)
        
        if relevance_matches >= 8:
            score += 15
            validation_result['strengths'].append('Altamente relevante')
        elif relevance_matches >= 5:
            score += 12
        elif relevance_matches >= 3:
            score += 8
        else:
            validation_result['issues'].append('Baixa relevância temática')

        # Determina nível de qualidade
        validation_result['quality_score'] = score
        
        if score >= self.quality_thresholds['excellent']:
            validation_result['quality_level'] = 'excellent'
        elif score >= self.quality_thresholds['good']:
            validation_result['quality_level'] = 'good'
        elif score >= self.quality_thresholds['fair']:
            validation_result['quality_level'] = 'fair'
        else:
            validation_result['quality_level'] = 'poor'

        # Valida se atende critérios mínimos
        validation_result['valid'] = (
            len(content) >= self.min_content_length and
            score >= self.quality_thresholds['poor']
        )

        return validation_result

    def validate_batch(self, content_dict: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Valida múltiplos conteúdos em lote"""
        results = {}
        
        for url, content in content_dict.items():
            results[url] = self.validate_content(content, url)
        
        return results

    def get_validation_summary(self, validations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Gera resumo das validações"""
        total = len(validations)
        valid_count = sum(1 for v in validations.values() if v['valid'])
        
        quality_distribution = {}
        for validation in validations.values():
            level = validation['quality_level']
            quality_distribution[level] = quality_distribution.get(level, 0) + 1

        avg_score = sum(v['quality_score'] for v in validations.values()) / total if total > 0 else 0

        return {
            'total_validated': total,
            'valid_content': valid_count,
            'invalid_content': total - valid_count,
            'success_rate': (valid_count / total * 100) if total > 0 else 0,
            'average_quality_score': round(avg_score, 2),
            'quality_distribution': quality_distribution,
            'extractor_stats': self.get_extractor_stats()
        }

    def get_extractor_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do extrator"""
        return self.stats.copy()

# Instância global
content_quality_validator = ContentQualityValidator()