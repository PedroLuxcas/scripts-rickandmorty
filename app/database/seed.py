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
            # Create tables
            TableCreator.create_tables(cursor)
            
            # Clear existing tables (in the correct order because of foreign keys)
            cursor.execute("TRUNCATE TABLE character_episodes RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE characters RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE episodes RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE locations RESTART IDENTITY CASCADE")
            
            # ============= SEED LOCATIONS =============
            print("\n--- Processando Localizações ---")
            locations = self.json_handler.ler_json('allLocations (1).json')
            location_map = {}  # URL -> ID
            
            if locations:
                # Sort by API ID
                locations_ordenadas = sorted(locations, key=lambda x: x['id'])
                
                for loc in locations_ordenadas:
                    cursor.execute("""
                        INSERT INTO locations (id, name, type, dimension)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        loc['id'],           # Use the API ID
                        loc.get('name'),
                        loc.get('type'),
                        loc.get('dimension')
                    ))
                    
                    location_map[loc.get('url')] = loc['id']
                    
                print(f"✅ Inseridas {len(locations_ordenadas)} localizações")
                print(f"   IDs: {locations_ordenadas[0]['id']} até {locations_ordenadas[-1]['id']}")
            else:
                print("❌ Nenhuma localização encontrada!")
            
            # ============= SEED EPISODES =============
            print("\n--- Processando Episódios ---")
            episodes = self.json_handler.ler_json('allEpisodesUpdated (1).json')
            episode_map = {}  # URL -> ID
            
            if episodes:
                # Sort by API ID
                episodes_ordenados = sorted(episodes, key=lambda x: x['id'])
                
                for ep in episodes_ordenados:
                    cursor.execute("""
                        INSERT INTO episodes (id, name, air_date, episode)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        ep['id'],             # Use the API ID
                        ep.get('name'),
                        ep.get('air_date'),
                        ep.get('episode')
                    ))
                    
                    episode_map[ep.get('url')] = ep['id']
                    
                print(f"✅ Inseridos {len(episodes_ordenados)} episódios")
                print(f"   IDs: {episodes_ordenados[0]['id']} até {episodes_ordenados[-1]['id']}")
            else:
                print("❌ Nenhum episódio encontrado!")
            
            # ============= SEED CHARACTERS =============
            print("\n--- Processando Personagens ---")
            characters = self.json_handler.ler_json('allCharsUpdated (3) (2).json')
            character_map = {}  # URL -> ID
            
            if characters:
                # Sort by API ID
                characters_ordenados = sorted(characters, key=lambda x: x['id'])
                
                for char in characters_ordenados:
                    # Get source and location data
                    origin_data = char.get('origin', {})
                    location_data = char.get('location', {})
                    
                    origin_url = origin_data.get('url') if origin_data else None
                    location_url = location_data.get('url') if location_data else None
                    
                    # Search location IDs
                    origin_id = location_map.get(origin_url) if origin_url and origin_url != '' else None
                    location_id = location_map.get(location_url) if location_url and location_url != '' else None
                    
                    cursor.execute("""
                        INSERT INTO characters (
                            id, name, status, species, type, gender, image,
                            origin_id, location_id, origin, location
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        char['id'],           # Use the API ID
                        char.get('name'),
                        char.get('status'),
                        char.get('species'),
                        char.get('type', ''),
                        char.get('gender'),
                        char.get('image'),
                        origin_id,
                        location_id,
                        json.dumps(origin_data),
                        json.dumps(location_data)
                    ))
                    
                    character_map[char.get('url')] = char['id']
                    
                print(f"✅ Inseridos {len(characters_ordenados)} personagens")
                print(f"   IDs: {characters_ordenados[0]['id']} até {characters_ordenados[-1]['id']}")
            else:
                print("❌ Nenhum personagem encontrado!")
            
            # ============= SEED CHARACTER_EPISODES =============
            print("\n--- Processando Relacionamentos Personagem-Episódio ---")
            relacionamentos = 0
            
            if characters and episodes:
                for char in characters_ordenados:
                    character_id = character_map.get(char.get('url'))
                    if character_id and 'episode' in char and char['episode']:
                        for episode_url in char['episode']:
                            # Extract the episode ID from the URL
                           
                            episode_id = None
                            if episode_url:
                                try:
                                    # Try to extract the ID from the URLL
                                    episode_id = int(episode_url.split('/')[-1])
                                except:
                                    # If you can't, try using the map
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
            
            # Mostrar primeiros registros para verificar
            print(f"\n🔍 PRIMEIROS PERSONAGENS:")
            cursor.execute("SELECT id, name FROM characters ORDER BY id LIMIT 5")
            for row in cursor.fetchall():
                print(f"   ID {row[0]}: {row[1]}")
            
        except Exception as e:
            print(f"\n❌ Erro durante o seeding: {e}")
            self.db.rollback()
        finally:
            self.db.close()