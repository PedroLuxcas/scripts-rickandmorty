import psycopg2


try:
    conn = psycopg2.connect(
        host='localhost',
        database='rickandmorty',
        user='postgres',
        password='123456',
        port='5432',
        client_encoding='utf8'
    )
    cursor = conn.cursor()
    print("Conectado ao banco com sucesso!")
    
  
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'characters'
        ORDER BY ordinal_position
    """)
    
    print("\n ESTRUTURA DA TABELA CHARACTERS:")
    print("-" * 40)
    colunas = cursor.fetchall()
    if colunas:
        for col in colunas:
            print(f"   • {col[0]} : {col[1]}")
    else:
        print("Tabela 'characters' não existe!")
    
    
    colunas_necessarias = ['name', 'status', 'species', 'type', 'gender', 'image']
    print("\n VERIFICANDO COLUNAS NECESSÁRIAS:")
    print("-" * 40)
    
    for coluna in colunas_necessarias:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'characters' AND column_name = %s
            )
        """, (coluna,))
        existe = cursor.fetchone()[0]
        if existe:
            print(f"    {coluna}: OK")
        else:
            print(f"    {coluna}: FALTANDO!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f" Erro: {e}")