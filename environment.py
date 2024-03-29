from logging import raiseExceptions
import sys
import pygame
import queue
import random
import time
from agent import Agent
from consts import BLACK,RED,BLUE
from functions import is_valid_value
from QL13 import puzzle13
from QL2 import puzzle2
import matplotlib.pyplot as plt
from puzzle2_SARSA import puzzle2_SARSA
from puzzle13_SARSA import puzzle13_SARSA
import numpy as np

class game:
    
    box_in_dock_a1 = False
    box_in_dock_a2 = False
    a1_finish = False
    a2_finish = False
    def is_valid_value(self,char):
        if ( char == ' 'or #floor
            char == '#' or #wall
            
            char == '@' or #agent1
            char == '=' or #agent2
            
            char == '+' or #agent1 on dock
            char == '-' or #agent2 on dock           
            char == '.' or #button
            
            char == '*' or #box on right place 
            char == '!' or #box on wrong place 

            char == '$' or #barrier
            char == '%' or #dividing wall
            
            char == '1' or #num1
            char == '2' or #num2
            char == '3' or #num3
            char == '4' or #num4
            char == '5' or #num5

            char == 'a' or #box on dock_num1
            char == 'b' or #box on dock_num2
            char == 'c' or #box on dock_num3
            char == 'd' or #box on dock_num4
            char == 'e' or #box on dock_num5
            char == 'p' or #box 2 on . dock
            char == 'o' or #box 3 on . dock
            char == 'l' or #agent1 on number docks
            char == 'm' or #agent2 on number docks
            char == 'z' #finish
            ):
            return True
        else:
            return False

    def __init__(self,filename,level):
        self.queue = queue.LifoQueue()
        self.matrix = []
        if int(level) < 1:
            print("ERROR: Level "+str(level)+" is out of range")
            sys.exit(1)
        else:
            file = open(filename,'r')
            level_found = False
            for line in file:
                row = []
                if not level_found:
                    if  "Level "+str(level) == line.strip():
                        level_found = True
                else:
                    if line.strip() != "":
                        row = []
                        for c in line:
                            if c != '\n' and self.is_valid_value(c):
                                row.append(c)
                            elif c == '\n':
                                continue
                            else:
                                print("ERROR: Level "+str(level)+" has invalid value "+c)
                                sys.exit(1)
                        self.matrix.append(row)
                    else:
                        break

    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32 + 40)

    def get_matrix(self):
        return self.matrix

    def print_matrix(self):
        for row in self.matrix:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == 'z':
                    return False
        return True



    def get_content(self,x,y):
        return self.matrix[y][x]


    def set_content(self,x,y,content):
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print("ERROR: Value '"+content+"' to be added is not valid")




    def agent_position(self, agent):
        
        x = 0
        y = 0
        if agent.id ==1:
            for row in self.matrix:
                for i in range(6):
                    if row[i] == '@' or row[i] == '+' or row[i] =='l':
                        return (x, y, row[i])
                    else:
                        x = x + 1
                y = y + 1
                x = 0

        elif agent.id ==2:
            
            for row in self.matrix:
                for i in range(6):
                    if row[i+5] == '=' or row[i+5] == '-' or row[i+5] == 'm':
                        return (x, y, row[i+5])
                    else:
                        x = x + 1
                y = y + 1
                x = 5

        else:
            raiseExceptions
            print("Invalid Id")


    def can_move(self,x,y, agent):
        return self.get_content(agent[0]+x,agent[1]+y) not in ['%','#','*', '$','1','2','3','4','5', '!','o','p']

    def next(self,x,y, agent ):
        return self.get_content(agent[0]+x,agent[1]+y)
    """
    def open_obstacle_agent(self,x,y, agent):
        return (self.next(x,y,agent) in ['.'])
    """
    def can_push(self,x,y,agent):
        #agent can only push boxes up or down
        if x != 0:
            return False
        elif (y<0 and agent[1] <=10) or (y>0 and agent[1]>=13) :
            return False
        else:
            options = ['1','2','3','4','5','!','o','p']#boxes and boxes in dock
            boxes_in_dock = ['a','b','c','d','e', ' ','.'] #boxes and floor 
            return (self.next(x,y,agent) in options and self.next(x+x,y+y,agent) in boxes_in_dock)

    
    def move_box(self,x,y,a,b):
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        boxes = ['1','2','3','4','5']
        boxes_in_dock = ['a','b','c','d','e']
        if current_box == '!':
            if(x == 1 ):
                self.set_content(x+a,y+b,'1')
                self.set_content(x,y,'a')
            elif(x == 3 ):
                self.set_content(x+a,y+b,'3')
                self.set_content(x,y,'c')
            elif(x == 4 ):
                self.set_content(x+a,y+b,'4')
                self.set_content(x,y,'d')
            elif(x == 6 ):
                self.set_content(x+a,y+b,'5')
                self.set_content(x,y,'b')
            else:
                self.set_content(x+a,y+b,'2')
                self.set_content(x,y,'e')


        elif current_box in boxes and future_box == ' ':
            self.set_content(x+a,y+b,current_box)
            self.set_content(x,y,' ')

        elif current_box in boxes and future_box in boxes_in_dock:
            self.set_content(x+a,y+b,'*') 
            self.set_content(x,y,' ')
            

        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,current_box)
            self.set_content(x,y,boxes_in_dock)

        elif current_box == '*' and future_box in boxes_in_dock:
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,boxes_in_dock)
        elif current_box in boxes and future_box == '.':
            if(current_box == '2'):
                self.set_content(x+a,y+b,'p')  
                self.set_content(x,y,' ')
            else:
                self.set_content(x+a,y+b,'o') 
                self.set_content(x,y,' ')
        elif current_box in ['p','o'] and future_box == ' ':
            if(current_box == 'p'):
                self.set_content(x+a,y+b,'2') 
                self.set_content(x,y,'.')
            else:
                self.set_content(x+a,y+b,'3') 
                self.set_content(x,y,'.')

                
    def reset(self):
        
        self.a1_finish = False
        self.a2_finish = False
        self.box_in_dock_a1 = False
        self.box_in_dock_a2 = False
        self.last_box = ''
        self.puzzle2= False
        self.a1_dock = False
        self.a2_dock = False


        self.__init__('levels',1)
        pygame.time.delay(2 * 1000)



   
    def move(self,x,y,save, agent):
        docks = ['a','b','c','d','e']
        agent_position = self.agent_position(agent)
  
        if self.can_move(x,y, agent_position):
            current = agent_position
            future = self.next(x,y,agent_position)
            boxes = ['1','2','3','4','5']
            boxes_in_dock = ['a','b','c','d','e'] 

            if (current[2] == '@' or current[2] == '=') and future == ' ':
                self.set_content(current[0]+x,current[1]+y,current[2])
                self.set_content(current[0],current[1],' ')
            
            elif (current[2] == '@' or current[2] == '=') and future in '.':
    
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'+')
                    for i in range(0,5):
                        if(self.get_content(i,15) == '$'): # this has to be changes if wall is moved!!
                            self.set_content(i,15,' ')

                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'-')
                    for i in range(6,11):
                        if(self.get_content(i,15) == '$'): # this has to be changes if wall is moved!!
                            self.set_content(i,15,' ')

                self.set_content(current[0],current[1],' ')
            
            
            elif (current[2] == '+' or current[2] == '-') and future == ' ':
                if agent.id == 1:
                    self.a1_dock = False
                    self.set_content(current[0]+x,current[1]+y,'@')
                elif agent.id == 2:
                    self.a2_dock = False
                    self.set_content(current[0]+x,current[1]+y,'=')

                self.set_content(current[0],current[1],'.')
            #agent stepping on colored dock
            elif (current[2] == '@' or current[2] == '=') and future in docks:
    
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'l')
                elif agent.id == 2:
                   self.set_content(current[0]+x,current[1]+y,'m')
                self.set_content(current[0],current[1],' ')

            #agent on colored docks
            elif (current[2] == 'l' or current[2] == 'm') and future == ' ':
                if agent.id == 1:
                  
                    self.set_content(current[0]+x,current[1]+y,'@')
                elif agent.id == 2:
              
                    self.set_content(current[0]+x,current[1]+y,'=')

                if(current[0] == 1 ):
                    self.set_content(current[0],current[1],'a')
                elif(current[0] == 3 ):
                    self.set_content(current[0],current[1],'c')
                elif(current[0] == 4 ):
                    self.set_content(current[0],current[1],'d')
                elif(current[0] == 6 ):
                    self.set_content(current[0],current[1],'b')
                else:
                    self.set_content(current[0],current[1],'e')
            #agent step on colored dock to other colored dock
            elif (current[2] == 'l' or current[2] == 'm') and future in docks:
                if agent.id == 1:
                  
                    self.set_content(current[0]+x,current[1]+y,'l')
                elif agent.id == 2:
              
                    self.set_content(current[0]+x,current[1]+y,'m')

                if(current[0] == 1 ):
                    self.set_content(current[0],current[1],'a')
                elif(current[0] == 3 ):
                    self.set_content(current[0],current[1],'c')
                elif(current[0] == 4 ):
                    self.set_content(current[0],current[1],'d')
                elif(current[0] == 6 ):
                    self.set_content(current[0],current[1],'b')
                else:
                    self.set_content(current[0],current[1],'e')

        

            elif (current[2] == '+' or current[2] == '-') and future == boxes_in_dock:
                self.set_content(current[0]+x,current[1]+y,current[2])
                self.set_content(current[0],current[1],boxes_in_dock)

            
            #finish line
            elif (current[2] == '@' or current[2] == '=')  and future == 'z':
                if agent.id == 1:
                    self.a1_finish = True
                elif agent.id == 2:
                    self.a2_finish = True
                self.set_content(current[0]+x,current[1]+y,current[2])
                self.set_content(current[0],current[1],' ')
        


        elif self.can_push(x,y,agent_position):
        
            current = agent_position
            future = self.next(x,y,agent_position)
            future_box = self.next(x+x,y+y,agent_position)
            boxes = ['1','2','3','4','5']
            boxes_in_dock = ['a','b','c','d','e']
    

            if (current[2] == '@'  or current[2] == '=') and future in boxes and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,current[2])
                        
                    
    
            elif (current[2] == '@' or current[2] == '=') and future in boxes and future_box in boxes_in_dock:

                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,current[2])
                if(agent.id == 1):
                    if(self.box_in_dock_a1):
                        #opens wall
                         for i in range(0,5):
                            if(self.get_content(i,8) == '$'): # this has to be changes if wall is moved!!
                                self.set_content(i,8,' ')
                    else:
                        self.box_in_dock_a1 =True
                elif(agent.id == 2):
                    if(self.box_in_dock_a2):
                        #opens wall
                        for i in range(6,11):
                            if(self.get_content(i,8) == '$'): # this has to be changes if wall is moved!!
                                self.set_content(i,8,' ')

                    else:
                        self.box_in_dock_a2 =True

            elif (current[2] == '@' or current[2] == '=') and future == '*' and future_box == ' ':

                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'+')
                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'-')

            elif (current[2] == '@' or current[2] == '=') and future == '*' and future_box in boxes_in_dock:
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'+')
                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'-')

            if (current[2] == '+' or current[2] == '-') and future in boxes and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'@')
                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'=')
       

            elif (current[2] == '+' or current[2] == '-') and future in boxes and future_box in boxes_in_dock:
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],boxes_in_dock[boxes.index(future)])
                self.set_content(current[0]+x,current[1]+y,current[2])


            elif (current[2] == '+' or current[2] == '-') and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],boxes_in_dock)
                self.set_content(current[0]+x,current[1]+y,current[2])
 
            elif (current[2] == '+' or current[2] == '-') and future == '*' and future_box in boxes_in_dock:
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],boxes_in_dock)
                self.set_content(current[0]+x,current[1]+y,current[2])

            elif (current[2] == '@' or current[2] == '=') and future == '!' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'l')
                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'m')

            elif (current[2] == 'l' or current[2] == 'm') and future in boxes and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                if(current[0] == 1 ):
                    self.set_content(current[0],current[1],'a')
                elif(current[0] == 3 ):
                    self.set_content(current[0],current[1],'c')
                elif(current[0] == 4 ):
                    self.set_content(current[0],current[1],'d')
                elif(current[0] == 6 ):
                    self.set_content(current[0],current[1],'b')
                else:
                    self.set_content(current[0],current[1],'e')
            
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'@')
                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'=')
        
            elif (current[2] == '@' or current[2] == '=') and future in boxes and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,current[2])
            elif (current[2] == '@' or current[2] == '=') and future in ['o','p'] and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                if agent.id == 1:
                    self.set_content(current[0]+x,current[1]+y,'+')
                elif agent.id == 2:
                    self.set_content(current[0]+x,current[1]+y,'-')
        agent_position = None    

