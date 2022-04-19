# Exemplo basico socket (lado ativo)

import socket

HOST = '' # maquina onde esta o par passivo
PORTA = 10000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

while True:
    # envia uma mensagem para o par conectado
    msg = input("Digite a mensagem que deseja enviar\n")
    sock.send(bytes(msg , 'utf-8'))
    
    if msg == 'pare':
        print('Enviando mensagem para encerrar o programa')
        break
    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    msg = sock.recv(1024) # argumento indica a qtde maxima de bytes da mensagem
    
    # imprime a mensagem recebida
    print(str(msg, 'utf-8'))

# encerra a conexao
sock.close() 
