import pygame
import sys
import random
from datetime import datetime


class SpaceShip(pygame.sprite.Sprite):
	def __init__(self, path, x_pos, y_pos):
		super().__init__()
		self.uncharged = pygame.image.load(path)
		self.charged = pygame.image.load("Assets/spaceship_charged.png")
		self.infinite = pygame.image.load("Assets/infinite_spaceship.png")

		self.image = self.uncharged
		self.rect = self.image.get_rect(center=(x_pos, y_pos))
		self.shield_surface = pygame.image.load("Assets/shield.png")
		self.health = 5

	def update(self):
		self.rect.center = pygame.mouse.get_pos()
		self.screen_constrain()
		self.display_health()

	def screen_constrain(self):
		if self.rect.right >= 1280:
			self.rect.right = 1280
		if self.rect.left <= 0:
			self.rect.left = 0

	def display_health(self):
		for index, shield in enumerate(range(self.health)):
			screen.blit(self.shield_surface, (10 + index * 40, 10))

	def get_damage(self, damage_amount):
		self.health -= damage_amount

	def charge(self):
		self.image = self.charged

	def discharge(self):
		self.image = self.uncharged

	def make_infinite(self):
		self.image = self.infinite


class Meteor(pygame.sprite.Sprite):
	def __init__(self, path, x_pos, y_pos, x_speed, y_speed):
		super().__init__()
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center=(x_pos, y_pos))
		self.x_speed = x_speed
		self.y_speed = y_speed
		self.x_pos = x_pos
		self.y_pos = y_pos

	def update(self):
		self.rect.centerx += self.x_speed
		self.rect.centery += self.y_speed

		if self.rect.centery >= 800:
			self.kill()


class Laser(pygame.sprite.Sprite):
	def __init__(self, path, pos, speed):
		super().__init__()
		self.pos = pos
		self.image = pygame.image.load(path)
		self.rect = self.image.get_rect(center=pos)
		self.speed = speed

	def update(self):
		self.rect.centery -= self.speed
		if self.rect.centery <= -100:
			self.kill()


def main_game():
	global laser_active, laser_cooldown, can_shoot_infinitely, infiniteshooting_timer
	laser_group.draw(screen)
	spaceship_group.draw(screen)
	meteor_group.draw(screen)
	bonushealth_group.draw(screen)
	infiniteshooting_group.draw(screen)

	laser_group.update()
	spaceship_group.update()
	meteor_group.update()
	bonushealth_group.update()
	infiniteshooting_group.update()

	# Collision
	if pygame.sprite.spritecollide(spaceship_group.sprite, meteor_group, True):
		spaceship_group.sprite.get_damage(1)
		
	if pygame.sprite.spritecollide(spaceship_group.sprite, bonushealth_group, True):
		spaceship_group.sprite.health += 3
		bonushealthsfx.play()

	for laser in laser_group:
		pygame.sprite.spritecollide(laser, meteor_group, True)
		if pygame.sprite.spritecollide(laser, bonushealth_group, True):
			spaceship_group.sprite.health += 3
			bonushealthsfx.play()
		if pygame.sprite.spritecollide(laser, infiniteshooting_group, True):
			infiniteshooting_timer = pygame.time.get_ticks()

	# Laser timer
	if pygame.time.get_ticks() - laser_timer >= laser_cooldown:
		laser_active = True
		spaceship_group.sprite.charge()

	if pygame.time.get_ticks() - infiniteshooting_timer <= 10000 and infiniteshooting_timer > 0:
		laser_cooldown = 0
		spaceship_group.sprite.make_infinite()
	else:
		laser_cooldown = 1000
		spaceship_group.sprite.discharge()
	return 1


def end_game():
	game_over_surface = game_font.render("Game Over!", True, (255, 255, 255))
	game_over_rect = game_over_surface.get_rect(center=(640, 200))
	screen.blit(game_over_surface, game_over_rect)

	score_surface = game_font.render(f"Score: {score}", True, (255, 255, 255))
	if score not in scores:
		scores.append(score)
	score_rect = game_over_surface.get_rect(center=(640, 240))
	screen.blit(score_surface, score_rect)

	button_surface = pygame.image.load("Assets/highscores_button.png")
	button_surface = pygame.transform.scale(button_surface, (320, 180))
	button_rect = button_surface.get_rect(center=(640, 360))
	screen.blit(button_surface, button_rect)

	high_scores_surface = game_font.render("High-Scores", True, (255, 255, 255))
	high_scores_rect = high_scores_surface.get_rect(center=(640, 360))
	screen.blit(high_scores_surface, high_scores_rect)


def sort_scores(lines):
	new_scores = []
	sorted_lines = []
	index = 0
	for line in lines:
		new_scores.append(int(line.split()[1]))

	new_scores.sort(reverse=True)

	for i in range(len(new_scores)):
		index += 1
		if index > 5:
			break
		for j in range(len(lines)):
			if str(new_scores[i]) in lines[j]:
				sorted_lines.append(f"{i+1}. {lines[j][:-1]}")
	return sorted_lines


def render_scores():
	screen.fill((42, 45, 51))
	x_pos = 640
	y_pos = 10
	index = 0
	lines = []

	title = game_font.render("HIGH SCORES", True, (255, 255, 0))
	title_rect = title.get_rect(center=(640, 100))
	screen.blit(title, title_rect)

	with open("high_scores.txt", "r") as high_scores:
		for line in high_scores.readlines():
			lines.append(line)

	sorted_lines = sort_scores(lines)

	for sorted_line in sorted_lines:
		y_pos += 100
		current_surface = game_font.render(sorted_line, True, (255, 255, 255))
		current_rect = current_surface.get_rect(center=(x_pos, y_pos+100))
		screen.blit(current_surface, current_rect)