def print_game(matrix,screen):

    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == '%': #dividing_wall
                screen.blit(dividing_wall,(x,y)) 
            elif char == '#': #wall
                screen.blit(wall,(x,y))

            elif char == '=': #agent2
                screen.blit(agent1,(x,y)) 
            elif char == '@': #agent1 
                screen.blit(agent,(x,y))
            elif char == 'l':
                screen.blit(agent,(x,y)) #agent1 on numbered dock
            elif char == 'm':
                screen.blit(agent1,(x,y)) #agent2 on numbered dock
            if char == ' ': #floor
                screen.blit(floor,(x,y))
 

            elif char == '.': #button
                screen.blit(docker,(x,y))

            elif char == '*': #box on right place
                screen.blit(box_right_place,(x,y))
            elif char == '!': #box on wrong place
                screen.blit(box_wrong_place,(x,y))

            elif char == '$': #barrier
                screen.blit(box,(x,y))

            elif char == '+': #agent1 on dock
                screen.blit(agent_docked,(x,y))
            elif char == '-': #agent2 on dock
                screen.blit(agent1_docked,(x,y))

            elif char == '1': #num1
                screen.blit(box_wrong_place,(x,y))
            elif char == '2': #num2
                screen.blit(box_wrong_place,(x,y))
            elif char == '3': #num3
                screen.blit(box_wrong_place,(x,y))
            elif char == '4': #num4
                screen.blit(box_wrong_place,(x,y))
            elif char == '5': #num5
                screen.blit(box_wrong_place,(x,y))

            elif char == 'a': #dock_num1
                screen.blit(dock_num1,(x,y))
            elif char == 'b': #dock_num2
                screen.blit(dock_num2,(x,y))
            elif char == 'c': #dock_num3
                screen.blit(dock_num3,(x,y))
            elif char == 'd': #dock_num4
                screen.blit(dock_num4,(x,y))
            elif char == 'e': #dock_num5
                screen.blit(dock_num5,(x,y))


            elif char == 'p': #box2 on dock .
                screen.blit(num2,(x,y))
            elif char == 'o':  #box3 on dock .
                screen.blit(num3,(x,y))

            elif char == 'z': #dock_num5
                screen.blit(finish,(x,y))

            x = x + 32
        x = 0
        y = y + 32


