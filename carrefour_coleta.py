
import os
import datetime
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIGURAÇÃO INICIAL ===
data_de_hoje = datetime.date.today()
produtos = []

options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")  # comente para visualizar
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://mercado.carrefour.com.br/")
time.sleep(3)


# Busca pelo nome do producto
search = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Pesquise por produtos ou marcas']"))
)
search.click()
search.send_keys("salmao")
search.send_keys(Keys.RETURN)


# Abertura inicial
WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='open-modal']"))
).click()

WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Retire na loja')]]"))
).click()

# Loop pelas cidades com tentativas
i = 54
while i <= 54:
    tentativas_cidade = 0
    sucesso_cidade = False

    while tentativas_cidade < 3 and not sucesso_cidade:
        try:
            print(f"[Cidade {i}] Iniciando tentativa {tentativas_cidade + 1}...")
            select = Select(WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.w-full.border-gray-300.rounded.p-3.mt-4.cursor-pointer.text-sm.drop-shadow-md"))
            ))
            select.select_by_index(i)
            time.sleep(2)

            loja_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.border.rounded-lg.shadow-md.p-4"))
            )
            total_lojas = len(loja_elements)
            print(f"[INFO] Total de lojas na cidade {i}: {total_lojas}")

            for loja_index in range(total_lojas):
                lojas_atualizadas = driver.find_elements(By.CSS_SELECTOR, "li.border.rounded-lg.shadow-md.p-4")
                time.sleep(1)
                loja = lojas_atualizadas[loja_index]
                nome_loja = loja.text.strip()
                print(f"[Cidade {i}] Loja selecionada: {nome_loja}")
                loja.click()
                time.sleep(3)

                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                divs_produtos = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='search-product-card']")
                print(f"[INFO] Total de blocos de produto encontrados: {len(divs_produtos)}")

                for idx in range(len(divs_produtos)):
                    try:
                        divs_produtos_atualizados = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='search-product-card']")
                        div = divs_produtos_atualizados[idx]
                        texto_produto = div.text.strip()
                        if texto_produto:
                            registro = f"{texto_produto}\n{nome_loja}"
                            produtos.append(registro)
                    except Exception as e:
                        print(f"[WARNING] Erro ao coletar produto {idx+1}: {e}")
                        continue

                print(f"[INFO] Total de produtos coletados até agora: {len(produtos)}")

                driver.back()
                time.sleep(3)

                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class*='container-default']"))
                ).click()
                time.sleep(1)

                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='open-modal']"))
                ).click()

                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Retire na loja')]]"))
                ).click()

                select = Select(WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select.w-full.border-gray-300.rounded.p-3.mt-4.cursor-pointer.text-sm.drop-shadow-md"))
                ))
                select.select_by_index(i)
                time.sleep(2)

            sucesso_cidade = True  # só chega aqui se não der erro em nenhuma loja

        except Exception as erro_cidade:
            tentativas_cidade += 1
            os.system("afplay /System/Library/Sounds/Basso.aiff")  # <- som de erro
            print(f"[⚠️] Erro na cidade {i}, tentativa {tentativas_cidade}: {erro_cidade}")
            time.sleep(5)
            driver.get("https://mercado.carrefour.com.br/")
            time.sleep(3)

            # Busca pelo nome do producto
            search = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Pesquise por produtos ou marcas']"))
            )
            search.click()
            search.send_keys("salmao")
            search.send_keys(Keys.RETURN)

            
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='open-modal']"))
                ).click()
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Retire na loja')]]"))
                ).click()
            except:
                pass

    if not sucesso_cidade:
        print(f"[⏭] Pulando cidade {i} após 3 falhas consecutivas.")

    i += 1  # próxima cidade

driver.quit()


print(f"[✔] Arquivo salvo com {len(produtos)} produtos coletados.")
os.system("afplay /System/Library/Sounds/Glass.aiff")



###### AQUI COMEÇA O TRATAMENTO DOS DADOS COLETADOS ######
print(f"Tratamento dos dados coletados...")

produtos_limpos = []

for p in produtos:
    # Remover linha se for "Produto indisponível" ou "lencol"
    if 'Produto indisponível' in p or 'lencol' in p.lower():
        continue

    # Remover a palavra "ADICIONAR"
    p = p.replace('ADICIONAR', '').strip()

    # Remover qualquer preço no formato por kg, litro, etc
    p = re.sub(r"R\$ ?\d+,\d{2}/(kg|g|l|ml|100ml|un|litro)", "", p, flags=re.IGNORECASE).strip()

    # Se sobrar algo válido, incluir na lista final
    if p:
        produtos_limpos.append(p)


