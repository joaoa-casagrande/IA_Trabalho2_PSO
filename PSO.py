import sys
from typing import List
import os
from io import open
from matplotlib import pyplot
from random import uniform, seed
import glob
import time
import numpy as np

class Eixo:
    x:float
    y:float

    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0

class MelhorResultado:
    posicao:Eixo
    fitness:float

class Particula:
    posicao:Eixo
    velocidade:Eixo
    melhorPosicao:MelhorResultado


    def __init__(self) -> None:
        self.posicao = Eixo()
        self.velocidade = Eixo()
        self.melhorPosicao = MelhorResultado()


class Resultado:
    numParticulas:int
    numIteracoes:int
    numExecucao:int
    resultados:List[float]

    def __init__(self) -> None:
        self.numParticulas = 0
        self.numIteracoes = 0
        self.numExecucao = 0
        self.resultados = []

class MediaIteracaoExecucoes:
    numIteracao:int
    media:float

    def __init__(self, numIteracao, media) -> None:
        self.numIteracao = numIteracao
        self.media = media

class ValoresGraficoIteracao:
    numIteracoes:int
    melhorExecucao:Resultado
    medias:List[MediaIteracaoExecucoes]
    medias2:List[float]

    def __init__(self, numIteracoes, melhor) -> None:
        self.numIteracoes = numIteracoes
        self.melhorExecucao = melhor
        self.medias = []
        self.medias2 = []


FULL_PATH = os.path.realpath(__file__)
OUTPUT_PATH = os.path.dirname(FULL_PATH)+"\\output\\"

POS_MIN = -512    #Valor mínimo do intervalo de posição
POS_MAX = 512     #Valor máximo do intervalo de posição
V_FATOR = 0.15    #15% do intervalo acima
V_MIN = -77
V_MAX = 77 
N_EXEC =  10
W_MIN = 0.4
W_MAX = 0.9

C1 = 2.5
C2 = 2.5
NUMERO_PARTICULAS:int
LISTA_ITERACOES = [20, 50, 100]

#FUNÇÕES AUXILIARES#
def GerarNumeroAleatorio(minRange, maxRange):
    seed()
    return uniform(minRange, maxRange)

def LimparPastaSaida():
    files = glob.glob(OUTPUT_PATH+"*")
    for f in files:
        os.remove(f)

def ProximidadeObjetivo(fitness):
    valorBusca = f(512,404.2319)
    return np.std([valorBusca,fitness])
###

def f(x, y):
    return -(y+47)*np.sin(np.sqrt(abs((x/2)+(y+47))))-x*np.sin(np.sqrt(abs(x-(y+47))))

def GerarListaPart(numParticulas)-> List[Particula]:
    particulas = []
    velGeralX = GerarNumeroAleatorio(POS_MIN,POS_MAX)
    velGeralY = GerarNumeroAleatorio(POS_MIN,POS_MAX)

    for i in range(numParticulas):
        tempPart = Particula()

        tempPart.melhorPosicao.fitness = -1
        tempPart.posicao.x = GerarNumeroAleatorio(POS_MIN,POS_MAX)
        tempPart.posicao.y = GerarNumeroAleatorio(POS_MIN,POS_MAX)

        tempPart.velocidade.x = velGeralX
        tempPart.velocidade.y = velGeralY
        particulas.append(tempPart)
    

    return particulas

def CalcularVelocidade(melhorPosicaoEixoParticula, velAtualEixoParticula, posicaoAtualEixoParticula, melhorPosicaoEixo, wAtual):

    novaVel = (wAtual * velAtualEixoParticula) + C1 * GerarNumeroAleatorio(0,1) * (melhorPosicaoEixoParticula - posicaoAtualEixoParticula ) + C2 * GerarNumeroAleatorio(0,1) * (melhorPosicaoEixo - posicaoAtualEixoParticula)

    if novaVel > POS_MAX * V_FATOR: novaVel = POS_MAX * V_FATOR
    elif novaVel < POS_MIN * V_FATOR: novaVel = POS_MIN * V_FATOR

    return novaVel


def AtualizarPosicaoParticula(particula:Particula):

    particula.posicao.x = particula.posicao.x + particula.velocidade.x
    particula.posicao.y = particula.posicao.y + particula.velocidade.y

    if (particula.posicao.x > POS_MAX):
        particula.posicao.x = POS_MAX
        particula.velocidade.x = 0

    elif (particula.posicao.x < POS_MIN):
        particula.posicao.x = POS_MIN
        particula.velocidade.x = 0

    if (particula.posicao.y > POS_MAX):
        particula.posicao.y = POS_MAX
        particula.velocidade.y = 0

    elif (particula.posicao.y < POS_MIN):
        particula.posicao.y = POS_MIN
        particula.velocidade.y = 0

