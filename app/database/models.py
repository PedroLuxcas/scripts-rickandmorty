class TableCreator:
    @staticmethod
    def create_tables(cursor):
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                type VARCHAR(100),
                dimension VARCHAR(100),
                url TEXT,
                created TIMESTAMP,
                residents JSONB,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                status VARCHAR(50),
                species VARCHAR(100),
                type VARCHAR(100),
                gender VARCHAR(50),
                image TEXT,
                url TEXT,
                created TIMESTAMP,
                origin_id INTEGER,
                location_id INTEGER,
                origin JSONB,
                location JSONB,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (origin_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
            )
        """)
        
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                air_date VARCHAR(100),
                episode VARCHAR(50),
                url TEXT,
                created TIMESTAMP,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_episodes (
                id SERIAL PRIMARY KEY,
                character_id INTEGER NOT NULL,
                episode_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE,
                UNIQUE(character_id, episode_id)
            )
        """)
        
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_origin_id ON characters(origin_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_location_id ON characters(location_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_episodes_character_id ON character_episodes(character_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_episodes_episode_id ON character_episodes(episode_id)")
        
        print("✅ Tabelas criadas/verificadas com sucesso!")