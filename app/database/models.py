class TableCreator:
    @staticmethod
    def create_tables(cursor):
        # ============= LOCATIONS TABLE =============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255),
                type VARCHAR(100),
                dimension VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ============= EPISODES TABLE =============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255),
                air_date VARCHAR(100),
                episode VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ============= CHARACTERS TABLE =============
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255),
                status VARCHAR(50),
                species VARCHAR(100),
                type VARCHAR(100),
                gender VARCHAR(50),
                image TEXT,
                origin_id INTEGER,
                location_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (origin_id) REFERENCES locations(id) ON DELETE SET NULL,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
            )
        """)
        
        # ============= CHARACTER_EPISODES TABLE (composite key) =============
        cursor.execute("""
            CREATE TABLE character_episode (
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                character_id INT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
                episode_id INT NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
                PRIMARY KEY (character_id, episode_id)
            );
        """)
        
        # ============= INDEXES FOR BETTER PERFORMANCE =============
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_characters_origin_id 
            ON characters(origin_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_characters_location_id 
            ON characters(location_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_character_episodes_character_id 
            ON character_episodes(character_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_character_episodes_episode_id 
            ON character_episodes(episode_id)
        """)
        
        print("✅ Tables created/verified successfully!")