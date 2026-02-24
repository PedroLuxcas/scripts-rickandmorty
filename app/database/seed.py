import json
import os
from database.connection import DatabaseConnection
from database.models import TableCreator
from utils.json_handler import JSONHandler

class DataSeeder:
    def __init__(self):
        self.db = DatabaseConnection()
        self.json_handler = JSONHandler()
    
    def seed_database(self):
        cursor = self.db.connect()
        if not cursor:
            return
        
        try:
            # Criar tabelas
            TableCreator.create_tables(cursor)
            
            # Limpar tabelas existentes (ordem correta por causa das chaves estrangeiras)
            cursor.execute("TRUNCATE TABLE character_episodes RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE characters RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE episodes RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE locations RESTART IDENTITY CASCADE")
            
            # ============= SEED LOCATIONS (PRIMEIRO) =============
            print("\n--- Processando Localizações ---")
            locations = self.json_handler.ler_json('allLocations (1).json')
            location_map = {}  # URL -> ID
            
            if locations:
                # Ordenar locations por ID para inserir na ordem correta
                locations_ordenadas = sorted(locations, key=lambda x: x['id'])
                
                for loc in locations_ordenadas:
                    cursor.execute("""
                        INSERT INTO locations (
                            id, name, type, dimension, url, created, residents, data
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        loc['id'],  # Usa o ID original da API
                        loc.get('name'),
                        loc.get('type'),
                        loc.get('dimension'),
                        loc.get('url'),
                        loc.get('created'),
                        json.dumps(loc.get('residents', [])),
                        json.dumps(loc)
                    ))
                    
                    location_map[loc.get('url')] = loc['id']
                    
                print(f"✅ Inseridas {len(locations_ordenadas)} localizações")
                print(f"   IDs: {locations_ordenadas[0]['id']} até {locations_ordenadas[-1]['id']}")
            else:
                print("❌ Nenhuma localização encontrada!")
            
            # ============= SEED EPISODES (SEGUNDO) =============
            print("\n--- Processando Episódios ---")
            episodes = self.json_handler.ler_json('allEpisodesUpdated (1).json')
            episode_map = {}  # URL -> ID
            
            if episodes:
                # Ordenar episódios por ID
                episodes_ordenados = sorted(episodes, key=lambda x: x['id'])
                
                for ep in episodes_ordenados:
                    cursor.execute("""
                        INSERT INTO episodes (
                            id, name, air_date, episode, url, created, data
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        ep['id'],  # Usa o ID original da API
                        ep.get('name'),
                        ep.get('air_date'),
                        ep.get('episode'),
                        ep.get('url'),
                        ep.get('created'),
                        json.dumps(ep)
                    ))
                    
                    episode_map[ep.get('url')] = ep['id']
                    
                print(f"✅ Inseridos {len(episodes_ordenados)} episódios")
                print(f"   IDs: {episodes_ordenados[0]['id']} até {episodes_ordenados[-1]['id']}")
            else:
                print("❌ Nenhum episódio encontrado!")
            
            # ============= SEED CHARACTERS (TERCEIRO) =============
            print("\n--- Processando Personagens ---")
            characters = self.json_handler.ler_json('allCharsUpdated (3) (2).json')
            character_map = {}  # URL -> ID
            
            if characters:
                # Ordenar personagens por ID
                characters_ordenados = sorted(characters, key=lambda x: x['id'])
                
                for char in characters_ordenados:
                    # Pegar URLs das localizações
                    origin_data = char.get('origin', {})
                    location_data = char.get('location', {})
                    
                    origin_url = origin_data.get('url') if origin_data else None
                    location_url = location_data.get('url') if location_data else None
                    
                    # Buscar IDs das localizações no mapa
                    origin_id = location_map.get(origin_url) if origin_url and origin_url != '' else None
                    location_id = location_map.get(location_url) if location_url and location_url != '' else None
                    
                    cursor.execute("""
                        INSERT INTO characters (
                            id, name, status, species, type, gender,
                            image, url, created, 
                            origin_id, location_id,
                            origin, location, data
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        char['id'],  # Usa o ID original da API
                        char.get('name'),
                        char.get('status'),
                        char.get('species'),
                        char.get('type', ''),
                        char.get('gender'),
                        char.get('image'),
                        char.get('url'),
                        char.get('created'),
                        origin_id,
                        location_id,
                        json.dumps(origin_data),
                        json.dumps(location_data),
                        json.dumps(char)
                    ))
                    
                    character_map[char.get('url')] = char['id']
                    
                print(f"✅ Inseridos {len(characters_ordenados)} personagens")
                print(f"   IDs: {characters_ordenados[0]['id']} até {characters_ordenados[-1]['id']}")
            else:
                print("❌ Nenhum personagem encontrado!")
            
            # ============= SEED CHARACTER_EPISODES (RELACIONAMENTOS) =============
            print("\n--- Processando Relacionamentos Personagem-Episódio ---")
            relacionamentos = 0
            
            if characters and episodes:
                for char in characters_ordenados:
                    character_id = character_map.get(char.get('url'))
                    if character_id and 'episode' in char and char['episode']:
                        for episode_url in char['episode']:
                            # Extrair o ID do episódio da URL
                            # URL exemplo: https://rickandmortyapi.com/api/episode/1
                            episode_id = None
                            if episode_url:
                                # Tenta extrair o ID da URL
                                try:
                                    episode_id = int(episode_url.split('/')[-1])
                                except:
                                    # Se não conseguir, tenta pelo mapa
                                    episode_id = episode_map.get(episode_url)
                            
                            if episode_id:
                                try:
                                    cursor.execute("""
                                        INSERT INTO character_episodes (character_id, episode_id)
                                        VALUES (%s, %s)
                                        ON CONFLICT (character_id, episode_id) DO NOTHING
                                    """, (character_id, episode_id))
                                    relacionamentos += 1
                                except Exception as e:
                                    print(f"⚠️ Erro ao inserir relacionamento: {e}")
                
                print(f"✅ Inseridos {relacionamentos} relacionamentos")
            else:
                print("❌ Não foi possível processar relacionamentos")
            
            # ============= COMMIT FINAL =============
            self.db.commit()
            print("\n" + "="*50)
            print("✅ BANCO DE DADOS POPULADO COM SUCESSO!")
            print("="*50)
            
            # Resumo final
            print(f"\n📊 RESUMO:")
            print(f"   • Localizações: {len(locations) if locations else 0}")
            print(f"   • Episódios: {len(episodes) if episodes else 0}")
            print(f"   • Personagens: {len(characters) if characters else 0}")
            print(f"   • Relacionamentos: {relacionamentos}")
            
            # Mostrar primeiros IDs para verificar
            print(f"\n🔍 PRIMEIROS REGISTROS:")
            cursor.execute("SELECT id, name FROM characters ORDER BY id LIMIT 5")
            for row in cursor.fetchall():
                print(f"   ID {row[0]}: {row[1]}")
            
        except Exception as e:
            print(f"\n❌ Erro durante o seeding: {e}")
            self.db.rollback()
        finally:
            self.db.close()