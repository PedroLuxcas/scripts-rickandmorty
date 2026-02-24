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
            
            # Clear existing tables (correct order due to foreign keys)
            cursor.execute("TRUNCATE TABLE character_episodes RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE characters RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE episodes RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE locations RESTART IDENTITY CASCADE")
            
            # ============= SEED LOCATIONS =============
            print("\n--- Processing Locations ---")
            locations = self.json_handler.read_json('allLocations (1).json')
            location_map = {}  # URL -> ID
            
            if locations:
                # Sort by API ID
                sorted_locations = sorted(locations, key=lambda x: x['id'])
                
                for loc in sorted_locations:
                    cursor.execute("""
                        INSERT INTO locations (id, name, type, dimension)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        loc['id'],           # Uses API ID
                        loc.get('name'),
                        loc.get('type'),
                        loc.get('dimension')
                    ))
                    
                    location_map[loc.get('url')] = loc['id']
                    
                print(f"✅ Inserted {len(sorted_locations)} locations")
                print(f"   IDs: {sorted_locations[0]['id']} to {sorted_locations[-1]['id']}")
            else:
                print("❌ No locations found!")
            
            # ============= SEED EPISODES =============
            print("\n--- Processing Episodes ---")
            episodes = self.json_handler.read_json('allEpisodesUpdated (1).json')
            episode_map = {}  # URL -> ID
            
            if episodes:
                # Sort by API ID
                sorted_episodes = sorted(episodes, key=lambda x: x['id'])
                
                for ep in sorted_episodes:
                    cursor.execute("""
                        INSERT INTO episodes (id, name, air_date, episode)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        ep['id'],             # Uses API ID
                        ep.get('name'),
                        ep.get('air_date'),
                        ep.get('episode')
                    ))
                    
                    episode_map[ep.get('url')] = ep['id']
                    
                print(f"✅ Inserted {len(sorted_episodes)} episodes")
                print(f"   IDs: {sorted_episodes[0]['id']} to {sorted_episodes[-1]['id']}")
            else:
                print("❌ No episodes found!")
            
            # ============= SEED CHARACTERS =============
            print("\n--- Processing Characters ---")
            characters = self.json_handler.read_json('allCharsUpdated (3) (2).json')
            character_map = {}  # URL -> ID
            
            if characters:
                # Sort by API ID
                sorted_characters = sorted(characters, key=lambda x: x['id'])
                
                for char in sorted_characters:
                    # Get origin and location data
                    origin_data = char.get('origin', {})
                    location_data = char.get('location', {})
                    
                    origin_url = origin_data.get('url') if origin_data else None
                    location_url = location_data.get('url') if location_data else None
                    
                    # Get location IDs from map
                    origin_id = location_map.get(origin_url) if origin_url and origin_url != '' else None
                    location_id = location_map.get(location_url) if location_url and location_url != '' else None
                    
                    cursor.execute("""
                        INSERT INTO characters (
                            id, name, status, species, type, gender, image,
                            origin_id, location_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        char['id'],           # Uses API ID
                        char.get('name'),
                        char.get('status'),
                        char.get('species'),
                        char.get('type', ''),
                        char.get('gender'),
                        char.get('image'),
                        origin_id,
                        location_id
                    ))
                    
                    character_map[char.get('url')] = char['id']
                    
                print(f"✅ Inserted {len(sorted_characters)} characters")
                print(f"   IDs: {sorted_characters[0]['id']} to {sorted_characters[-1]['id']}")
            else:
                print("❌ No characters found!")
            
            # ============= SEED CHARACTER_EPISODES =============
            print("\n--- Processing Character-Episode Relationships ---")
            relationships = 0
            
            if characters and episodes:
                for char in sorted_characters:
                    character_id = character_map.get(char.get('url'))
                    if character_id and 'episode' in char and char['episode']:
                        for episode_url in char['episode']:
                            # Extract ID from episode URL
                            # URL example: https://rickandmortyapi.com/api/episode/1
                            episode_id = None
                            if episode_url:
                                try:
                                    # Try to extract ID from URL
                                    episode_id = int(episode_url.split('/')[-1])
                                except:
                                    # If fails, try using map
                                    episode_id = episode_map.get(episode_url)
                            
                            if episode_id:
                                try:
                                    cursor.execute("""
                                        INSERT INTO character_episodes (character_id, episode_id)
                                        VALUES (%s, %s)
                                        ON CONFLICT (character_id, episode_id) DO NOTHING
                                    """, (character_id, episode_id))
                                    relationships += 1
                                except Exception as e:
                                    print(f"⚠️ Error inserting relationship: {e}")
                
                print(f"✅ Inserted {relationships} relationships")
            else:
                print("❌ Could not process relationships")
            
            # ============= FINAL COMMIT =============
            self.db.commit()
            print("\n" + "="*50)
            print("✅ DATABASE SUCCESSFULLY POPULATED!")
            print("="*50)
            
            # Final summary
            print(f"\n📊 SUMMARY:")
            print(f"   • Locations: {len(locations) if locations else 0}")
            print(f"   • Episodes: {len(episodes) if episodes else 0}")
            print(f"   • Characters: {len(characters) if characters else 0}")
            print(f"   • Relationships: {relationships}")
            
            # Show first records to verify
            print(f"\n🔍 FIRST CHARACTERS:")
            cursor.execute("SELECT id, name FROM characters ORDER BY id LIMIT 5")
            for row in cursor.fetchall():
                print(f"   ID {row[0]}: {row[1]}")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            self.db.rollback()
        finally:
            self.db.close()