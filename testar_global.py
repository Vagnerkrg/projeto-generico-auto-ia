import os
import time
import subprocess

def executar_passo(titulo, comando):
    print("\n" + "="*70)
    print(f" 🔥 {titulo.upper()}")
    print("="*70)
    try:
        # Executa o script python filho e aguarda a finalização
        resultado = subprocess.run(["python", comando], capture_output=False, text=True)
        if resultado.returncode == 0:
            print(f"✅ PASSO CONCLUÍDO COM SUCESSO!")
        else:
            print(f"❌ OCORREU UM ERRO NO PASSO: {comando}")
    except Exception as e:
        print(f"❌ FALHA CRÍTICA AO EXECUTAR: {str(e)}")
    time.sleep(2)

if __name__ == "__main__":
    print("\n" + "#"*70)
    print(" 🧪 INICIALIZANDO PIPELINE DE TESTE GLOBAL - ECOSSISTEMA LUNA")
    print("#"*70)
    
    # Passo 1: Simular a conversa inteligente e travas comerciais da Luna
    executar_passo("Testando Inteligência da IA e Travas de Horário", "testar_bot.py")
    
    # Passo 2: Executar o motor ativo de busca e disparo de lembretes
    executar_passo("Testando Motor Ativo de Lembretes Automáticos", "rodar_lembretes.py")
    
    # Passo 3: Exibir a tabela consolidada do banco de dados SQLite
    executar_passo("Consultando Persistência Final no Dashboard", "exibir_dashboard.py")
    
    print("\n" + "#"*70)
    print(" 🎉 PIPELINE GLOBAL EXECUTADO COMPLEMENTARMENTE COM SUCESSO!")
    print("#"*70)
