from unittest.main import main
import rpyc
from rpyc.utils.server import ThreadedServer
import random
from sys import exit

topografia = []
id = int(input("Informe o ID referente a sua aplicação (1 ate n)"))
porta = 5000 + id 
    
with open('topografia.txt') as arquivo:
    topografia = arquivo.readlines()

topografia = topografia[id-1]
topografia = topografia.replace("\n","")
vizinhos = topografia.split(" ")
print (vizinhos)
probe = False
no_pai = 0
cont = 0
retorno = []
filhos = []
tipo = 0
wait = True
inicial = False
filho = []

class ProbEcho(rpyc.Service):
    
    def on_connect(self,conn):
        print("Conexão iniciada")
    
    def on_disconnect(self,conn):
        print("Conexão encerrada") 

    def exposed_reset(self):
        global probe
        global no_pai
        global cont
        global retorno
        global filhos
        global tipo
        global wait
        global inicial
        global filho
        probe = False
        no_pai = 0
        cont = 0
        retorno = []
        filhos = []
        tipo = 0
        wait = True
        inicial = False
        filho = []
    
    def exposed_election(self,tipo):
        global vizinhos
        global retorno
        global wait
        global inicial
        global id
        print("Votação iniciada pelo processo {}".format(id))
        print(no_pai)
        if no_pai != 0:
            try:
                print("Removedo pai {}".format(no_pai))
                vizinhos.remove(str(no_pai))
                print("Testando remove\n")
                print(vizinhos)
            except:
                pass
        else:
            print("Processo {} e o inicial".format(id))
            inicial = True
        print("vizinhos:{}".format(vizinhos))
        print(vizinhos)
        for i,vizinho in enumerate(vizinhos):
            conn = rpyc.connect('localhost', 5000+int(vizinho))
            retornin = conn.root.exposed_probe(id)
            conn.close()
            if retornin != 'ACK':
                filhos.append(int(vizinho))
                print("filhos:{}".format(filhos))
                print("mandando {} iniciar sua eleição".format(int(vizinho)))
                conn = rpyc.connect('localhost', 5000+int(vizinho))
                conn.root.exposed_election(tipo)
                conn.close()
        print("Cabaram os vizinho do {}".format(id))               
        if cont == len(vizinhos):
            print("Its echo time")
            retorno.append(id)
            print(retorno)
            if tipo == 'M':
                max(retorno)
            elif tipo == 'm':
                min(retorno)
            print("retorno final:{}".format(retorno))
            print(" no pai final{}".format(no_pai))
            conn = rpyc.connect('localhost', 5000 + no_pai)
            print("ponto 1")
            conn.root.exposed_echo(id,retorno)
            print("ponto 2")
            conn.close()
        else:
            while wait:
                if filhos == [] and not inicial:
                    wait = False
                    conn = rpyc.connect('localhost',5000+no_pai)
                    retorno.append(id)
                    if tipo == 'M':
                        max(retorno)
                    elif tipo == 'm':
                        min(retorno)
                    conn.root.exposed_echo(id,retorno)
                    conn.close()
                elif filhos == [] and inicial:
                    print("Pra fechar..")
                    print("retorno final do mal: {}".format(retorno))
                    retorno.append(id)
                    retorno = list(set(retorno))
                    if tipo == 'M':
                        return max(retorno)
                    elif tipo == 'm':
                        return min(retorno)
            
    def exposed_probe(self,id_pai):
        global probe
        global no_pai
        global cont
        if probe:
            cont = cont + 1
            return "ACK"
        else:
            probe = True
            no_pai = id_pai
            print(no_pai)
        
        
    def exposed_echo(self,id_filho,retorno_filho):
        print("Echo enviado, hora de morbar")
        global retorno
        global filhos
        retorno.extend(retorno_filho)
        try:
            filhos.remove(id_filho)
        except:
            print("Falha ao remover {} de {} na função echo dos cria".format(id_filho,filhos))
        print(retorno)
       
            

if __name__ == "__main__":
    server = ThreadedServer(ProbEcho,port = porta)
    server.start()