def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
      return event.key
    else:
      pass



def display_end(screen):
    message = "Level Completed"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 50,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,34), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 60, (screen.get_height() / 2) - 90))
    pygame.display.flip()

def display_box(screen, message):
  "Print a message in a box in the middle of the screen"
  fontobject = pygame.font.Font(None,30)

  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 470, (screen.get_height() / 2 -10) ))
  pygame.display.flip()


def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + "     " + "".join(current_string)
)
  while 1:
    inkey = get_key()
    if inkey == pygame.K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == pygame.K_RETURN:
      break
    elif inkey == pygame.K_MINUS:
      current_string.append("_")
    elif inkey <= 127:
      current_string.append(chr(inkey))
    display_box(screen, question + " >>  " + "".join(current_string)
)
  return "".join(current_string)


def agentType():
    start = pygame.display.set_mode((1000,240))


    agent_type = ask(start,"OPTION:  1) Random Vs Q-Learning    2) SARSA Vs Q-Learning    3) Random Vs SARSA ")
    if int(agent_type) > 0 and int(agent_type)<=3:
        return agent_type 
    else:
        print("ERROR: Invalid Level or game option: "+str(agent_type))
        sys.exit(2)
  
dividing_wall = pygame.image.load('images/wall1.png')
agent1 = pygame.image.load('images/agent1.png')
wall = pygame.image.load('images/wall.png')
floor = pygame.image.load('images/floor.png')
box = pygame.image.load('images/bomx.png')
box_right_place = pygame.image.load('images/box_docked.png')
box_wrong_place = pygame.image.load('images/box_docked_wrong.png')
agent = pygame.image.load('images/agent.png')
agent_docked = pygame.image.load('images/agent_dock.png')
agent1_docked = pygame.image.load('images/agent_dock1.png')
docker = pygame.image.load('images/dock.png')
num1 = pygame.image.load('images/n1.png')
num2 = pygame.image.load('images/n2.png')
num3 = pygame.image.load('images/n3.png')
num4 = pygame.image.load('images/n4.png')
num5 = pygame.image.load('images/n5.png')
dock_num1 = pygame.image.load('images/dock_n1.png')
dock_num2 = pygame.image.load('images/dock_n1.png')
dock_num3 = pygame.image.load('images/dock_n1.png')
dock_num4 = pygame.image.load('images/dock_n1.png')
dock_num5 = pygame.image.load('images/dock_n1.png')
finish = pygame.image.load('images/finish.png')


