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

def cor_proxima(pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor do pixel está dentro da tolerância da cor alvo.
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_faixa_azul(imagem, tolerancia=15):
    """
    Encontra posições onde há o padrão visual vertical:
    - 1 pixel branco (255, 255, 255)
    - 30 pixels da cor cinza (167, 165, 163) [com margem de erro de 5 pixels para mais ou para menos na altura, i.e., 25 a 35 pixels]
    - 1 pixel branco (255, 255, 255)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    branco = (255, 255, 255)
    cinza = (167, 165, 163)
    
    # Altura base do cinza é 30, com margem de erro de 5 (variação de 25 a 35)
    altura_min_cinza = 25
    altura_max_cinza = 35
    
    # Percorre a imagem de cima para baixo
    y = 0
    # Tamanho total mínimo do padrão: 1 (branco) + 25 (cinza mín) + 1 (branco) = 27 pixels
    while y < altura - 27:
        # Verifica o primeiro pixel (branco)
        pixel_inicial = pixels[largura - 2, y]
        if not cor_proxima(pixel_inicial, branco, tolerancia):
            y += 1
            continue
            
        # Tenta encontrar a altura exata do bloco cinza dentro da margem de erro (25 a 35)
        altura_cinza_encontrada = -1
        for h_cinza in range(altura_min_cinza, altura_max_cinza + 1):
            bloco_valido = True
            for dy in range(1, 1 + h_cinza):
                if y + dy >= altura:
                    bloco_valido = False
                    break
                pixel_atual = pixels[largura - 2, y + dy]
                if not cor_proxima(pixel_atual, cinza, tolerancia):
                    bloco_valido = False
                    break
            
            if bloco_valido:
                # Verifica se o pixel logo após o bloco cinza é branco
                pos_pixel_final = y + 1 + h_cinza
                if pos_pixel_final < altura:
                    pixel_final = pixels[largura - 2, pos_pixel_final]
                    if cor_proxima(pixel_final, branco, tolerancia):
                        altura_cinza_encontrada = h_cinza
                        break
        
        if altura_cinza_encontrada != -1:
            # Padrão encontrado! 
            # Corta a imagem um pixel acima de o padrão começar, para que o primeiro pixel branco e a faixa fiquem no início da nova imagem.
            posicao_corte = y
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            tamanho_total_padrao = 1 + altura_cinza_encontrada + 1
            print(f"Padrão encontrado começando em y={y}, cortando em y={posicao_corte}")
            
            # Pula o padrão inteiro para evitar detecções múltiplas
            y += tamanho_total_padrao
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando exatamente no início do padrão
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das faixas
    posicoes_corte = encontrar_faixa_azul(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Se a posição de corte for 0 (início do arquivo), não gera uma seção vazia
        if posicao_corte <= posicao_anterior:
            # Atualiza a posição anterior para a próxima iteração ignorar este corte se necessário
            # mas mantemos o fluxo normal caso seja o primeiro
            if posicao_corte == 0:
                continue
            else:
                continue
            
        # Corta a seção até o início do padrão atual
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final (após o último padrão encontrado)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes" # Substitua pelo nome da pasta de saída desejada

    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")