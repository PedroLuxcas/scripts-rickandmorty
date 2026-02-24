import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            'host': 'localhost',
            'database': 'rickandmorty', 
            'user': 'postgres',
            'password': '123456', 
            'port': '5432',
            'client_encoding': 'utf8'
        }
        self.conn = None
        self.cursor = None
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
            print("✅ Conectado ao banco de dados com sucesso!")
            return self.cursor
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return None
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("🔒 Conexão fechada.")
    
    def commit(self):
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        if self.conn:
            self.conn.rollback()
            print("↩️ Rollback realizado com sucesso!")