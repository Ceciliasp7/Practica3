""" PRÁCTICA 3 PROGRAMACIÓN PARALELA.
    Sergio Rodrigo Angulo, Cecilia Sánchez Plaza, Pablo Sierra Erice"""
    
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import time

LEFT_GOALKEEPER = 0
RIGHT_GOALKEEPER = 1
LEFT_ATTACKER= 2
RIGHT_ATTACKER=3
SIDESSTR = ["portero rojo", "portero azul","delantero rojo", "delantero azul"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 30
TIEMPO=30

class Player():
    """ En esta clase aparecen las funciones que implementan las posiciones y movimientos de cada uno de los jugadores"""
    
    def __init__(self, side): #En esta función se decide la posición de la pelota y los jugadores al principio de juego
        self.side = side
        if side == LEFT_GOALKEEPER:
            self.pos = [10, SIZE[Y]//2]
        elif side== LEFT_ATTACKER:
            self.pos = [175, SIZE[Y]//2]
        elif side== RIGHT_ATTACKER:
            self.pos = [SIZE[X] - 175, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 10, SIZE[Y]//2]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side
    # estas funciones determinan los posibles movimientos que pueden hacer los jugadores
    def moveDown(self):
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"

class Ball():
    """ Esta clase determina la posicion y el movimieno de la pelota """
    def __init__(self, velocity):
        self.pos=[ SIZE[X]//2, SIZE[Y]//2 ]  #Empieza estando en el centro deol tablero
        self.velocity = velocity

    def get_pos(self):
        return self.pos

    def update(self):                       #La posición de la pelota se va actulizando en ambos ejes en función del vector 
                                            #velocity que entra como párametro de la clase Ball
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]  #Para que rebote invierte el sentido del vector

    def collide_player(self, side):             #Determina el comportamiento de la pelota al rebotar con un jugador.
        self.bounce(X)
        self.pos[X] += 3*self.velocity[X]
        self.pos[Y] += 3*self.velocity[Y]


    def __str__(self):
        return f"B<{self.pos, self.velocity}>"


class Game():
    def __init__(self, manager):    #Inicializa cada componete del juego y define los elementos necesarios para gestionar 
                                    #la ejeciución del juego de forma distribuida
        self.time=time.time()
        self.players = manager.list( [Player(i) for i in range(4)] )  #Lista de cada jugador
        self.ball = manager.list( [ Ball([-4,4]) ] ) # la pelota con la velocidad metida como parámetro
        self.score = manager.list( [0,0] )  # el marcador
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()

    def get_player(self, side):
        return self.players[side]

    def get_ball(self):
        return self.ball[0]

    def get_score(self):
        return list(self.score)

    def is_running(self):         #Si el valor es 1 el programa continiua
        return self.running.value == 1

    def stop(self):
        if time.time() - self.time > TIEMPO: # el programa para cuando la diferencia entre el tiempo al iniciarse
            self.running.value = 0           # la sala y el tiempo en el momento en que se accede a la función stop 
                                             # supera la costante TIEMPO
                                             
    def end(self):           
        self.running.value = 0   #Cambia el valor a 0 pra que el programa pare
        
    # Las siguientes funciones se implementan para gestionar los movimientos de los jugadores de forma distribuida mediante un lock.
    def moveUp(self, player):   
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()
        
    #De manera ánaloga con la pelota rebotando en los jugadores
    def ball_collide(self, player):
        self.lock.acquire()
        ball = self.ball[0]
        ball.collide_player(player)
        self.ball[0] = ball
        self.lock.release()

    def get_info(self):     #recoge la información de cada uno de los "player" de cada jugador
        info = {
            'pos_LEFT_GOALKEEPER': self.players[LEFT_GOALKEEPER].get_pos(),
            'pos_RIGHT_GOALKEEPER': self.players[RIGHT_GOALKEEPER].get_pos(),
            'pos_LEFT_ATTACKER': self.players[LEFT_ATTACKER].get_pos(),
            'pos_RIGHT_ATTACKER': self.players[RIGHT_ATTACKER].get_pos(),
            'pos_ball': self.ball[0].get_pos(),
            'score': list(self.score),
            'is_running': self.running.value == 1,
            'time': self.time
        }
        return info

    def move_ball(self):    #Determina los movimientos de la bola (donde debe rebotar)
        self.lock.acquire() #también utiliza un lock para poder gestionar cada movimiento
        ball = self.ball[0]
        ball.update()
        pos = ball.get_pos()
        if pos[Y]<0 or pos[Y]>SIZE[Y]:
            ball.bounce(Y)
        if pos[X]>SIZE[X]:
            ball.bounce(X)
            if 131 < pos[Y] and pos[Y] < 394:     #Sirve para gestionar los límites de la portería
                self.score[LEFT_GOALKEEPER] += 1
        elif pos[X]<0:
            ball.bounce(X)
            if 131 < pos[Y] and pos[Y] < 394:
                self.score[RIGHT_GOALKEEPER] += 1
        self.ball[0]=ball
        self.lock.release()


    def __str__(self):
        return f"G<{self.players[RIGHT_GOALKEEPER]}:{self.players[LEFT_GOALKEEPER]}:{self.ball[0]}:{self.running.value}>"

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""                        #Los "controles" de cada función que tiene el juego: los movimientos y como continua o por el contrario como salir de él
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "collide":
                    game.ball_collide(side)
                elif command == "quit":
                    game.end()    
             
            if side == 3:     #En cuanto los jugadores están conectados la bola empieza a moverse y el juego comienza hasta
                                # que la condión de stop determina el final de juego
                game.move_ball()
                if game.stop(): 
                    return f"GAME OVER"
                
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    
    manager = Manager()
    
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None, None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 4:
                    players[0].start()
                    players[1].start()
                    players[2].start()
                    players[3].start()
                    n_player = 0
                    players = [None, None, None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
