"""
Propósito: Dividir as questões por padrão em múltiplas imagens (com margem de erro e cor personalizada).
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026
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

# ALTERADO: Tolerância levemente ajustada para 8 para cobrir variações dessa cor específica
def encontrar_faixa_azul(imagem, cor_alvo, tolerancia=8, altura_faixa=4):
    """
    Encontra posições onde há uma faixa horizontal da cor especificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    y = 0
    while y < altura - altura_faixa:
        faixa_encontrada = True
        
        for dy in range(altura_faixa):
            pixel = pixels[largura-2, y + dy]
            
            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]
            
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            pixels_acima = 13  # Quantos pixels acima do início do padrão você deseja cortar
            posicao_corte = y - pixels_acima  
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão visual encontrado em y={y}, cortando em y={posicao_corte}")
            
            # Avança o 'y' dinamicamente enquanto o pixel continuar dentro da cor do padrão
            while y < altura:
                pixel_atual = pixels[largura-2, y]
                r, g, b = pixel_atual[:3]
                if (abs(r - cor_alvo[0]) > tolerancia or 
                    abs(g - cor_alvo[1]) > tolerancia or 
                    abs(b - cor_alvo[2]) > tolerancia):
                    break 
                y += 1
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo {caminho_imagem} não foi encontrado.")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"\nProcessando: {caminho_imagem} ({largura}x{altura} pixels)")
    
    posicoes_corte = encontrar_faixa_azul(imagem, cor_alvo)
    
    if not posicoes_corte:
        print(f"Nenhuma faixa padrão encontrada em {caminho_imagem}!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte + 15  
    
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    imagens_para_processar = [
        "colunas_concatenadas_verticalmente1.png",
        "colunas_concatenadas_verticalmente2.png"
    ]
    
    pasta_saida_base = "questoes_colunas"
    
    # ALTERADO: Reativada a conversão do GIMP passando seus novos valores (13.7, 12.2, 12.5)
    cor_do_padrao = converter_cor_gimp_para_rgb(13.7, 12.2, 12.5) 
    print(f"Cor convertida do GIMP para RGB (0-255): {cor_do_padrao}")
    
    for indice, caminho_imagem in enumerate(imagens_para_processar, start=1):
        pasta_saida_atual = f"{pasta_saida_base}_{indice}"
        dividir_imagem_por_faixas(caminho_imagem, pasta_saida_atual, cor_do_padrao)
    
    print("\nTodos os arquivos foram processados com sucesso!")