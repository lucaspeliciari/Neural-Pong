import pygame
from classes import *
from vars import *
import random

import neat
import os
import pickle
from datetime import timedelta, datetime


total_generations = 30
current_generation = 0
total_time_elapsed = 0 # rename to chronometer_in_game or something
chronometer_start = datetime.now()
all_time_most_fit = [0, 0]
all_time_least_fit = [1000, 0]

class Game():
    def __init__(self,
        genomes,
        config
        ):

        self.paddles = []
        self.nets = []
        self.ge = []
        self.to_remove = []
        self.position_removed = []

        global current_generation
        current_generation += 1

        global total_time_elapsed

        for _, g in genomes: # first element of genomes[0] is useless here so add _, before g
            g.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(g, config)
            self.nets.append(net)
            self.paddles.append(Paddle('Computer', screen_width - goal_width, (screen_height - boundary_upper) / 2))
            self.ge.append(g)

        pygame.init()
        pygame.display.set_caption('Neural Pong')
        # pygame.display.set_icon(icon)

        self.title_font = pygame.font.SysFont("monospace", 50)
        self.engine_font = pygame.font.SysFont("monospace", 15)
        self.game_font = pygame.font.SysFont("monospace", 35)

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.current_framerate = framerate
        self.current_timescale = timescale

        self.game_running = True  
        self.game_started = True
        self.timeElapsed = 0
        self.frame = 1 # 1st frame

        rand_x = random.choice([random.randrange(-900, -500), random.randrange(500, 900)])
        rand_y = random.choice([random.randrange(-900, -500), random.randrange(500, 900)])
        self.ball = Ball(
            self.paddles, 
            self.nets, 
            self.ge, 
            screen_width / 2, 
            screen_height / 2, 
            700, 
            700
            )

        self.main_loop()

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def draw_ball(self):
        if self.game_started:
            self.to_remove, self.position_removed = self.ball.update_position(self.current_timescale, self.clock.get_fps(), self.paddles)
        pygame.draw.circle(self.screen, white, (self.ball.x, self.ball.y), ball_radius) # scale is divide by 1000, arg is radius so divide by 2

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def draw_paddles(self): 
        for paddle in self.paddles:
            paddle.update_position()
            pygame.draw.rect(self.screen, paddle.color, (paddle.x, paddle.y, paddle_width, paddle_height))

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def draw_pitch(self):
        pygame.draw.line(self.screen, white, (goal_width, 0), (goal_width, screen_height))
        pygame.draw.line(self.screen, white, (screen_width - goal_width, 0), (screen_width - goal_width, screen_height))
        pygame.draw.line(self.screen, white, (0, boundary_upper), (screen_width, boundary_upper))
        pygame.draw.line(self.screen, white, (0, screen_height - boundary_lower), (screen_width, screen_height - boundary_lower))

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def draw_engine_labels(self):
        framerateLabel = self.engine_font.render(f'{round(self.clock.get_fps())} / {self.current_framerate}', 1, white)
        self.screen.blit(framerateLabel, (screen_width - 90, screen_height - 20))
        timescaleLabel = self.engine_font.render(str(round(self.current_timescale)), 1, white)
        self.screen.blit(timescaleLabel, (screen_width - 30, screen_height - 40))
        timeElapsedLabel = self.engine_font.render(f'{round(self.timeElapsed)} seconds', 1, white)
        self.screen.blit(timeElapsedLabel, (10, screen_height - 20))

        self.screen.blit(self.engine_font.render(f'Alive: {len(self.paddles)}', 1, white), (50, 100))
        self.screen.blit(self.engine_font.render(f'Gen: {current_generation} / {total_generations}', 1, white), (50, 120))

        fitness_list = [x.fitness for x in self.ge]
        current_most_fit = max(fitness_list)
        current_least_fit = min(fitness_list)
        self.screen.blit(self.engine_font.render(f'Current best: {current_most_fit:.2f}', 1, white), (50, 140))
        self.screen.blit(self.engine_font.render(f'Current worst: {current_least_fit:.2f}', 1, white), (50, 160))

        global all_time_most_fit, all_time_least_fit
        if current_most_fit > all_time_most_fit[0]:
            all_time_most_fit[0] = current_most_fit
            all_time_most_fit[1] = current_generation
        if current_least_fit < all_time_least_fit[0]:
            all_time_least_fit[0] = current_least_fit 
            all_time_least_fit[1] = current_generation

        self.screen.blit(self.engine_font.render(f'All-time best: {all_time_most_fit[0]:.2f} from gen {all_time_most_fit[1]}', 1, white), (50, 180))
        self.screen.blit(self.engine_font.render(f'All-time worst: {all_time_least_fit[0]:.2f} from gen {all_time_least_fit[1]}', 1, white), (50, 200))

        self.screen.blit(self.engine_font.render(f'{total_time_elapsed:.0f} seconds', 1, white), (50, 220))

        global chronometer_start
        real_world_time = datetime.now() - chronometer_start
        self.screen.blit(self.engine_font.render(f'Real world time: {real_world_time}', 1, white), (50, 240))

        # should calculate avg time per generation instead
        eta = real_world_time * total_generations / current_generation 
        self.screen.blit(self.engine_font.render(f'ETA: {eta - real_world_time}', 1, white), (50, 260))

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def event_handler(self):
        keys = pygame.key.get_pressed()

        key_value = 1
        if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
            key_value = 10

        if self.game_started: # no humans
            pass

        if keys[pygame.K_r]:
            self.reset_game()

        if keys[pygame.K_KP_PLUS]:
            self.current_timescale += key_value / 40
        elif keys[pygame.K_KP_MINUS]:
            self.current_timescale -= key_value / 40

        if keys[pygame.K_ESCAPE]:
            print('Quitting')
            pygame.quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Quitting')
                self.game_running = False
                

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def draw_labels(self):
        self.screen.blit(self.title_font.render('Neural Pong', 1, white), ((screen_width / 2) - 155, 10))            
    
