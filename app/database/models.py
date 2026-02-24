class TableCreator:
    @staticmethod
    def create_tables(cursor):
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY,  -- Mudou de SERIAL para INTEGER
                name VARCHAR(255),
                type VARCHAR(100),
                dimension VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY,  -- Mudou de SERIAL para INTEGER
                name VARCHAR(255),
                air_date VARCHAR(100),
                episode VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,  -- Mudou de SERIAL para INTEGER
                name VARCHAR(255),
                status VARCHAR(50),
                species VARCHAR(100),
                type VARCHAR(100),
                gender VARCHAR(50),
                image TEXT,
                origin_id INTEGER,
                location_id INTEGER,
                origin JSONB,
                location JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (origin_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
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