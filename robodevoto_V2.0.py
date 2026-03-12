from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# --- CONFIGURAÇÕES DO BOT ---
URL = "http://localhost:8501/?tela=urna"
QTD_VOTACOES = 250  # Quantas vezes o bot vai realizar o processo completo
VAGAS_TOTAIS = 7  # Limite máximo (3 presbíteros + 4 diáconos)

# Inicializa o navegador
options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Descomente esta linha se quiser rodar invisível
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

print("Iniciando o robô de votação...")

try:
    # Acessa a página apenas na primeira vez (o próprio Streamlit vai resetar a urna depois)
    driver.get(URL)
    time.sleep(3) # Aguarda o carregamento inicial completo

    for i in range(QTD_VOTACOES):
        print(f"\n--- Iniciando Votação {i+1} de {QTD_VOTACOES} ---")
        
        # Sorteia aleatoriamente em quantos candidatos o bot vai votar nesta rodada
        num_votos_rodada = random.randint(3, VAGAS_TOTAIS)
        
        votos_realizados = 0
        tentativas = 0
        
        # O limite de tentativas evita que o bot fique preso caso esbarre no limite de vagas de um cargo
        while votos_realizados < num_votos_rodada and tentativas < 15:
            time.sleep(1.5) 
            tentativas += 1
            
            # Busca todos os botões que ainda têm o texto VOTAR
            xpath_botoes = "//button[contains(., 'VOTAR')]"
            botoes_votar = driver.find_elements(By.XPATH, xpath_botoes)
            
            if botoes_votar:
                botao_escolhido = random.choice(botoes_votar)
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_escolhido)
                    time.sleep(0.5)
                    botao_escolhido.click()
                    votos_realizados += 1
                    print(f"[{votos_realizados}/{num_votos_rodada}] Tentativa de voto registrada na urna...")
                except Exception as e:
                    print(f"Falha ao clicar no botão: {e}")
            else:
                print("Nenhum botão 'VOTAR' restante.")
                break 

        # --- ETAPA DE REVISÃO ---
        time.sleep(1.5)
        print("Avançando para revisar votos...")
        try:
            botao_revisar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'REVISAR MEUS VOTOS')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_revisar)
            time.sleep(0.5)
            botao_revisar.click()
        except Exception:
            print("⚠️ Erro ao encontrar o botão de revisar. Recarregando e pulando rodada...")
            driver.get(URL)
            continue

        # --- ETAPA DE CONFIRMAÇÃO ---
        time.sleep(1.5)
        print("Confirmando voto com cadeado...")
        try:
            botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'CONFIRMAR VOTO')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_confirmar)
            time.sleep(0.5)
            botao_confirmar.click()
            print("Voto finalizado com sucesso! 🎉")
        except Exception:
            print("⚠️ Erro ao encontrar o botão de confirmar. Recarregando e pulando rodada...")
            driver.get(URL)
            continue

        # Aguarda a tela de agradecimento (balões) passar e o Streamlit recarregar a urna sozinho
        print("Aguardando o sistema reiniciar a urna...")
        time.sleep(5) 

except Exception as ex:
    print(f"\nOcorreu um erro inesperado: {ex}")

finally:
    driver.quit()
    print("\nAutomação finalizada.")