from logging import fatal
from math import trunc
from os import write

import pygame
import os
import random
import neat
import threading
import time
import csv

geracao = 0

TELA_LARGURA = 570
TELA_ALTURA = 954

pygame.mixer.init()
pygame.mixer.music.load("music/Kamado Tanjiro no Uta [8-Bit Cover] Kimetsu no Yaiba (320).mp3")
pygame.mixer.music.set_volume(0.2)
# pygame.mixer.music.play(-1, 2)

voar = pygame.mixer.Sound("efeitos_sonoros/mixkit-boxing-punch-2051.wav")
voar.set_volume(0.2)
perdeu = pygame.mixer.Sound("efeitos_sonoros/mixkit-arcade-retro-game-over-213.wav")
ganhou_ponto = pygame.mixer.Sound("efeitos_sonoros/mixkit-bonus-earned-in-video-game-2058.wav")
selecionar = pygame.mixer.Sound("efeitos_sonoros/mixkit-arcade-game-jump-coin-216.wav")

IMAGEM_BEGIN = (pygame.image.load(os.path.join('Imagens', 'inicio.jpg')))
IMAGEM_BEGIN_ESCOLHA = (pygame.image.load(os.path.join('Imagens', 'inicio_escolha.jpg')))
IMAGEM_BEGIN_AI = (pygame.image.load(os.path.join('Imagens', 'inicio_ai.jpg')))
IMAGEM_BEGIN_PLAYER = (pygame.image.load(os.path.join('Imagens', 'inicio_player.jpg')))
IMAGEM_PONTUACAO = (pygame.image.load(os.path.join('Imagens', 'tela_quando_perde_pontos.jpg')))
IMAGEM_END = (pygame.image.load(os.path.join('Imagens', 'tela_quando_perde.jpg')))
IMAGEM_END_NO = (pygame.image.load(os.path.join('Imagens', 'tela_quando_perde_no.jpg')))
IMAGEM_END_YES = (pygame.image.load(os.path.join('Imagens', 'tela_quando_perde_yes.jpg')))
IMAGEM_PAUSADO = (pygame.image.load(os.path.join('Imagens', 'tela_pausado.jpg')))
IMAGEM_PAUSADO_RESUME = (pygame.image.load(os.path.join('Imagens', 'tela_pausado_resume.jpg')))
IMAGEM_PAUSADO_RESTART = (pygame.image.load(os.path.join('Imagens', 'tela_pausado_restart.jpg')))
IMAGEM_PAUSADO_QUIT = (pygame.image.load(os.path.join('Imagens', 'tela_pausado_quit.jpg')))
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens', 'bird3.png'))),
]

pygame.font.init()
caminho_fonte = os.path.join('fonts', 'PixelOperator8.ttf')
FONTE_PONTOS = pygame.font.Font(caminho_fonte, 25)

def salvar_dados_csv(lista_genomas, pontos, geracao_num):
    arquivo_csv = 'dados_genomas.csv'
    file_exists = os.path.isfile(arquivo_csv)
    with open(arquivo_csv, mode='a', newline='') as arquivo:
        writer = csv.writer(arquivo)
        if not file_exists:
            writer.writerow(["Geracao", "ID_Genoma", "Fitness", "Pontos"])
        for genoma in lista_genomas:
            writer.writerow(["Geracao", "ID_Genoma", "Fitness", "Pontos"])

class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self, pontuacao):
        self.velocidade = -10.5 * Cano.VELOCIDADE_ATUAL
        self.tempo = 0
        self.altura = self.y

        def incrementar():
            if pontuacao % 5 == 0 and pontuacao > 0:
                self.velocidade += 5
                self.tempo += 2

        thread = threading.Thread(target=incrementar)
        thread.start()

        def resetar():
            self.velocidade = -10.5
            self.tempo = 0

        thread = threading.Thread(target=resetar)
        thread.start()

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 14:
            deslocamento = 14
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)