def print_scores():
	global scores_text
	with open("high_scores.txt", "r") as high_scores:
		for line in high_scores.readlines():
			scores_text += f"{line}\n"


def high_scores_input():
	save_scores = str(input("Would you like to save a score? Y or N "))
	if save_scores.casefold() == "y":
		name = str(input("Enter your name: "))
		if len(scores) > 1:
			print("Which score would you like to save?")
			for index, current_score in enumerate(scores):
				print(f"{index}: {current_score}")
			score_select = int(input())
		else:
			score_select = 0
		with open("high_scores.txt", "a") as high_scores:
			high_scores.write(f"{name}: {scores[score_select]} ({datetime.date(datetime.now())})\n")
	sys.exit()


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

game_font = pygame.font.Font("Assets/Roboto-Bold.ttf", 40)
score = 0
laser_timer = 0
infiniteshooting_timer = 0
laser_active = False
can_shoot_infinitely = False
death_index = 0

spaceship = SpaceShip('Assets/spaceship.png', 640, 500)
spaceship_group = pygame.sprite.GroupSingle()
spaceship_group.add(spaceship)

meteor_group = pygame.sprite.Group()
bonushealth_group = pygame.sprite.Group()
infiniteshooting_group = pygame.sprite.Group()

METEOR_EVENT = pygame.USEREVENT
BONUSHEALTH_EVENT = pygame.USEREVENT + 1
INFINITESHOOTING_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(METEOR_EVENT, 100)
pygame.time.set_timer(BONUSHEALTH_EVENT, 10000)
pygame.time.set_timer(INFINITESHOOTING_EVENT, 30000)

laser_group = pygame.sprite.Group()

scores = []
scores_text = ""
high_scores_clicked = False

laser1 = pygame.mixer.Sound("Assets/Laser1.mp3")
laser2 = pygame.mixer.Sound("Assets/Laser2.mp3")
laser3 = pygame.mixer.Sound("Assets/Laser3.mp3")

bonushealthsfx = pygame.mixer.Sound("Assets/BonusHealth.mp3")

death = pygame.mixer.Sound("Assets/Death.mp3")

pygame.mixer.music.load("Assets/Soundtrack.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

laser_cooldown = 1000

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			high_scores_input()
		if event.type == METEOR_EVENT:
			meteor_path = random.choice(("Assets/Meteor1.png", "Assets/Meteor2.png", "Assets/Meteor3.png"))
			meteor_x = random.randrange(0, 1280)
			meteor_y = random.randrange(-500, -50)
			meteor_x_speed = random.randrange(-1, 1)
			meteor_y_speed = random.randrange(4, 10)
			meteor = Meteor(meteor_path, meteor_x, meteor_y, meteor_x_speed, meteor_y_speed)
			meteor_group.add(meteor)
		if event.type == BONUSHEALTH_EVENT:
			bonushealth_path = "Assets/extra_life.png"
			bonushealth_x = random.randrange(0, 1280)
			bonushealth_y = random.randrange(-500, -50)
			bonushealth_x_speed = random.randrange(-1, 1)
			bonushealth_y_speed = random.randrange(4, 10)
			bonushealth = Meteor(bonushealth_path, bonushealth_x, bonushealth_y, bonushealth_x_speed, bonushealth_y_speed)
			bonushealth_group.add(bonushealth)
		if event.type == INFINITESHOOTING_EVENT:
			infiniteshooting_path = "Assets/Automatic Shooting Icon.png"
			infiniteshooting_x = random.randrange(0, 1280)
			infiniteshooting_y = random.randrange(-500, -50)
			infiniteshooting_x_speed = random.randrange(-1, 1)
			infiniteshooting_y_speed = random.randrange(4, 10)
			infiniteshooting = Meteor(infiniteshooting_path, infiniteshooting_x, infiniteshooting_y, infiniteshooting_x_speed, infiniteshooting_y_speed)
			infiniteshooting_group.add(infiniteshooting)
		if event.type == pygame.MOUSEBUTTONDOWN and laser_active:
			new_laser = Laser("Assets/Laser.png", event.pos, 15)
			laser_group.add(new_laser)
			laser_active = False
			laser_timer = pygame.time.get_ticks()
			spaceship_group.sprite.discharge()
			selected_sound = random.choice([laser1, laser2, laser3])
			selected_sound.play()
		if event.type == pygame.MOUSEBUTTONDOWN and spaceship_group.sprite.health <= 0:
			# Check if mouse position is within bounds of button
			death = 0
			if 490 <= pygame.mouse.get_pos()[0] <= 790 and 315 <= pygame.mouse.get_pos()[1] <= 400:
				high_scores_clicked = True
			else:
				high_scores_clicked = False
				spaceship_group.sprite.health = 5
				score = 0
				meteor_group.empty()
				pygame.mouse.set_pos(640, 500)

	screen.fill((42, 45, 51))

	if spaceship_group.sprite.health > 0:
		score += main_game()
	else:
		end_game()
		if high_scores_clicked:
			print_scores()
			render_scores()
		else:
			end_game()

	pygame.display.update()

	clock.tick(120)
