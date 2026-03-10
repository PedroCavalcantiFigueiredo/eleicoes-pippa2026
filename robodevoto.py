from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# --- CONFIGURAÇÕES DO BOT ---
URL = "http://localhost:8501/?tela=urna"
QTD_VOTACOES = 194  # Quantas vezes o bot vai realizar o processo completo
VAGAS_TOTAIS = 7  # Limite máximo de cliques (3 presbíteros + 4 diáconos, conforme seu padrão)

# Inicializa o navegador
options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Descomente esta linha se quiser rodar invisível
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

print("Iniciando o robô de votação...")

try:
    for i in range(QTD_VOTACOES):
        print(f"\n--- Iniciando Votação {i+1} de {QTD_VOTACOES} ---")
        driver.get(URL)
        
        # Sorteia aleatoriamente em quantos candidatos o bot vai votar nesta rodada
        num_votos_rodada = random.randint(3, VAGAS_TOTAIS)
        
        for v in range(num_votos_rodada):
            time.sleep(1.5) 
            
            # XPATH CORRIGIDO: O ponto (.) busca a palavra 'VOTAR' em qualquer lugar dentro do botão
            xpath_botoes = "//button[contains(., 'VOTAR')]"
            botoes_votar = driver.find_elements(By.XPATH, xpath_botoes)
            
            if botoes_votar:
                botao_escolhido = random.choice(botoes_votar)
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_escolhido)
                    time.sleep(0.5)
                    botao_escolhido.click()
                    print(f"[{v+1}/{num_votos_rodada}] Voto registrado na urna...")
                except Exception as e:
                    print(f"Falha ao clicar no botão: {e}")
            else:
                print("Nenhum botão 'VOTAR' restante ou limite atingido.")
                break 

        # --- ETAPA DE CONFIRMAÇÃO ---
        time.sleep(1.5)
        print("Avançando para revisar votos...")
        # Usa o mesmo truque do ponto (.) para evitar problemas de texto oculto no Streamlit
        botao_revisar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'REVISAR MEUS VOTOS')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_revisar)
        time.sleep(0.5)
        botao_revisar.click()

        # --- FINALIZAR VOTO ---
        time.sleep(1.5)
        print("Confirmando voto com cadeado...")
        botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'CONFIRMAR VOTO')]")))
        botao_confirmar.click()
        print("Voto finalizado com sucesso! 🎉")

        time.sleep(4)

except Exception as ex:
    print(f"\nOcorreu um erro inesperado: {ex}")

finally:
    driver.quit()
    print("\nAutomação finalizada.")