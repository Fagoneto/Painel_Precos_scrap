from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Configurações do Chrome
options = Options()
options.add_argument("--headless")  # roda sem abrir navegador
driver = webdriver.Chrome(options=options)

# Termo de busca
produto = "tilápia"
url = f"https://www.carrefour.com.br/busca?term={produto}"

# Acessa o site
driver.get(url)
time.sleep(5)  # aguarda JS carregar

# Coleta os produtos da página
produtos = driver.find_elements(By.CLASS_NAME, "product-card__description")

dados = []

for produto in produtos:
    try:
        nome = produto.find_element(By.CLASS_NAME, "product-card__name").text
        preco = produto.find_element(By.CLASS_NAME, "sales-price").text
        dados.append({"nome": nome, "preco": preco})
    except Exception as e:
        continue

# Salva como DataFrame
df = pd.DataFrame(dados)
df.to_csv("precos_carrefour.csv", index=False)

driver.quit()