background = 255, 226, 191
pygame.init()


agent_type= agentType()
game = game('levels',1)
size = game.load_size()
screen = pygame.display.set_mode(size)



clock = pygame.time.Clock()
all_sprites_list = pygame.sprite.Group()
a1 = Agent(1)		
a2 = Agent(2)
p1 = True
p2 = False
p3 = False
puzzle1 = puzzle13("./puzzle_splitted1.txt", (3, 1))
puzzle_2= puzzle2("./puzzle_splited2.txt")
puzzle_3 = puzzle13("./puzzle_splitted3.txt", (3, 1))

p1_SARSA = True
p2_SARSA = False
p3_SARSA = False

#puzzle1_DQN =  DQNAgent13("./puzzle_splitted1.txt",(3, 1), gamma=0.99, epsilon=0.5, batch_size=64, n_actions=4,input_dims=[2], lr=0.001)
#puzzle2_DQN=  DQNAgent2("./puzzle_splited2.txt", gamma=0.99, epsilon=0.5, batch_size=64, n_actions=4, input_dims=[6], lr=0.9)
#puzzle3_DQN = DQNAgent13("./puzzle_splitted3.txt",(3, 1), gamma=0.99, epsilon=5, batch_size=64, n_actions=4, input_dims=[2], lr=0.001)

