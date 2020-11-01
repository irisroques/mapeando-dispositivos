#!/usr/bin/env python
#__Author__: gnoo

from socket import *
import threading
from datetime import datetime
from queue import Queue
import geoip2.database
import time


lista_ip = open("lista_ip.txt", "r")                                                                                                                             # Abre arq. onde estão os IP's para teste

ip_em_lista = lista_ip.readlines()                                                                                                     # Lê as linhas do arq. aberto anteriormente
 
resultado_backup = open("hosts_ativos.txt", "a")                                                                                           # se não existe, cria um arq. e armazena informação sobre os hosts ativos 

numero_host = len(open("lista_ip.txt").readlines())                                                                                      # conta nr de hosts no arq.

lista_host_ativo = []                                                                                                                                                     # armazena os hosts detectados 

porto = 80



segura_saida = threading.Lock()                                                                                                                              # impede que a ação das Threads multiplique o mesmo output e o repita

def localizador():

    if len(lista_host_ativo) == 0:                                                                                                                                 # se não houver hosts na lista fecha programa
            print("[-]Não foram encontrados hosts ativos")
    else:
        resultado_backup.write("Data:{}\n\n".format(str(datetime.now())))                                              # escreve data no arquivo ref. anteriormente
        for hosts in lista_host_ativo: # percorre a lista de hosts ativos, onde são aplicadas as intruções dadas no bloco que segue a cada iteração... até ao ultimo host.
            try:
                sock_head = socket(AF_INET,SOCK_STREAM)                                                                                     # inicia objeto socket
                sock_head.connect_ex((hosts, porto))                                                                                                    # Faz a conexão a cada host na lista no porto definido
                sock_head.sendall(b"HEAD / HTTP/1.1\r\nHost:%a\r\n\r\n" %hosts)                                     # Faz requisição HTTP com método HEAD
                header = sock_head.recv(1024)                                                                                                                 # Recebe resposta com cabeçalho 
                sock_head.close()                                                                                                                                            # fecha socket
            except:
                pass
            
            time.sleep(2)                                                                                                                                                           # Pausa o programa dois segundo 
            
            print("\033[5;92m[+]Host ativo\033[00m: {}".format(hosts))                                                             # identifica host
            base_dados = geoip2.database.Reader('GeoLite2-City.mmdb')                                                         # inicia leitura base dados para identificar localização do host
            resposta= base_dados.city(hosts)                                                                                                                 # é armazenada a resposta da localização do host que passa na função city() 
            print("\033[1;93m-País:\033[00m {}".format(resposta.country.name))                                         # informa país origem
            print("\033[1;93m-Cidade:\033[00m {}".format(resposta.city.name))                                            # informa cidade origem
            print("\033[1;96m««« HTTP HEAD Request »»»\033[00m\n{}\n\n".format(header.decode())) # converte resposta em formato de byte para string
            resultado_backup.writelines("Host ativo: {}\n".format(hosts))                                                         # escreve no arq. de backup host identificado
            resultado_backup.writelines("País: {}\n".format(resposta.country.name))                                  # escreve no arq. de backup país identificado
            resultado_backup.writelines("{}\n\n".format(header.decode()))                                                      # escreve no arq. de backup headers
            time.sleep(3)
        
        resultado_backup.close()                                                                                                                                      # fecha arquivo backup
        print(lista_host_ativo)                                                                                                                                            # output hosts em lista 

def scan_tcp(host):
    try:
        sock = socket(AF_INET,SOCK_STREAM)                                                                                                            # inicia objecto socket
        setdefaulttimeout(1)                                                                                                                                                 # define o tempo de ligação no porto definido 
        resultado = sock.connect_ex((host, porto))                                                                                                     # Faz a conexão a cada host na lista no porto definido
        print("TCP/{} a testar Host: {} \r".format(porto,host), end="")                                                                  # informa host a ser testado no momento
        with segura_saida:
            if resultado == 0:                                                                                                                                                    # confirma se ligação é efetuada... se sim, passa para instruções dadas
                lista_host_ativo.append(host.rstrip())                                                                                                     # adiciona cada host ativo à lista
            else:
               pass
    except:
        pass
def thread():
    while True:
        acao=q.get()                                                                                                                                                                 # retira e recebe dados em fila 
        scan_tcp(acao)                                                                                                                                                           # função scan_tcp recebe parametros em fila ... host 
        q.task_done()                                                                                                                                                              # termina tarefa 
        

def executa_scan_tcp():
    global q

    q = Queue()                                                                                                                                                                        # inicia objeto 

    for y in range(5):                                                                                                                                                              # Define número de Threads
        tarefa= threading.Thread(target=thread)
        tarefa.daemon=True
        tarefa.start()

        
        
    t1 = datetime.now()
    
    for host in ip_em_lista:                                                                                                                                                  # percorre lista de ip 
        q.put(host)                                                                                                                                                                      # põe dados em fila... parâmetros que vão passar na função scan_tcp()
    q.join()                                                                                                                                                                                   # Espera que todos os dados sejam tratados, e as threads terminem,
                                                                                                                                                                                                     # para terminar com auxilio da função task_done()

    
    t2 = datetime.now()
    total_tempo = t2-t1
    print("Operação terminada em {}\n\n".format(total_tempo))                                                                        # informa tempo de duração do programa 

print("\033[1;35m>>>>  A Iniciar Scan ---- Nº Hosts:\033[00m {}\n\n".format(numero_host))           # output inf. inicio prog. com total de hosts a tratar   
time.sleep(2)
def main():
    executa_scan_tcp()
    print("\n\nA Resolver Total de {} Hosts encontrados\n\n".format(len(lista_host_ativo)))               # Informa nr de hosts encontrados para resolver 
    time.sleep(3)
    localizador()

if __name__ == '__main__':
    main()