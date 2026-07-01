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

def encontrar_faixa_azul(imagem, cor_alvo, tolerancia=15): 
    """
    Encontra posições analisando um bloco horizontal de 50 pixels no meio da imagem.
    Considera uma margem de erro de faixa entre 3 e 7 pixels de altura.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Define os limites do bloco horizontal de 50 pixels bem no centro da imagem
    x_centro = largura // 2
    x_inicio = x_centro - 25
    x_fim = x_centro + 25
    
    y = 0
    while y < altura:
        # Verifica se TODOS os 50 pixels horizontais na linha atual são da cor alvo
        linha_correta = True
        for x in range(x_inicio, x_fim):
            pixel = pixels[x, y]
            r, g, b = pixel[:3]
            
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                linha_correta = False
                break  # Sai do loop horizontal se um único pixel falhar
        
        # Se a linha atual bate com o padrão, vamos medir a altura dessa faixa
        if linha_correta:
            altura_faixa_real = 0
            
            # Varre para baixo para ver quantos pixels de altura a faixa tem
            while (y + altura_faixa_real < altura):
                linha_continua = True
                
                # Checa os mesmos 50 pixels nas linhas de baixo
                for x in range(x_inicio, x_fim):
                    p_atual = pixels[x, y + altura_faixa_real]
                    r_c, g_c, b_c = p_atual[:3]
                    
                    if (abs(r_c - cor_alvo[0]) > tolerancia or 
                        abs(g_c - cor_alvo[1]) > tolerancia or 
                        abs(b_c - cor_alvo[2]) > tolerancia):
                        linha_continua = False
                        break
                
                if linha_continua:
                    altura_faixa_real += 1
                else:
                    break
            
            # Valida a margem de erro (5 pixels +/- 2 -> entre 3 e 7 pixels)
            if 3 <= altura_faixa_real <= 7:
                posicao_corte = y + altura_faixa_real
                
                if posicao_corte < altura:
                    posicoes_corte.append((y, posicao_corte))
                    print(f"Faixa horizontal de 50px validada! Altura: {altura_faixa_real}px em y={y}. Cortando em y={posicao_corte}")
                
                # Pula a faixa inteira encontrada para continuar a busca abaixo dela
                y += altura_faixa_real
                continue
                
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando DEPOIS das faixas
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    intervalos_faixas = encontrar_faixa_azul(imagem, cor_alvo)
    
    if not intervalos_faixas:
        print("Nenhuma faixa encontrada na imagem com esses critérios!")
        return
    
    print(f"Encontradas {len(intervalos_faixas)} faixas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (inicio_faixa, posicao_corte) in enumerate(intervalos_faixas):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta o resto da imagem após a última faixa
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(intervalos_faixas)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  
    pasta_saida = "questoes_colunas" 

    #caminho_imagem = "./inteiras/pagina_enem_15.png"  
    #pasta_saida = "pagina_15" 
    
    # Padrão RGB solicitado: (35, 31, 32)
    cor_do_padrao = (35, 31, 32)
    
    print(f"Cor alvo definida: RGB{cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!") 