puzzle_1_SARSA = puzzle13_SARSA("./puzzle_splitted1.txt", (3, 1))
puzzle_2_SARSA= puzzle2_SARSA("./puzzle_splited2.txt")
puzzle_3_SARSA = puzzle13_SARSA("./puzzle_splitted3.txt", (3, 1))


"""
def user_actions(pygame, game, agent):
    if event.key == pygame.K_UP: 
        game.move(0,-1, True, agent)
    elif event.key == pygame.K_DOWN : 
        game.move(0,1, True, agent)
    elif event.key == pygame.K_LEFT : 
        game.move(-1,0, True, agent)
    elif event.key == pygame.K_RIGHT:
        game.move(1,0, True,  agent)
"""

def random_actions(pygame, game, agent, action):
    if action == 'UP':
        game.move(0,-1, True, agent)
    elif action == 'DOWN': 
        game.move(0,1, True, agent)
    elif action == 'LEFT': 
        game.move(-1,0, True, agent)
    elif action == 'RIGHT':
        game.move(1,0, True,  agent)



steps_A1 = 0
steps_A2 = 0
stepsA1 = []
stepsA2 = []

steps_A1_p1 = 0
stepsA1p1 = []

steps_A1_p2 = 0
stepsA1p2 = []

steps_A1_p3 = 0
stepsA1p3 = []

steps_A2_p1 = 0
stepsA2p1 = []

steps_A2_p2 = 0
stepsA2p2 = []

steps_A2_p3 = 0
stepsA2p3 = []

box_in_dock_1 = False
box_in_dock_2 = False

box_in_dock_1_A2 = False
box_in_dock_2_A2 = False

win_A1 = False
win_A2 = False

a1_done = False
a2_done = False

costsa1 = []

costsa2 = []

cost_p1_a1 = 0
cost_p2_a1 = 0
cost_p3_a1 = 0

cost_p1_a2 = 0
cost_p2_a2 = 0
cost_p3_a2 = 0

costs_p1_a1 = []
costs_p2_a1 = []
costs_p3_a1 = []

costs_p1_a2 = []
costs_p2_a2 = []
costs_p3_a2 = []

fig1 = plt.figure() 
def make_plot(name1 , name2, step1, step2):
    plt.plot(step1, c = 'b')
    plt.plot(step2,  c = 'r')
    plt.legend([name1, name2])
    plt.title("Steps Per Episode")
    plt.ylabel("Steps")
    plt.xlabel("Episode")
    plt.show(block=False)
    plt.pause(.1)


costa1 = 0

costa2 = 0

