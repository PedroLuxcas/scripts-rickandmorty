from app.database.seed import DataSeeder
from app.database.connection import DatabaseConnection
from app.utils.json_handler import JSONHandler

def populate_relationships_only():
    """Popula apenas a tabela character_episodes"""
    print("\n" + "="*50)
    print("🔄 POPULANDO APENAS RELACIONAMENTOS")
    print("="*50)
    
    # Conectar ao banco
    db = DatabaseConnection()
    cursor = db.connect()
    
    if not cursor:
        print("❌ Erro ao conectar ao banco")
        return
    
    try:
        # Carregar personagens do JSON
        handler = JSONHandler()
        characters = handler.read_json('allCharsUpdated (3) (2).json')
        
        if not characters:
            print("❌ Erro ao carregar personagens")
            return
        
        print(f"📂 Carregados {len(characters)} personagens")
        
        # Limpar tabela de relacionamentos (opcional)
        cursor.execute("TRUNCATE TABLE character_episodes CASCADE;")
        print("🧹 Tabela character_episodes limpa")
        
        # Processar relacionamentos
        total = 0
        personagens_com_episodios = 0
        
        for char in characters:
            character_id = char['id']
            episodios = char.get('episode', [])
            
            if episodios:
                personagens_com_episodios += 1
                
                for episode_url in episodios:
                    try:
                        # Extrair ID da URL (ex: .../episode/1 → 1)
                        episode_id = int(episode_url.split('/')[-1])
                        
                        cursor.execute("""
                            INSERT INTO character_episodes (character_id, episode_id)
                            VALUES (%s, %s)
                            ON CONFLICT (character_id, episode_id) DO NOTHING
                        """, (character_id, episode_id))
                        
                        total += 1
                        
                        # Mostrar progresso a cada 500
                        if total % 500 == 0:
                            print(f"   ... {total} relacionamentos processados")
                            
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ Erro na URL {episode_url}: {e}")
        
        # Commit
        db.commit()
        
        print(f"\n✅ Inseridos {total} relacionamentos")
        print(f"👤 Personagens com episódios: {personagens_com_episodios}")
        
        if personagens_com_episodios > 0:
            print(f"📊 Média: {total/personagens_com_episodios:.1f} episódios por personagem")
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM character_episodes")
        count = cursor.fetchone()[0]
        print(f"📊 Total na tabela character_episodes: {count}")
        
        # Mostrar alguns exemplos
        cursor.execute("""
            SELECT c.name, COUNT(ce.episode_id) as total_episodios
            FROM characters c
            LEFT JOIN character_episodes ce ON c.id = ce.character_id
            GROUP BY c.id, c.name
            ORDER BY total_episodios DESC
            LIMIT 5
        """)
        
        print("\n🔍 Top 5 personagens com mais episódios:")
        for row in cursor.fetchall():
            print(f"   • {row[0]}: {row[1]} episódios")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

def main_menu():
    print("\n" + "="*50)
    print("🏠 RICK AND MORTY DATABASE SYSTEM")
    print("="*50)
    print("1. View character statistics")
    print("2. Search character by name")
    print("3. Populate database (complete)")
    print("4. Populate relationships only")  # NOVA OPÇÃO
    print("5. Exit")
    print("="*50)
    
    return input("Choose an option: ")

def main():
    json_handler = JSONHandler()
    
    while True:
        option = main_menu()
        
        if option == '1':
            print("\n📊 Character Statistics")
            stats = json_handler.estatisticas_personagens()
            if stats:
                print(f"Total characters: {stats['total']}")
                print(f"Alive: {stats['vivos']}")
                print(f"Human: {stats['humanos']}")
        
        elif option == '2':
            name = input("\nEnter character name: ")
            results = json_handler.buscar_personagem(name)
            if results:
                print(f"\n🔍 Found {len(results)} characters:")
                for char in results[:5]:
                    print(f"   • {char['name']} ({char['status']})")
            else:
                print("No characters found")
        
        elif option == '3':
            print("\n💾 POPULATING COMPLETE DATABASE...")
            seeder = DataSeeder()
            seeder.seed_database()
        
        elif option == '4':  # NOVA OPÇÃO
            populate_relationships_only()
        
        elif option == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option!")

if __name__ == "__main__":
    main()