import json
import os

def ordenar_e_salvar(arquivo_entrada):
    """Lê, ordena por ID e salva temporariamente"""
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Ordenar por ID
    dados_ordenados = sorted(dados, key=lambda x: x['id'])
    
    # Salvar temporariamente
    arquivo_temp = arquivo_entrada.replace('.json', '_temp.json')
    with open(arquivo_temp, 'w', encoding='utf-8') as f:
        json.dump(dados_ordenados, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {arquivo_entrada} ordenado e salvo como {arquivo_temp}")
    return arquivo_temp

# Arquivos para ordenar
arquivos = [
    'app/data/allCharsUpdated (3) (2).json',
    'app/data/allEpisodesUpdated (1).json',
    'app/data/allLocations (1).json'
]

print("🔄 Ordenando JSONs...")
for arquivo in arquivos:
    ordenar_e_salvar(arquivo)
print("\n✅ JSONs temporários criados! Agora execute o seed.")