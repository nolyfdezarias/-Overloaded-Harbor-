 
import sys
import heapq
from utils import *

 
class Barco():
    def __init__(self,tiempoDellegada,id = 0):
        self.tiempoDeEspera = 0 #tiempo de espera global
        self.tiempoEnPuerto = 0
        self.tiempoEnMuelle = 0
        self.tiempoDeLlegadaAlMuelle = 0
        self.tiempoDeLlegadaAlPuerto = tiempoDellegada
        self.tiempoDeSalidaPalPueto = 0
        self.tipo = self.generarTipo()
        self.tiempoDeCarga = self.generarTiempoDeCarga(self.tipo)
        self.id = id
    
    def __lt__(self,other):
        if self.id < other.id:
            return True
        return False

    def generarTipo (self):
        r = random.random()
        if r <= 0.25:
            return 0
        if r <= 0.5:
            return 1
        return 2
    
    def generarTiempoDeCarga(self,tipo):
        if tipo == 0:
            return normal(9, 1) * 60

        if tipo == 1:
            return normal(12, 2) * 60

        return normal(18, 3) * 60

class Muelle():
    def __init__(self):
        self.finCarga  = 0
        self.barco = None

class Remorcador():
    def __init__(self):
        self.lugar = "Puerto"

class Puerto():
    def __init__(self,tiempoDeSimulacion,nombre = "Pepito"):
        self.muelles = [Muelle(),Muelle(),Muelle()]
        self.remolcador = Remorcador()
        self.tiempoDeSimulacion = tiempoDeSimulacion
        self.colaDeBarcos = []
        self.eventos = []
        self.tiempoActual = 0
        self.arribo = 0
        self.espera = 0 #espera en el muelle
        self.tiempoDeEsperaTotal = 0
        self.tiempoEnPuerto = 0
        self.barcosAtendidos = 0
        self.barcoId = 1
        
    
    def generarArriboDebarcos(self):
        return exponencial(8) * 60
        #return exponencial(8*60)

    def generarTrasladoDeRemolcador(self):
        return exponencial(15)

    def generarLlevarBarcoAlMuelle(self):
        return exponencial(2) * 60
        #return exponencial(2 * 60)
    def generarSacarBarcoDelPuerto(self):
        return exponencial(1) * 60
        #return exponencial(1*60)

    def llevarBarcoAlMuelle(self,barco,pos):
        
        if self.remolcador.lugar == 'Muelle':
            self.tiempoActual += self.generarTrasladoDeRemolcador()

        self.tiempoActual += self.generarLlevarBarcoAlMuelle()
        barco.tiempoDeLlegadaAlMuelle = self.tiempoActual
        muelle = self.muelles[pos]
        muelle.barco = barco
        muelle.finCarga = self.tiempoActual + barco.tiempoDeCarga
        self.remolcador.lugar = 'Muelle'
        heapq.heappush(self.eventos,((muelle.finCarga,barco.id) , ("Fin de Carga" , barco , pos)))

    
    def muelleLibre(self):  # da algun muelle si esta libre

        pos = [x for x in range(len(self.muelles))  if self.muelles[x].barco == None]
        if len(pos) > 0:
            return pos[0]
        return -1 
    

    def sacarBarcoDelMuelle(self,pos):

        if self.remolcador.lugar == 'Puerto':
            self.tiempoActual += self.generarTrasladoDeRemolcador()

        barco = self.muelles[pos].barco
        barco.finCarga = self.muelles[pos].finCarga
        

        llegada = barco.tiempoDeLlegadaAlMuelle
        salida = barco.finCarga
        barco.tiempoEnMuelle = salida - llegada

        tiempoS = self.tiempoActual
        self.tiempoActual += self.generarSacarBarcoDelPuerto()
        barco.tiempoEnPuerto = self.tiempoActual - barco.tiempoDeLlegadaAlPuerto
        
        barco.tiempoDeEspera = (barco.tiempoDeLlegadaAlMuelle - barco.tiempoDeLlegadaAlPuerto) + (tiempoS - self.muelles[pos].finCarga)


        self.remolcador.lugar = 'Puerto'

        self.barcosAtendidos += 1

        print(f'Espera del barco {barco.id} en el muelle:{barco.tiempoEnMuelle / 60} ' )
        print(f'Tiempo del barco {barco.id} en el puerto: {barco.tiempoEnPuerto / 60}'  )
        print(f'Espera del barco {barco.id} en colas del puerto: {barco.tiempoDeEspera / 60}'  )

        self.espera += barco.tiempoEnMuelle
        self.tiempoEnPuerto += barco.tiempoEnPuerto
        self.tiempoDeEsperaTotal += barco.tiempoDeEspera

        self.muelles[pos].barco = None
    
    def simulacion(self):
        
        while self.tiempoActual < self.tiempoDeSimulacion :

            #proximoArribo = self.tiempoActual + self.generarArriboDebarcos()
            self.arribo += self.generarArriboDebarcos() 
            proximoArribo = self.arribo
            barco = Barco(id = self.barcoId,tiempoDellegada = proximoArribo)
            self.barcoId += 1
            self.colaDeBarcos.append(barco)
            muelleLibre = self.muelleLibre()

            if muelleLibre != -1:
                barco = self.colaDeBarcos.pop(0)
                heapq.heappush(self.eventos, ((barco.tiempoDeLlegadaAlPuerto,barco.id), ("Llevar al Muelle", barco, muelleLibre)))
            
                

            if len(self.eventos) > 0:
                evento = heapq.heappop(self.eventos)
                accion , barco , muelle = evento[1]

                if accion == "Llevar al Muelle":
                    self.tiempoActual = max(evento [0][0], self.tiempoActual)
                    self.llevarBarcoAlMuelle(barco,muelle)
                elif accion == "Fin de Carga":
                    self.tiempoActual = max(self.muelles[muelle].finCarga,self.tiempoActual)
                    heapq.heappush(self.eventos, ((self.muelles[muelle].finCarga, self.muelles[muelle].barco.id ), ("Salir del Muelle", barco, muelle)))
                elif accion == "Salir del Muelle":
                    self.sacarBarcoDelMuelle(muelle)


    def estadisticaDeSimulacion(self):
        if self.barcosAtendidos > 0:
            esperaBarcos = self.espera / self.barcosAtendidos / 60
            tiempoEnPuerto = self.tiempoEnPuerto / self.barcosAtendidos / 60
            tiempoDeEspera = self.tiempoDeEsperaTotal / self.barcosAtendidos / 60
            

            print("----------------------------------------------------------------------")
            print("Barcos atendidos: ", self.barcosAtendidos)
            print("Promedio total de demora de los barcos en el muelle en una corrida: ", esperaBarcos )
            print("Promedio total del tiempo de los barcos en el puerto en una corrida: ", tiempoEnPuerto )
            print("Promedio total del tiempo de espera de los barcos en las colass del puerto en una corrida: ", tiempoDeEspera )

            return (self.espera ,self.tiempoEnPuerto  ,self.tiempoDeEsperaTotal , self.barcosAtendidos)

        else:
            print("No se han atendido barcos")
            return 0,0,0,0

        

