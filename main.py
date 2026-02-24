import sys
import os

# Adiciona o caminho da pasta app ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.json_handler import JSONHandler
from app.database.seed import DataSeeder

def menu_principal():
    print("\n" + "="*50)
    print("🏠 SISTEMA RICK AND MORTY")
    print("="*50)
    print("1. Ver estatísticas dos personagens")
    print("2. Buscar personagem por nome")
    print("3. Popular banco de dados")
    print("4. Sair")
    print("="*50)
    
    return input("Escolha uma opção: ")

def main():
    json_handler = JSONHandler()
    
    while True:
        opcao = menu_principal()
        
        if opcao == '1':
            print("\n📊 ESTATÍSTICAS DOS PERSONAGENS")
            stats = json_handler.estatisticas_personagens()
            if stats:
                print(f"Total de personagens: {stats['total']}")
                print(f"Vivos: {stats['vivos']}")
                print(f"Humanos: {stats['humanos']}")
        
        elif opcao == '2':
            nome = input("\nDigite o nome do personagem: ")
            resultados = json_handler.buscar_personagem(nome)
            if resultados:
                print(f"\n🔍 Encontrados {len(resultados)} personagens:")
                for p in resultados[:5]:
                    print(f"  - {p['name']} ({p['status']})")
            else:
                print("Nenhum personagem encontrado!")
        
        elif opcao == '3':
            print("\n💾 POPULANDO BANCO DE DADOS...")
            seeder = DataSeeder()
            seeder.seed_database()
        
        elif opcao == '4':
            print("\n👋 Até mais!")
            break
        
        else:
            print("\n❌ Opção inválida!")

if __name__ == "__main__":
    main()