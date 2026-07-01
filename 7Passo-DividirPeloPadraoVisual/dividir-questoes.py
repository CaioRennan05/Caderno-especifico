"""
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a imagem "colunas_concatenadas_verticalmente.png" do passo 6 para essa pasta do passo 7, e as imagens de páginas inteiras da pasta "inteiras" do passo 5 para essa pasta do passo 7

OBS2: este código foi originalmente preparado para percorrer cada pixel de cima para baixo, analizando o penúltimo pixel da direita, procurando por um padrão visual vertical de 10 pixels RGB 0-255 (64, 193, 243), seguido de 7 pixels RGB 0-255 (179, 230, 250), 4 px  RGB 0-255 (64, 193, 243) e 8 px RGB 0-255 (179, 230, 250). Quando encontrava esse padrão, cortava-se 13 pixels acima de começar o padrão.

OBS3: você vai precisar identificar o padrão visual que indica o começo da questão na sua prova usando o GIMP. Pode usar IA para mudar minimamente o código a fim de cortar sua imagem seguindo o padrão visual vertical da sua prova.

OBS4: você vai rodar esse código para cortar a imagem de colunas concatenadas, depois você vai rodar para cada página inteira

OBS5: atualize as linhas 130 e 134 para recortar a imagem de colunas concatenadas, depois atualize para recortar cada página inteira. Atualize o nome da pasta de saída também
"""

from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_azul(imagem, cor_alvo, tolerancia=5, altura_faixa=10): # Ajustada tolerância para preto e mantida altura 10
    """
    Encontra posições onde há uma faixa horizontal da cor especificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - altura_faixa:
        # Verifica se há uma faixa de 'altura_faixa' pixels da cor alvo
        faixa_encontrada = True
        
        for dy in range(altura_faixa):
            # Pega a cor do pixel atual (verifica no último pixel da linha, ou seja, no canto da imagem)
            pixel = pixels[largura-2, y + dy]  # CORRIGIDO: verificar o pixel próximo ao canto para evitar bordas
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Corta ANTES da faixa (no pixel anterior definido pela folga desejada)
            pixels_acima = 13  # Altere aqui quantos pixels ACIMA do padrão você deseja cortar
            posicao_corte = y - pixels_acima  
            if posicao_corte < 0:  # Evitar posições negativas
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão preto encontrado começando em y={y}, cortando em y={posicao_corte}")
            # Pula a faixa inteira para evitar detecções múltiplas
            y += altura_faixa
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das faixas azuis
    posicoes_corte = encontrar_faixa_azul(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa padrão encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES da faixa (do início anterior até o início da faixa)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa (pula os 10 pixels do padrão)
        posicao_anterior = posicao_corte + 10  
    
    # Corta a seção final (após a última faixa)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes_colunas" # Substitua pelo nome da pasta de saída desejada (questoes_colunas, pagina_15, pagina_28)

    #caminho_imagem = "./inteiras/pagina_enem_15.png"  # Substitua pelo caminho da sua imagem
    #pasta_saida = "pagina_15" # Substitua pelo nome da pasta de saída desejada (questoes_colunas, pagina_15, pagina_28)
    
    # Define diretamente a cor padrão como Preto (0, 0, 0)
    cor_do_padrao = (0, 0, 0) 
    print(f"Cor definida: RGB{cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")