def main():
    veces = 0
    duracion = 0
    cantidadDeBarcos = 0
    tiempoDeEsperaEnElMuelle = 0
    tiempoEnElPuerto = 0
    tiempoDeEsperaEnElPuerto = 0

    
    if len(sys.argv) < 3 :
        veces = 45
        duracion = 24

    else :
        veces = int(sys.argv[1])
        duracion = int(sys.argv[2])

    for i in range(veces):
        print("#"*100)
        print(f"Corrida: {i+1}")  
        p = Puerto(tiempoDeSimulacion = duracion * 60)
        p.simulacion()
        esperaBarcos ,tiempoEnPuerto ,tiempoDeEspera , barcosAtendidos = p.estadisticaDeSimulacion()
        cantidadDeBarcos += barcosAtendidos
        tiempoDeEsperaEnElMuelle += esperaBarcos
        tiempoDeEsperaEnElPuerto += tiempoDeEspera
        tiempoEnElPuerto += tiempoEnPuerto
    
    if cantidadDeBarcos > 0:
        print("@"*100)
        print("Total de Barcos atendidos: ", cantidadDeBarcos)
        print("Promedio total de demora de los barcos en el muelle en todas las corridas: ", tiempoDeEsperaEnElMuelle / cantidadDeBarcos /60 )
        print("Promedio total del tiempo de los barcos en el puerto en todas las corridas: ", tiempoEnElPuerto / cantidadDeBarcos / 60 )
        print("Promedio total del tiempo de espera de los barcos en las colas del puerto en todas las corridas: ", tiempoDeEsperaEnElPuerto/ cantidadDeBarcos / 60)
    else:
        print("No se atendieron barcos")

main()
