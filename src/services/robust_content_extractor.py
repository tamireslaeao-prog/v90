#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Robust Content Extractor
Extrator de conteúdo robusto com múltiplas estratégias - SEM SIMULAÇÃO
"""

import os
import logging
import time
import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class RobustContentExtractor:
    """Extrator de conteúdo robusto - APENAS DADOS REAIS"""

    def __init__(self):
        """Inicializa o extrator"""
        self.jina_api_key = os.getenv('JINA_API_KEY')
        self.session = requests.Session()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        
        self.session.headers.update(self.headers)
        
        # Estatísticas de extração
        self.stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'jina_successes': 0,
            'direct_successes': 0,
            'fallback_successes': 0
        }
        
        logger.info("🔍 Robust Content Extractor inicializado - APENAS DADOS REAIS")

    def extract_content(self, url: str) -> Optional[str]:
        """Extrai conteúdo REAL de uma URL"""
        if not url or not url.startswith(('http://', 'https://')):
            logger.warning(f"⚠️ URL inválida: {url}")
            return None

        self.stats['total_extractions'] += 1
        
        try:
            # Estratégia 1: Jina Reader (prioritária)
            if self.jina_api_key:
                content = self._extract_with_jina(url)
                if content and len(content.strip()) > 100:
                    self.stats['successful_extractions'] += 1
                    self.stats['jina_successes'] += 1
                    logger.info(f"✅ Jina: {len(content)} caracteres de {url}")
                    return content

            # Estratégia 2: Extração direta
            content = self._extract_direct(url)
            if content and len(content.strip()) > 100:
                self.stats['successful_extractions'] += 1
                self.stats['direct_successes'] += 1
                logger.info(f"✅ Direto: {len(content)} caracteres de {url}")
                return content

            # Estratégia 3: Fallback agressivo
            content = self._extract_fallback(url)
            if content and len(content.strip()) > 50:
                self.stats['successful_extractions'] += 1
                self.stats['fallback_successes'] += 1
                logger.info(f"✅ Fallback: {len(content)} caracteres de {url}")
                return content

            # Se chegou aqui, falhou
            self.stats['failed_extractions'] += 1
            logger.warning(f"⚠️ Falha em todas as estratégias para {url}")
            return None

        except Exception as e:
            self.stats['failed_extractions'] += 1
            logger.error(f"❌ Erro na extração de {url}: {e}")
            return None

    def _extract_with_jina(self, url: str) -> Optional[str]:
        """Extrai usando Jina Reader API"""
        try:
            headers = {
                **self.headers,
                "Authorization": f"Bearer {self.jina_api_key}"
            }
            
            jina_url = f"https://r.jina.ai/{url}"
            
            response = self.session.get(jina_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Limita tamanho para otimização
                if len(content) > 15000:
                    content = content[:15000] + "... [conteúdo truncado]"
                
                return content
            else:
                logger.warning(f"⚠️ Jina falhou para {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro Jina para {url}: {e}")
            return None

    def _extract_direct(self, url: str) -> Optional[str]:
        """Extração direta com BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=20, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Remove elementos desnecessários
                for element in soup(["script", "style", "nav", "footer", "header", 
                                   "form", "aside", "iframe", "noscript"]):
                    element.decompose()
                
                # Busca conteúdo principal
                main_content = (
                    soup.find('main') or 
                    soup.find('article') or 
                    soup.find('div', class_=re.compile(r'content|main|article|post')) or
                    soup.find('div', id=re.compile(r'content|main|article|post'))
                )
                
                if main_content:
                    text = main_content.get_text()
                else:
                    text = soup.get_text()
                
                # Limpa o texto
                text = self._clean_text(text)
                return text
                
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} para {url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro direto para {url}: {e}")
            return None

    def _extract_fallback(self, url: str) -> Optional[str]:
        """Extração de fallback mais agressiva"""
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Remove apenas elementos críticos
                for element in soup(["script", "style", "noscript"]):
                    element.decompose()
                
                # Pega todo o texto disponível
                text = soup.get_text()
                text = self._clean_text(text)
                
                return text if len(text) > 50 else None
                
        except Exception as e:
            logger.error(f"❌ Erro fallback para {url}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto extraído"""
        if not text:
            return ""

        # Remove quebras excessivas
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove linhas muito curtas (menu/navegação)
        lines = []
        for line in text.splitlines():
            line = line.strip()
            if len(line) > 10:  # Apenas linhas substanciais
                lines.append(line)
        
        cleaned_text = '\n'.join(lines)
        
        # Limita tamanho final
        if len(cleaned_text) > 12000:
            cleaned_text = cleaned_text[:12000] + "... [truncado]"
        
        return cleaned_text.strip()

    def batch_extract(self, urls: List[str], max_workers: int = 5) -> Dict[str, Optional[str]]:
        """Extração em lote com threading"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.extract_content, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result()
                    results[url] = content
                except Exception as e:
                    logger.error(f"❌ Erro em lote para {url}: {e}")
                    results[url] = None
        
        return results

    def get_extractor_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do extrator"""
        success_rate = 0
        if self.stats['total_extractions'] > 0:
            success_rate = (self.stats['successful_extractions'] / self.stats['total_extractions']) * 100
        
        return {
            **self.stats,
            'success_rate': round(success_rate, 2),
            'jina_available': bool(self.jina_api_key)
        }

    def clear_cache(self):
        """Limpa cache (placeholder para compatibilidade)"""
        logger.info("🧹 Cache limpo")
        return True

# Instância global
robust_content_extractor = RobustContentExtractor()