#How many episodes will be played
number_of_rounds = 100
i = 0
while i < number_of_rounds:
    print("round")
    print(i+1)
    if game.is_completed():
        game.reset()
        
    clock = pygame.time.Clock()


    print_game(game.get_matrix(),screen)
    
    #RANDOM vs Q-Learning -----------------------------------------------------------------------------------------
    if int(agent_type) ==1:

        #AGENTE 1 - RANDOM
        if not a1_done:
            action = random.choice(a1.actions())	
            random_actions(pygame, game, a1,action)
            steps_A1 +=1
            if game.a1_finish:
                a1_done = True

        
        #Agent2 -> Q-Learning
        if not a2_done:
           
            steps_A2 +=1
          
            if p1:
                steps_A2_p1 +=1
                action,win, cost_p1_a2 =  puzzle1.run_one(cost_p1_a2)
                #print("COST", cost)
                if action == 'UP': 
                    game.move(0,-1, True, a2)
                    # steps_A2_p1 +=1
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
                    # steps_A2_p1 +=1
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)
                    #steps_A2_p1 +=1
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)
                    #steps_A2_p1 +=1
                if win:
                    costs_p1_a2.append(cost_p1_a2)
                    stepsA2p1.append(steps_A2_p1)
                    steps_A2_p1 = 0
                    puzzle1.change_init_position( (3, 1))
                    p1 = False
                    p2 = True
            
            if p2:
                steps_A2_p2 +=1
                action, win, cost_p2_a2, pos = puzzle_2.run_one(cost_p2_a2)

                if action == 'UP': 
                    game.move(0,-1, True, a2)
 
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)

                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)

                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)
            
                if win:
    
                    costs_p2_a2.append(cost_p2_a2)
                    stepsA2p2.append(steps_A2_p2)
                    steps_A2_p2 = 0
                    p2 = False
                    p3 = True
                    puzzle_3.change_init_position((12,pos[1]))
                    puzzle_2.reset()


            if p3:
                steps_A2_p3 +=1
                time1=time.time()
                action, win, cost_p3_a2= puzzle_3.run_one(cost_p3_a2)
                if action == 'UP': 
                    game.move(0,-1, True, a2)

                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
 
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)
      
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)
           
                if win:
                    costs_p3_a2.append(cost_p3_a2)
                    costsa2.append(cost_p1_a2+cost_p2_a2+cost_p3_a2)
                    cost_p1_a2=0
                    cost_p2_a2=0
                    cost_p3_a2=0
                    
                    costa2 = 0
                    stepsA2p3.append(steps_A2_p3)
                    steps_A2_p3 = 0
                    a2_done = True
                    p1 = True
                    p2 = False
                    p3 = False
                    steps_A2_p1= 0
                    steps_A2_p2= 0
                    steps_A2_p3 = 0

        if a1_done and a2_done:
            i+=1
            stepsA1.append(steps_A1)
            stepsA2.append(steps_A2)
            make_plot("Agent1: Random" , "Agent2: Q-Learning",  stepsA1,stepsA2)
            steps_A2 = 0
            steps_A1 = 0
            a1_done = False
            a2_done = False
            game.reset()


    
    #SARSAvs Q-Learning -----------------------------------------------------------------------------------------------------
    elif int(agent_type) ==2: 
        #Agent1 -> User input
        if not a1_done:
            #Agent1 -> SARSA
            steps_A1 += 1
            if p1_SARSA:
                
                action,win, cost_p1_a1=  puzzle_1_SARSA.run_one(cost_p1_a1)
    
                steps_A1_p1 +=1

                if action == 'UP': 
                    game.move(0,-1, True, a1)
        
                elif action == 'DOWN': 
                    game.move(0,1, True, a1)
          
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a1)
             
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a1)
               
                if win:
                
                    costs_p1_a1.append(cost_p1_a1)
                    stepsA1p1.append(steps_A1_p1)
                    steps_A1_p1 = 0
                    puzzle_1_SARSA.change_init_position( (np.float32(3), np.float32(1)))
                    p1_SARSA = False
                    p2_SARSA = True
            
            if p2_SARSA:
                steps_A1_p2 +=1
                action, win, cost_p2_a1, pos = puzzle_2_SARSA.run_one(cost_p2_a1)
             
                if action == 'UP': 
                    game.move(0,-1, True, a1)
             
                elif action == 'DOWN': 
                    game.move(0,1, True, a1)
              
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a1)
                
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a1)
                
                if win:
                    costs_p2_a1.append(cost_p2_a1)
                    stepsA1p2.append(steps_A1_p2)
                    steps_A1_p2 = 0
                    p2_SARSA = False
                    p3_SARSA = True
                    puzzle_3_SARSA.change_init_position((12,pos[1]))
                    puzzle_2_SARSA.reset()


            if p3_SARSA:
                steps_A1_p3 +=1
                time1=time.time()
                action, win, cost_p3_a1=  puzzle_3_SARSA.run_one(cost_p3_a1)
                if action == 'UP': 
                    game.move(0,-1, True, a1)
                 
                elif action == 'DOWN': 
                    game.move(0,1, True, a1)
  
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a1)
          
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a1)
              
                if win:
                    costs_p3_a1.append(cost_p3_a1)
                    costsa1.append(cost_p1_a1+cost_p2_a1+cost_p3_a1)
                    cost_p1_a1=0
                    cost_p2_a1=0
                    cost_p3_a1=0
                    costa1 = 0
                    stepsA1p3.append(steps_A1_p3)
                    steps_A1_p3 = 0
                    a1_done = True
                    p1_SARSA = True
                    p2_SARSA = False
                    p3_SARSA = False
                   

            

        if not a2_done:
            #Agent2 -> Q-Learning
            steps_A2 +=1
          
            if p1:
                steps_A2_p1 +=1
                action,win, cost_p1_a2 =  puzzle1.run_one(cost_p1_a2)
                if action == 'UP': 
                    game.move(0,-1, True, a2)
      
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
 
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)

                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)

                if win:
                    costs_p1_a2.append(cost_p1_a2)
                    stepsA2p1.append(steps_A2_p1)
                    steps_A2_p1 = 0
                    puzzle1.change_init_position( (3, 1))
                    p1 = False
                    p2 = True
            
            if p2:
                steps_A2_p2 +=1
                action, win, cost_p2_a2, pos = puzzle_2.run_one(cost_p2_a2)
  
                if action == 'UP': 
                    game.move(0,-1, True, a2)
          
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
                
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)
      
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)
              
                if win:
    
                    costs_p2_a2.append(cost_p2_a2)
                    stepsA2p2.append(steps_A2_p2)
                    steps_A2_p2 = 0
                    p2 = False
                    p3 = True
                    puzzle_3.change_init_position((12,pos[1]))
                    puzzle_2.reset()


            if p3:
                steps_A2_p3 +=1
                time1=time.time()
                action, win, cost_p3_a2= puzzle_3.run_one(cost_p3_a2)
                if action == 'UP': 
                    game.move(0,-1, True, a2)
        
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
                  
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)
                
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)
                   
                if win:
                    costs_p3_a2.append(cost_p3_a2)
                    costsa2.append(cost_p1_a2+cost_p2_a2+cost_p3_a2)
                    cost_p1_a2=0
                    cost_p2_a2=0
                    cost_p3_a2=0
                    costa2 = 0
                    stepsA2p3.append(steps_A2_p3)
                    steps_A2_p3 = 0
                    a2_done = True
                    p1 = True
                    p2 = False
                    p3 = False
                    steps_A2_p1= 0
                    steps_A2_p2= 0
                    steps_A2_p3 = 0
            
        if a1_done and a2_done:
            i+=1
            stepsA1.append(steps_A1)
            stepsA2.append(steps_A2)
            make_plot("Agent1: SARSA" , "Agent2: Q-Learning",  stepsA1,stepsA2)
            steps_A2 = 0
            steps_A1 = 0
            a1_done = False
            a2_done = False
            game.reset()
    





    #RANDOM vs SARSA -----------------------------------------------------------------------------------------------------
    elif int(agent_type) ==3:

        if not a1_done:  
            #Agent1 -> RANDOM
            action = random.choice(a1.actions())	
            random_actions(pygame, game, a1,action)
            steps_A1 +=1
            if game.a1_finish:
                a1_done = True
        
         #Agent2 -> SARSA
        if not a2_done:
            steps_A2 += 1
            if p1_SARSA:
                
                action,win, cost_p1_a2=  puzzle_1_SARSA.run_one(cost_p1_a2)
    
                steps_A2_p1 +=1
          
                if action == 'UP': 
                    game.move(0,-1, True, a2)
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)
    
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)

                if win:
                
                    costs_p1_a2.append(cost_p1_a2)
                    stepsA2p1.append(steps_A2_p1)
                    steps_A2_p1 = 0
                    puzzle_1_SARSA.change_init_position( (3,1))
                    p1_SARSA = False
                    p2_SARSA = True
            
            if p2_SARSA:
                steps_A2_p2 +=1
                action, win, cost_p2_a2, pos = puzzle_2_SARSA.run_one(cost_p2_a2)

                if action == 'UP': 
                    game.move(0,-1, True, a2)

                elif action == 'DOWN': 
                    game.move(0,1, True, a2)

                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)

                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)

                if win:
                    costs_p2_a2.append(cost_p2_a2)
                    stepsA1p2.append(steps_A1_p2)
                    steps_A2_p2 = 0
                    p2_SARSA = False
                    p3_SARSA = True
                    puzzle_3_SARSA.change_init_position((12,pos[1]))
                    puzzle_2_SARSA.reset()


            if p3_SARSA:
                steps_A2_p3 +=1
                time1=time.time()
                action, win, cost_p3_a2=  puzzle_3_SARSA.run_one(cost_p3_a2)
                if action == 'UP': 
                    game.move(0,-1, True, a2)
              
                elif action == 'DOWN': 
                    game.move(0,1, True, a2)
                    
                elif action == 'LEFT': 
                    game.move(-1,0, True,  a2)
                
                elif action == 'RIGHT': 
                    game.move(1,0, True,  a2)
            
                if win:
                    costs_p3_a2.append(cost_p3_a1)
                    costsa2.append(cost_p1_a1+cost_p2_a1+cost_p3_a1)
                    cost_p1_a2=0
                    cost_p2_a2=0
                    cost_p3_a1=0
                    costa1 = 0
                    stepsA2p3.append(steps_A2_p3)
                    steps_A1_p3 = 0
                    a2_done = True
                    p1_SARSA = True
                    p2_SARSA = False
                    p3_SARSA = False
                   
            
        if a1_done and a2_done:
            i+=1
            stepsA1.append(steps_A1)
            stepsA2.append(steps_A2)
            make_plot("Agent1: Random" , "Agent2: SARSA",  stepsA1,stepsA2)
            steps_A2 = 0
            steps_A1 = 0
            a1_done = False
            a2_done = False
            game.reset()

        
   

    #STATISTICS------------------------------------------------------------------------------------------------------------------------
    def time_convert(time): #miliseconds
        return int(time*1000)
 
    if int(agent_type) ==1:
        font = pygame.font.Font(None, 23)
        text = font.render(str("Agent1: Random"), 1, BLUE)
        screen.blit(text, (5,644)) 
        text = font.render(str("Agent2: Q-Learning"), 1, RED)
        screen.blit(text, (195,644)) 

    if int(agent_type) ==2:
        font = pygame.font.Font(None, 23)
        text = font.render(str("Agent1: SARSA"), 1, BLUE)
        screen.blit(text, (5,644)) 
        text = font.render(str("Agent2: Q-Learning"), 1, RED)
        screen.blit(text, (195,644)) 

    if int(agent_type) ==3:
        font = pygame.font.Font(None, 23)
        text = font.render(str("Agent1: Random"), 1, BLUE)
        screen.blit(text, (5,644)) 
        text = font.render(str("Agent2: SARSA"), 1, RED)
        screen.blit(text, (195,644)) 
        

    pygame.display.update()

