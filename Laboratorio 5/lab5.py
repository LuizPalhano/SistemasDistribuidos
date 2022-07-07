import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import os
import time

'''
    #Declaração de variáveis readonly
'''
PORT_NUMBER_BASE = 6543 #Deslocamento inicial do número de porta

'''
    #Inicialização; roda exatamente uma vez
'''
appID = input("Digite o ID da thread:\n") #ID da thread
appID = int(appID)
port = PORT_NUMBER_BASE + appID

'''
    #Declaração de variáveis globais
'''
copyTarget = 0 #Variável que será replicada
#Chapéu. Inicialmente pertence ao processo 1
if appID == 1:
    hasHat = True
else:
    hasHat = False
isWriting = False #Indica se está alterando o alvo
queue = [] #Fila de espera para escrita
history = {} #Histórico de mudanças

'''
    #Interface do usuário
'''
def ui():
    #Variáveis descritas acima
    global appID
    global copyTarget
    global hasHat
    global isWriting
    global queue
    global history

    print("\nEscolha uma operação para ser executada.\n")
    #Roda dentro de um loop infinito; só sai quando o usuário pede para sair
    while True:
        print("Ler: mostra o valor da variável replicada\n")
        print("Hst: mostra o histórico de alterações da variável replicada\n")
        print("Alt: muda o valor da variável a ser replicada\n")
        print("Fim: fecha o programa\n")
        choice = input()
        choice = choice.lower()

        #Mostra o valor de copyTarget
        if choice == "ler":
            print("Valor da variável alvo: {}\n".format(copyTarget))

        #Mostra o histórico de alterações
        elif choice == "hst":
            print("Histórico de alterações:{}\n".format(history))
        
        #Tenta realizar a escrita
        elif choice == "alt":
            #Checa se o processo já possui o chapéu:
            
            #Se não tiver, entra na fila até o processo que tem não estar escrevendo. Quando não estiver, pega o chapéu e escreve
            if not hasHat:
                #Pega as filas dos outros processos que podem estar na fila
                for i in range(4):
                    otherID = i + 1
                    if otherID != appID:
                        conn = rpyc.connect('localhost', PORT_NUMBER_BASE + i + 1)
                        currentQueue = conn.root.exposed_getQueue()
                        if len(currentQueue) != 0:                            
                            for process in currentQueue:
                                queue.append(process)
                        conn.close()
                queue.append(appID)

                #Elimina quaisquer duplicatas
                try:
                    queue = list(dict.fromkeys(queue))
                except:
                    pass

                #Espera o processo que está escrevendo terminar de escrever
                while True:
                    #Espera um segundo para não chamar a função constantemente
                    time.sleep(1)

                    #Procura pelo processo com o chapéu
                    for i in range(4):
                        candidate = i + 1
                        if candidate != appID:
                            conn = rpyc.connect('localhost', PORT_NUMBER_BASE + candidate)
                            hatHaver = conn.root.exposed_getHasHat()
                            conn.close()
                            if hatHaver:
                                conn = rpyc.connect('localhost', PORT_NUMBER_BASE + candidate)
                                currentlyWriting = conn.root.exposed_getIsWriting()
                                conn.close()
                                break
                    
                    #Quando não tem mais ninguém escrevendo nem nenhum outro processo na fila, pega o chapéu e sai da fila.
                    #Atualiza a fila para todos os outros antes de sair
                    if not currentlyWriting and len(queue) == 1:
                        primaryCopy.exposed_takeHat(primaryCopy, candidate)
                        isWriting = True
                        queue.remove(appID)
                        for i in range(4):
                            otherID = i + 1
                            if otherID != appID:
                                conn = rpyc.connect('localhost', PORT_NUMBER_BASE + otherID)
                                conn.root.exposed_updateQueue(appID)
                                conn.close()
                        #Quando termina de avisar os outros que saiu da fila, sai do loop
                        break
            
            #Se já tiver o chapéu, ou ao obtê-lo, marca que está executando uma escrita e a inicia
            else:
                isWriting = True
            newValue = input("Digite o novo valor da variável replicada\n")
            newValue = int(newValue)
            primaryCopy.exposed_setTargetLocal(primaryCopy, newValue)
            for k in range (4):
                testID = k + 1
                if testID != appID:
                    conn = rpyc.connect('localhost', PORT_NUMBER_BASE + testID)
                    conn.root.exposed_setTargetGlobal(appID, copyTarget)
                    conn.close()
            isWriting = False
            print("\n")
        
        #Fecha a aplicação
        elif choice == "fim":
            os._exit(1)
        
        #Caso o usuário não tenha feito uma escolha válida
        else:
            print("\nPor favor, entre com um comando válido.")
        #while True, volta para o começo
    
'''
    #Classe que agrega as funções usadas
'''
class primaryCopy(rpyc.Service):
    #Retorna se está escrevendo
    def exposed_getIsWriting(self):
        global isWriting
        return isWriting
    
    #Retorna se o processo tem o chapéu
    def exposed_getHasHat(self):
        global hasHat
        return hasHat
    
    #Pega o chapéu de outro processo
    def exposed_takeHat(self, hatID):
        global hasHat
        conn = rpyc.connect('localhost', PORT_NUMBER_BASE + hatID)
        conn.root.exposed_removeHat()
        conn.close()
        hasHat = True
    
    #Tira o chapéu do processo com o chapéu             
    def exposed_removeHat(self):
        global hasHat
        hasHat = False
    
    #Retorna se o processo está na fila
    def exposed_getQueue(self):
        global queue
        return queue
    
    #Atualiza a fila de todos os outros processos
    def exposed_updateQueue(self, removedID):
        global queue
        try:
            queue.remove(removedID)
        except:
            pass
    
    #Muda o valor da variável alvo localmente    
    def exposed_setTargetLocal(self, newValue):
        global copyTarget
        global appID
        global hasHat 
        copyTarget = newValue
        aux1 = []
        aux2 = {}
        try:
            for i in history[appID]:
                aux1.append(i)
        except:
            pass
        aux1.append(copyTarget)
        aux2[appID] = aux1
        history.update(aux2)
                    
    #Muda o valor da variável alvo em todos os outros processos depois que aquele com o chapéu fez suas modificações
    def exposed_setTargetGlobal(self, appID, mod):
        global copyTarget
        global history
        copyTarget = mod
        aux1 = []
        aux2 = {}
        try:
            for i in history[appID]:
                aux1.append(i)
        except:
            pass
        aux1.append(copyTarget)
        aux2[appID] = aux1
        history.update(aux2)

'''
    #"Main". Inicia o programa
'''
thread = threading.Thread(target = ui, args=())
thread.start()
server = ThreadedServer(primaryCopy, port = port)
server.start()