#—————————————————————————————————————————————————————————————————————————————————————————————————


    def reset_game(self):
        self.ball.reset()

#—————————————————————————————————————————————————————————————————————————————————————————————————


    def main_loop(self):
        posX = 0
        posY = 0
        while self.game_running: 
            self.clock.tick(self.current_framerate)

            self.screen.fill(black) # try light blue         
            for i, paddle in enumerate(self.paddles):
                self.ge[i].fitness += 0.007

                output = self.nets[i].activate((
                    paddle.y, 
                    abs(paddle.y - self.ball.y),
                    abs((paddle.y + paddle_height) - self.ball.y)
                    ))

                if output[0] > 0.5: # give more fitness just for moving?
                    paddle.update_position(-self.current_timescale)
                elif output[1] < -0.5:
                    paddle.update_position(self.current_timescale)
                else:
                    self.ge[i].fitness -= 0.012 # moving is better than standing still
            
            self.draw_pitch()
            self.draw_paddles()
            self.draw_ball()

            if len(self.paddles) == 0:
                self.game_running = False
                break # redundant, but Tim told me to do this


            # self.check_goal()

            self.draw_labels()

            self.draw_engine_labels()

            # self.draw_buttons()
            
            self.event_handler()

            for i in reversed(self.to_remove):
                self.ge[i].fitness -= 3
                self.paddles.pop(i)
                self.nets.pop(i)
                self.ge.pop(i)
            self.to_remove.clear()

            
            self.frame +=1
            self.timeElapsed += abs(self.current_timescale / self.current_framerate)

            global total_time_elapsed
            total_time_elapsed += abs(self.current_timescale / self.current_framerate)

            pygame.display.flip()

        # pygame.quit()

#—————————————————————————————————————————————————————————————————————————————————————————————————
#—————————————————————————————————————————————————————————————————————————————————————————————————

def train_ai(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # winner is the best of all generations
    winner = p.run(Game, total_generations) # 2nd arg is the number of generations

    with open('winner_ai.pkl', 'wb') as file: # add prompt to ask if you want to save AI
        pickle.dump(winner, file)             # even when aborting with esc

    global total_time_elapsed
    formatted_total_time_elapsed = timedelta(seconds=total_time_elapsed)
    print(f'\n\nTraining took {formatted_total_time_elapsed} (in-game time)')

    global chronometer_start
    real_world_time = (datetime.now() - chronometer_start)
    print(f'\n\nTraining took {real_world_time} (real world+ time)')

def load_ai(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open('winner_ai.pkl', "rb") as file:
       genome = pickle.load(file)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    Game(genomes, config)

if __name__=="__main__":
    # game = Game()    

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neural_config.txt')

    # Train AI
    train_ai(config_path)

    # Load previously trained AI
    # load_ai(config_path)