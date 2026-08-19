from PIL import Image
import os
import shutil

def cores_proximas(c1, c2, tolerancia=25):
    """Verifica se duas cores RGB estão dentro da margem de erro (tolerância)."""
    return all(abs(c1[i] - c2[i]) <= tolerancia for i in range(3))

def encontrar_faixa_inferior(imagem, cor_faixa=(35, 31, 32), cor_transicao=(155, 153, 154), tolerancia=25):
    """
    Percorre a imagem de baixo para cima buscando a faixa horizontal de 4px (35, 31, 32)
    e valida a transição do fundo branco para a cor do padrão antes de definir o corte.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Percorre de baixo para cima
    for y in range(altura - 5, 20, -1):
        # 1. Verifica se há 4 pixels consecutivos verticais com a cor da faixa (35, 31, 32)
        faixa_vertical = True
        for dy in range(4):
            pixel = pixels[largura // 2, y + dy][:3]
            if not cores_proximas(pixel, cor_faixa, tolerancia):
                faixa_vertical = False
                break
                
        if not faixa_vertical:
            continue
            
        # 2. Confirma se a faixa é contínua horizontalmente na maior parte da página
        pontos_faixa = 0
        amostras = range(10, largura - 10, 20)
        for x in amostras:
            if cores_proximas(pixels[x, y][:3], cor_faixa, tolerancia):
                pontos_faixa += 1
                
        # Exige que pelo menos 80% das amostras na largura sejam da cor da faixa
        if len(amostras) > 0 and (pontos_faixa / len(amostras)) < 0.80:
            continue

        # 3. Valida se acima dessa faixa existe a sequência de brancos que encontra o padrão (155, 153, 154)
        encontrou_padrao = False
        for y_verifica in range(y - 1, max(0, y - 150), -1):
            pixel_chk = pixels[largura // 2, y_verifica][:3]
            # Se sair do fundo branco
            if not cores_proximas(pixel_chk, (255, 255, 255), tolerancia=15):
                # Confirma se o pixel encontrado bate com a cor alvo do padrão
                if cores_proximas(pixel_chk, cor_transicao, tolerancia):
                    encontrou_padrao = True
                break

        if encontrou_padrao:
            print(f"Faixa e padrão válidos encontrados! Cortando na posição y={y}")
            return y

    return None

def processar_imagens(pasta_origem, pasta_destino, cor_faixa, cor_transicao):
    """
    Processa todas as imagens da pasta origem, recortando as que têm a faixa e padrão detectados.
    """
    os.makedirs(pasta_destino, exist_ok=True)
    
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                posicao_corte = encontrar_faixa_inferior(imagem, cor_faixa, cor_transicao)
                
                if posicao_corte is not None and posicao_corte > 0:
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem faixa/padrão detectado)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

if __name__ == "__main__":
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    cor_faixa = (35, 31, 32)
    cor_transicao = (155, 153, 154)
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor da faixa: RGB{cor_faixa}")
    print(f"Cor de transição: RGB{cor_transicao}")
    
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    processar_imagens(pasta_origem, pasta_destino, cor_faixa, cor_transicao)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")