class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5
    VELOCIDADE_ATUAL = VELOCIDADE
    INCREMENTO_VELOCIDADE = 1.5  # Novo atributo para incrementar a velocidade

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(40, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

        if Cano.VELOCIDADE_ATUAL > 5 and Cano.VELOCIDADE_ATUAL <= 8:
            self.altura = random.randrange(50, 400)
            self.pos_topo = self.altura - self.CANO_TOPO.get_height()
            self.pos_base = self.altura + self.DISTANCIA
        elif Cano.VELOCIDADE_ATUAL >8 and Cano.VELOCIDADE_ATUAL <= 12.5:
            self.altura = random.randrange(80, 350)
            self.pos_topo = self.altura - self.CANO_TOPO.get_height()
            self.pos_base = self.altura + self.DISTANCIA
        elif Cano.VELOCIDADE_ATUAL > 12.5 and Cano.VELOCIDADE_ATUAL <=15.5:
            self.altura = random.randrange(110, 300)
            self.pos_topo = self.altura - self.CANO_TOPO.get_height()
            self.pos_base = self.altura + self.DISTANCIA
        elif Cano.VELOCIDADE_ATUAL > 15.5:
            self.altura = random.randrange(140, 250)
            self.pos_topo = self.altura - self.CANO_TOPO.get_height()
            self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= Cano.VELOCIDADE_ATUAL

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if topo_ponto or base_ponto:
            return True
        return False

    @classmethod
    def aumentar_velocidade(cls, pontuacao):
        def incrementar():
            if pontuacao % 5 == 0 and pontuacao > 0:
                cls.VELOCIDADE_ATUAL += cls.INCREMENTO_VELOCIDADE

        thread = threading.Thread(target=incrementar)
        thread.start()

    @classmethod
    def resetar_velocidade(cls):
        def resetar():
            cls.VELOCIDADE_ATUAL = cls.VELOCIDADE

        thread = threading.Thread(target=resetar)
        thread.start()


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto_sombra = FONTE_PONTOS.render(f"Pontos: {pontos}", True, (0, 0, 0))
    texto = FONTE_PONTOS.render(f"Pontos: {pontos}", True, (255, 255, 255))
    tela.blit(texto_sombra, (TELA_LARGURA - 12 - texto.get_width(), 12))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

    if ai_jogando:
        texto_sombra = FONTE_PONTOS.render(f"Nivel: {geracao}", True, (0, 0, 0))
        texto = FONTE_PONTOS.render(f"Nivel: {geracao}", True, (255, 255, 255))
        tela.blit(texto_sombra, (12, 12))
        tela.blit(texto, (10, 10))

    chao.desenhar(tela)
    pygame.display.update()

def tela_inicio(tela):
    global ai_jogando  # Adicione esta linha
    rodando = True
    escolha = 0
    while rodando:
        tela.blit(IMAGEM_BEGIN, (0, 0))

        if escolha == 1:
            tela.blit(IMAGEM_BEGIN_ESCOLHA, (0, 0))
        elif escolha == 2:
            tela.blit(IMAGEM_BEGIN_AI, (0, 0))
        elif escolha == 3:
            tela.blit(IMAGEM_BEGIN_PLAYER, (0, 0))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif evento.type == pygame.KEYDOWN:  # Verifica se houve pressionamento de tecla
                if evento.key == pygame.K_SPACE:
                    escolha = 1
                elif evento.key == pygame.K_LEFT:
                    selecionar.play()
                    escolha = 2
                elif evento.key == pygame.K_RIGHT:
                    selecionar.play()
                    escolha = 3
                elif evento.key == pygame.K_RETURN:
                    if escolha == 2:
                        ai_jogando = True
                        rodando = False
                    elif escolha == 3:
                        ai_jogando = False
                        rodando = False

def tela_pausada(tela):
    rodando = True
    opcao = 0  # 0 = Resume, 1 = Restart, 2 = Quit
    while rodando:
        if opcao == 0:
            tela.blit(IMAGEM_PAUSADO, (0, 0))
        elif opcao == 1:
            tela.blit(IMAGEM_PAUSADO_RESUME, (0, 0))
        elif opcao == 2:
            tela.blit(IMAGEM_PAUSADO_RESTART, (0, 0))
        elif opcao == 3:
            tela.blit(IMAGEM_PAUSADO_QUIT, (0, 0))
        pygame.display.update()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecionar.play()
                    opcao = (opcao - 1) % 4
                elif evento.key == pygame.K_DOWN:
                    selecionar.play()
                    opcao = (opcao + 1) % 4
                elif evento.key == pygame.K_RETURN:
                    if opcao == 1:
                        pygame.mixer.music.unpause()
                        rodando = False
                    elif opcao == 2:
                        pygame.mixer.music.stop()
                        return 'restart'
                    elif opcao == 3:
                        pygame.quit()
                        quit()


def tela_pontuacao(tela, pontos):
    tela.blit(IMAGEM_PONTUACAO, (0, 0))
    texto_sombra = FONTE_PONTOS.render(f"PONTOS: {pontos}", 1, (0, 0, 0))
    texto = FONTE_PONTOS.render(f"PONTOS: {pontos}", 1, (255, 255, 224))
    tela.blit(texto_sombra, (TELA_LARGURA - 182 - texto.get_width(), 563))
    tela.blit(texto, (TELA_LARGURA - 180 - texto.get_width(), 561))
    pygame.display.update()
    time.sleep(5)

def tela_fim(tela, pontos):
    tela_pontuacao(tela, pontos)
    fim = True
    escolha = 0  # 0 para esquerda, 1 para direita
    while fim:
        tela.blit(IMAGEM_END, (0, 0))
        texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
        tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

        if escolha == 0:
            tela.blit(IMAGEM_END, (0, 0))
        elif escolha == 1:
            tela.blit(IMAGEM_END_YES, (0, 0))
        else:
            tela.blit(IMAGEM_END_NO, (0, 0))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    selecionar.play()
                    escolha = 1
                elif evento.key == pygame.K_RIGHT:
                    selecionar.play()
                    escolha = 2
                elif evento.key == pygame.K_RETURN:
                    if escolha == 1:
                        fim = False
                        caminho_config = os.path.join(caminho, 'config.txt')
                        tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
                        tela_inicio(tela)
                        rodar(caminho_config)
                    elif escolha == 2:
                        pygame.quit()
                        quit()

def main(genomas, config):

    pygame.mixer.music.play(-1, 2)
    global geracao

    redes = []
    lista_genomas = []
    passaros = [Passaro(230, 350)]

    if ai_jogando:
        geracao += 1
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350))

    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()


    rodando = True
    while rodando:
        relogio.tick(30)

        # interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:
                    pygame.mixer.music.pause()
                    acao = tela_pausada(tela)
                    if acao == 'restart':
                        main(genomas, config)
                        return
                elif evento.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    perdeu.play()
                    tela_fim(tela,pontos)
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular(pontos)
                            voar.play()


        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].CANO_TOPO.get_width()):
                indice_cano = 1
        else:
            rodando = False
            break

        # mover as coisas
        for i, passaro in enumerate(passaros):
            passaro.mover()
            if ai_jogando:
                lista_genomas[i].fitness += 0.1
                output = redes[i].activate((passaro.y,
                                            abs(passaro.y - canos[indice_cano].altura),
                                            abs(passaro.y - canos[indice_cano].pos_base)))
                if output[0] > 0.5:
                    passaro.pular(pontos)
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                    if not ai_jogando or len(passaros) == 0:
                        pygame.mixer.music.stop()
                        perdeu.play()
                        Cano.resetar_velocidade()  # Resetar a velocidade ao colidir com o último pássaro
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            ganhou_ponto.play()
            canos.append(Cano(600))
            if ai_jogando:
                for genoma in lista_genomas:
                    genoma.fitness += 5
            Cano.aumentar_velocidade(pontos)  # Chamar a função para aumentar a velocidade

        for cano in remover_canos:
            canos.remove(cano)

        # Verificar se o pássaro colide com o chão ou vai para fora da tela
        passaros_a_remover = []
        for i, passaro in enumerate(passaros):
            if ai_jogando:
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    passaros_a_remover.append(i)
                    if len(passaros) == 0:
                        pygame.mixer.music.stop()
                        perdeu.play()
            elif not ai_jogando:
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    passaros_a_remover.append(i)
                    pygame.mixer.music.stop()
                    perdeu.play()

        for i in reversed(passaros_a_remover):
            passaros.pop(i)
            if ai_jogando:
                lista_genomas.pop(i)
                redes.pop(i)
            if not ai_jogando or len(passaros) == 0:
                Cano.resetar_velocidade()  # Resetar a velocidade ao colidir com o último pássaro

        desenhar_tela(tela, passaros, canos, chao, pontos)

    # Tela de fim
    if not ai_jogando:
        tela_fim(tela, pontos)

def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)

    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())

    if ai_jogando:
        populacao.run(main, 50)
    else:
        while True:
            main(None, None)

if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    tela_inicio(pygame.display.get_surface())
    rodar(caminho_config)
