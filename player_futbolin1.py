""" PRÁCTICA 3 PROGRAMACIÓN PARALELA.
    Sergio Rodrigo Angulo, Cecilia Sánchez Plaza, Pablo Sierra Erice"""


from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import time

'''
En nuestro futbolín vamos a recrear una partida de cuatro jugadores: dos 
equipos de un atacante y un portero cada uno.
Creamos un conjunto de variables para describir el color y las dimensiones 
de los jugadores. Le asignamos a cada jugador del futbolín un valor de 0 a 3 
para poder acceder a los vectores que están implementados en el código.
'''

LEFT_GOALKEEPER = 0
RIGHT_GOALKEEPER = 1
LEFT_ATTACKER= 2
RIGHT_ATTACKER=3

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
PLAYER_COLOR = [RED, BLUE, RED,BLUE] 
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 10

X = 0
Y = 1
SIZE = (700, 525) #Tamaño del campo de fútbol

TIEMPO=30  #El juego finaliza a los 30 segundos
FPS = 60  #Velocidad del cronómetro


SIDES = ["portero rojo", "portero azul","delantero rojo","delantero azul"]
SIDESSTR = ["portero rojo", "portero azul","delantero rojo","delantero azul"]

'''
La clase player la utilizamos para definir la posición de cada jugador en el 
campo.
'''
class Player():
    
    def __init__(self, side): #La clase player necesita el parámetro side para saber sobre
                              # que jugador(del vector SIDES de 0 a 3) se está ejecutando las funciones de esta clase
        self.side = side
        self.pos = [None, None] #Para cada jugador tenemos una posición pos inicializada 
                                #con dos coordenadas vacías que indicanrán la posición en 
                                #los ejes de coordenadas

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

'''
La clase Ball la utilizamos para definir la posición de la bola.
'''
class Ball():
    def __init__(self):  #En este caso no necesita parámetros porque solo hay una bola
        self.pos=[ None, None ]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"

class Game():
    def __init__(self,gameinfo):
        self.players = [Player(i) for i in range(4)] #crea en Game los 4 jugadores accediendo a la clase PLayer(i)
        self.ball = Ball()  #Accediendo a Ball() crea la pelota en Game
        self.score = [0,0]  #Inicializa el score de cada equipo en 0
        self.running = True  #Crea una variable booleana running que indica si el juego se está ejecutando o no
        self.time = gameinfo['time']  

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def get_ball(self):
        return self.ball

    def set_ball_pos(self, pos):
        self.ball.set_pos(pos)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
        
    def get_time(self):
        return self.time
    
    def set_time(self, time):
        self.time=time

    def update(self, gameinfo):
        self.set_pos_player(LEFT_GOALKEEPER, gameinfo['pos_LEFT_GOALKEEPER'])
        self.set_pos_player(RIGHT_GOALKEEPER, gameinfo['pos_RIGHT_GOALKEEPER'])
        self.set_pos_player(LEFT_ATTACKER, gameinfo['pos_LEFT_ATTACKER'])
        self.set_pos_player(RIGHT_ATTACKER, gameinfo['pos_RIGHT_ATTACKER'])
        self.set_ball_pos(gameinfo['pos_ball'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):      # El juego para cuando la variable running se vuelve falsa
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_GOALKEEPER]}:{self.players[LEFT_GOALKEEPER]}:{self.players[RIGHT_ATTACKER]}:{self.players[LEFT_ATTACKER]}:{self.ball}>"

'''
En la clase Paddle se define la representación gráfica de los jugadores y define 
su posición en el campo.
'''
class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):  #Necesita un parámetro para saber que jugador estamos ejecutando
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)#drawing the paddle
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
      self.rect = self.image.get_rect()
      self.update()

    def update(self):     # Actualiza la posición de cada jugador a lo largo del juego.
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"

'''
La clase BallSprite define la representación gráfica de la pelota que vamos a 
utilizar en el partido y define la posición de la misma en el campo.
'''

class BallSprite(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.image.load('pelota.png')  #implmenta la imagen la imagen de la pelota de futbol
        self.rect = self.image.get_rect()
        self.update()

    def update(self):  # Actualiza la posición de cada jugador a lo largo del juego.
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos

'''
La clase Display hace referencia a cómo se muestra el juego por pantalla. 
Consta de cuatro funciones:.
    
'''
class Display():
    def __init__(self, game):   #Inicializa todos los elementos que aparecen por pantalla
                                #entrando como parámetro game que accede a la clase game donde hemos 
                                #creado todos los elementos necesarios para ejecutar el juego.
        self.game = game
        #self.score=game.get_score()
        self.time=game.get_time()   
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(4)] #Utiliza un bucle que genera cada pala de cada jugador

        self.ball = BallSprite(self.game.get_ball())
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        self.all_sprites.add(self.ball)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.time_group=pygame.sprite.Group()
        self.background = pygame.image.load('campo.png')
        pygame.init()

    def analyze_events(self, side): #gestiona los movimientos que puede hacer cada jugador 
                                    #indicando que comando hay que utilizar.
        events = []                 #Además en events se almacena todos los comandos utilizados por cada jugador
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
            elif event.type == pygame.QUIT:
                events.append("quit")
        if pygame.sprite.collide_rect(self.ball, self.paddles[side]):
            events.append("collide")
        return events


    def refresh(self):  #Determina la forma, el tamño y el color del maracador
                        #También se encarga de ir actualizandolo durante el juego si un equipo mete un gol
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        time=self.game.get_time()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[LEFT_GOALKEEPER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[RIGHT_GOALKEEPER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):   #Gestiona el marcador del tiempo accediendo al tiempo en sala y 
                      #mostrándolo por pantalla
        font2 = pygame.font.Font(None,30)
        clock = (pygame.time.get_ticks())//1000
        #tiempo = TIEMPO-clock
        self.clock.tick(FPS)
        tiempo=int(TIEMPO - (time.time() - self.time))
        contador = font2.render("TIEMPO: " + str(tiempo),1,WHITE)
        self.screen.blit(contador,(20, 10))
        pygame.display.update()

    @staticmethod
    def quit():
        pygame.quit()

'''
En la función main establecemos el código de programación distribuida para jugar
desde cuatro ordenadores y ejecutamos la partida.
'''

def main(ip_address):
    #Imprimimos un texto con las normas del juego
    print("Vamos a jugar al fubolin, cada uno maneja un jugador y vais en equipo.La portería es el área grande del fondo.El que meta más goles antes de que se acabe el tiempo gana")
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            
            side,gameinfo = conn.recv()
            game=Game(gameinfo)
            print(f"Eres el {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)


