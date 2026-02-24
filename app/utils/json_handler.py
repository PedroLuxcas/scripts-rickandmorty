import json
import os

class JSONHandler:
    def __init__(self, pasta_data='data'):
        # Caminho para a pasta data
        self.pasta_data = os.path.join(os.path.dirname(__file__), '..', pasta_data)
    
    def ler_json(self, nome_arquivo):
        """Lê um arquivo JSON e retorna os dados"""
        caminho = os.path.join(self.pasta_data, nome_arquivo)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Arquivo {nome_arquivo} não encontrado em {caminho}!")
            return None
        except json.JSONDecodeError:
            print(f"Erro ao decodificar {nome_arquivo}!")
            return None
    
    def salvar_json(self, dados, nome_arquivo):
        """Salva dados em um arquivo JSON"""
        caminho = os.path.join(self.pasta_data, nome_arquivo)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        print(f"Dados salvos em {caminho}")
    
    def estatisticas_personagens(self):
        """Analisa estatísticas dos personagens"""
        personagens = self.ler_json('allCharsUpdated (3) (2).json')
        if not personagens:
            return {}
        
        stats = {
            'total': len(personagens),
            'vivos': 0,
            'humanos': 0,
            'por_genero': {},
            'por_especie': {}
        }
        
        for p in personagens:
            if p.get('status') == 'Alive':
                stats['vivos'] += 1
            if p.get('species') == 'Human':
                stats['humanos'] += 1
            
            genero = p.get('gender', 'Desconhecido')
            stats['por_genero'][genero] = stats['por_genero'].get(genero, 0) + 1
            
            especie = p.get('species', 'Desconhecida')
            stats['por_especie'][especie] = stats['por_especie'].get(especie, 0) + 1
        
        return stats
    
    def buscar_personagem(self, nome):
        """Busca personagem por nome"""
        personagens = self.ler_json('allCharsUpdated (3) (2).json')
        if not personagens:
            return []
        return [p for p in personagens if nome.lower() in p.get('name', '').lower()]