def MostrarGrafico(src, numIteracoes):

    valores:ValoresGraficoIteracao = GetValoresGrafico(src, numIteracoes)
    SalvarResultadosIteracao(valores)


    x = [i for i in range(valores.numIteracoes)]
    pyplot.plot(x,valores.melhorExecucao.resultados, label='Melhor Execução')
    pyplot.plot(x,valores.medias2, label='Medias')

    ultimoX = x[-1]
    ultimoYMelhorExecucao = valores.melhorExecucao.resultados[-1]
    ultimoYMedia = valores.medias2[-1]

    pyplot.xticks(range(min(x), numIteracoes+1, 5))
    pyplot.legend()
    pyplot.title(f"Resultado {numIteracoes} iterações")

    pyplot.xlabel("Iteração")
    pyplot.ylabel("Fitness")

    pyplot.text(ultimoX, ultimoYMelhorExecucao  + 0.0001, f"{ultimoYMelhorExecucao:.4f}", color="blue", fontsize=10)
    pyplot.text(ultimoX, ultimoYMedia  + 0.0001, f"{ultimoYMedia:.4f}", color="red", fontsize=10)

    pyplot.show()

def replace(num):
    return str("%.30f" % num).replace(".",",")

def SalvarResultadosIteracao(valores:ValoresGraficoIteracao):
    
    with open(OUTPUT_PATH+f"TABELA_RESULTADOS_{valores.numIteracoes}i.csv","a") as arq:

        arq.write(f"Iteracao;MelhorResultado;MediaResultados;\n")
        for numIteracao in range(valores.numIteracoes):
            melhor = valores.melhorExecucao.resultados[numIteracao]
            media = [x for x in valores.medias if x.numIteracao == numIteracao+1][0].media
            

            arq.write(f"{numIteracao+1};{replace(melhor)};{replace(media)};\n")

def GetValoresGrafico(src:List[Resultado], numIteracoes)->ValoresGraficoIteracao:

    melhorExecucao:Resultado = None
    lstIteracao:List[Resultado] = [x for x in src if x.numIteracoes == numIteracoes]
    for execucao in range (1,11):
        resultadoExecucao:List[Resultado] = [x for x in lstIteracao if x.numExecucao == execucao]
        if(melhorExecucao is None or ProximidadeObjetivo(resultadoExecucao[0].resultados[-1]) < ProximidadeObjetivo(melhorExecucao.resultados[-1])):
            melhorExecucao = resultadoExecucao[0]

    ret = ValoresGraficoIteracao(numIteracoes, melhorExecucao)

    for i in range(numIteracoes):

        somaIteracao:float = 0.0
        for execucao in range (1,11):
            resultadoExecucao = [x for x in lstIteracao if x.numExecucao == execucao]
            somaIteracao+= resultadoExecucao[0].resultados[i]
        mediaIteracao = MediaIteracaoExecucoes(i+1, somaIteracao/10)
        ret.medias.append(mediaIteracao)
        ret.medias2.append(somaIteracao/10)


    return ret


def AtualizarW(numIteracoes, iteracaoAtual):

    return W_MAX - iteracaoAtual*((W_MAX-W_MIN)/numIteracoes)

def main():

    resultados:List[Resultado] = []
    NUMERO_PARTICULAS = int(input("Número de partículas: "))

    #limpando pasta de saída
    if os.path.exists(OUTPUT_PATH): LimparPastaSaida()
    else: os.makedirs(OUTPUT_PATH)
    time.sleep(1)
    #

    for numExecucao in range(1,N_EXEC+1):
        for numIteracoes in LISTA_ITERACOES:
            W_atual = W_MAX
            nomeArquivo = f"{NUMERO_PARTICULAS}p_{numIteracoes}i_{numExecucao}exec.csv"

            resultado = Resultado()
            resultado.numParticulas = NUMERO_PARTICULAS
            resultado.numIteracoes = numIteracoes
            resultado.numExecucao = numExecucao

            particulas:List[Particula] = GerarListaPart(NUMERO_PARTICULAS)
            melhor:MelhorResultado = MelhorResultado()
            melhor.fitness = sys.float_info.max
            melhor.posicao = Eixo()
            
            with open(OUTPUT_PATH+nomeArquivo,"w") as arq:
                for k in range(numIteracoes):
                    for particula in particulas:
                        fitness = f(particula.posicao.x, particula.posicao.y)
                        proximidadeFitnessNovo = ProximidadeObjetivo(fitness)
                        proximidadeFitnessMelhorDaParticula = ProximidadeObjetivo(particula.melhorPosicao.fitness)
                        proximidadeFitnessMelhor = ProximidadeObjetivo(melhor.fitness)

                        if proximidadeFitnessNovo < proximidadeFitnessMelhorDaParticula or particula.melhorPosicao.fitness == -1.0:
                            particula.melhorPosicao.posicao = particula.posicao
                            particula.melhorPosicao.fitness = fitness

                            if (proximidadeFitnessNovo < proximidadeFitnessMelhor):
                                melhor.posicao = particula.posicao
                                melhor.fitness = fitness

                        particula.velocidade.x = CalcularVelocidade(particula.melhorPosicao.posicao.x, particula.velocidade.x, particula.posicao.x, melhor.posicao.x, W_atual)
                        particula.velocidade.y = CalcularVelocidade(particula.melhorPosicao.posicao.y, particula.velocidade.y, particula.posicao.y, melhor.posicao.y, W_atual)
                        AtualizarPosicaoParticula(particula)
                    arq.write(f"{k+1};{melhor.fitness:.30f}\n")

                    resultado.resultados.append(melhor.fitness)
                    W_atual = AtualizarW(numIteracoes, k+1)

            resultados.append(resultado)
            

    for qtdIter in LISTA_ITERACOES:
        MostrarGrafico(resultados, qtdIter)
    
        

main()