print(f"Total de produtos limpos: {len(produtos_limpos)}")

# Lista original
dados_brutos = produtos_limpos

data_de_hoje = data_de_hoje
dados_estruturados = []

for linha in dados_brutos:
    try:
        partes = linha.split("\n\n")
        produto_bloco = partes[0]
        endereco_bloco = partes[1] if len(partes) > 1 else ""

        # Quebra o bloco do produto em linhas individuais
        linhas = produto_bloco.strip().split("\n")

        # REMOVE TRECHOS tipo "/kg", "/g", "/L" apenas de dentro das linhas
        linhas_limpa = []
        for l in linhas:
            # Remove apenas os fragmentos como "R$ XX,XX/kg", "R$ XX,XX/L", etc
            l_limpo = re.sub(r"R\$ ?\d+,\d{2}/(kg|g|l|ml|100ml|un|litro)", "", l, flags=re.IGNORECASE)
            linhas_limpa.append(l_limpo.strip())

        # Nome do produto
        produto_nome = next((x for x in linhas_limpa if "R$" not in x and "%" not in x and "promoção" not in x.lower()), "").strip()

        # Preço final (último R$ válido depois da limpeza)
        precos_encontrados = [x for x in linhas_limpa if re.search(r"R\$ ?\d+,\d{2}", x)]
        preco_final = precos_encontrados[-1] if precos_encontrados else None
        if preco_final:
            preco_final = re.search(r"R\$ ?(\d+,\d{2})", preco_final).group(1)
            preco_final = float(preco_final.replace(",", "."))

        # Desconto
        desconto_linha = next((x for x in linhas_limpa if "%" in x and "-" in x), None)
        desconto = float(desconto_linha.replace("%", "").replace(",", ".").strip()) if desconto_linha else None

        # Loja e endereço
        endereco_linhas = endereco_bloco.strip().split("\n")
        loja = endereco_linhas[0] if len(endereco_linhas) > 0 else ""
        endereco = " - ".join(endereco_linhas[1:]) if len(endereco_linhas) > 1 else ""

        # Cidade e estado
        cidade_estado_texto = endereco_linhas[-1] if len(endereco_linhas) >= 1 else ""
        if "," in cidade_estado_texto and " - " in cidade_estado_texto:
            cidade_texto = cidade_estado_texto.split(",")[-1].strip()
            cidade, estado = cidade_texto.split(" - ")
        else:
            cidade, estado = "", ""

        # Monta o dicionário final
        dados_estruturados.append({
            "produto": produto_nome,
            "preco": preco_final,
            "desconto": desconto,
            "loja": loja.strip(),
            "endereco": endereco_bloco.strip(),
            "cidade": cidade.strip(),
            "estado": estado.strip(),
            "data": data_de_hoje
        })

    except Exception as e:
        print(f"[ERRO] Linha com problema:\n{linha}\n-> {e}")

# DataFrame final
df_produtos = pd.DataFrame(dados_estruturados)

# Garante que a coluna 'data' exista antes de reorganizar
if 'data' not in df_produtos.columns:
    df_produtos['data'] = data_de_hoje

# Reorganizar com 'data' na frente
colunas = ['data'] + [col for col in df_produtos.columns if col != 'data']
df_produtos = df_produtos[colunas]

#Incluir coluna de regioes
regioes_brasil = {
    'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste',
    'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
}
df_produtos['regiao'] = df_produtos['estado'].map(regioes_brasil).fillna('Desconhecida')

# Alterar os dados da coluna cidade
df_produtos['cidade'] = df_produtos['cidade']+'/'+df_produtos['estado']

df_produtos.rename(columns={'estado': 'uf'}, inplace=True)


# Salva o dataframe atual da rodada
df_produtos.to_csv('carrefour_coleta_salmao_test.csv', index=False)

# Emite som de sucesso
os.system("afplay /System/Library/Sounds/Glass.aiff")
print("Arquivo salvo")

# Lê o histórico completo (caso exista)
try:
    df_produtos_total = pd.read_csv('carrefour_coleta_salmao_total.csv')
except FileNotFoundError:
    df_produtos_total = pd.DataFrame(columns=df_produtos.columns)

# Concatena os novos dados
df_produtos_total = pd.concat([df_produtos_total, df_produtos], ignore_index=True)

# Salva o arquivo total atualizado
df_produtos_total.to_csv('carrefour_coleta_salmao_total.csv', index=False)