#plots for agent type 1 results
'''
fig1 = plt.figure(figsize =(10, 8)) 
plt.plot(stepsA1, c = 'b')
plt.plot(stepsA2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (Random)", "Agent 2 (Q-Learning)"])
plt.title("Steps Per Episode")
plt.ylabel("Steps")
plt.xlabel("Episode")
plt.show()
'''

#plots for agent type 2 results
'''
fig1 = plt.figure(figsize =(10, 8)) 
plt.plot(stepsA1, c = 'b')
plt.plot(stepsA2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Steps Per Episode")
plt.ylabel("Steps")
plt.xlabel("Episode")
fig2 = plt.figure(figsize =(10, 8)) 
plt.plot(stepsA1p1, c = 'b')
plt.plot(stepsA2p1,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Steps Per Episode Puzzle1")
plt.ylabel("Steps")
plt.xlabel("Episode")
fig3 = plt.figure(figsize =(10, 8)) 
plt.plot(stepsA1p2, c = 'b')
plt.plot(stepsA2p2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Steps Per Episode Puzzle2")
plt.ylabel("Steps")
plt.xlabel("Episode")
fig4 = plt.figure(figsize =(10, 8)) 
plt.plot(stepsA1p3, c = 'b')
plt.plot(stepsA2p3,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Steps Per Episode Puzzle3")
plt.ylabel("Steps")
plt.xlabel("Episode")
fig5 = plt.figure(figsize =(10, 8)) 
plt.plot(costsa1, c = 'b')
plt.plot(costsa2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Reward Per Episode")
plt.ylabel("Reward")
plt.xlabel("Episode")
fig6 = plt.figure(figsize =(10, 8)) 
plt.plot(costs_p1_a1, c = 'b')
plt.plot(costs_p1_a2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Reward Per Episode Puzzle1")
plt.ylabel("Reward")
plt.xlabel("Episode")
fig7 = plt.figure(figsize =(10, 8)) 
plt.plot(costs_p2_a1, c = 'b')
plt.plot(costs_p2_a2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Reward Per Episode Puzzle2")
plt.ylabel("Reward")
plt.xlabel("Episode")
fig8 = plt.figure(figsize =(10, 8)) 
plt.plot(costs_p3_a1, c = 'b')
plt.plot(costs_p3_a2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (SARSA)", "Agent 2 (Q-Learning)"])
plt.title("Reward Per Episode Puzzle3")
plt.ylabel("Reward")
plt.xlabel("Episode")
plt.show()
'''
#plots for agent type 2 results
'''
fig1 = plt.figure(figsize =(10, 8)) 
plt.plot(stepsA1, c = 'b')
plt.plot(stepsA2,  c = 'r')
plt.xlim([1, number_of_rounds])
plt.legend(["Agent 1 (Random)", "Agent 2 (SARSA)"])
plt.title("Steps Per Episode")
plt.ylabel("Steps")
plt.xlabel("Episode")
plt.show()
'''











    





