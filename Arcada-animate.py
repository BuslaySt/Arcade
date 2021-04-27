# Подключить нужные модули
import pygame
import os

pygame.init()
# Глобальные переменные (настройки)
win_width = 800 
win_height = 600
left_bound = win_width / 40             # границы, за которые персонаж не выходит (начинает ехать фон)
right_bound = win_width - 8 * left_bound
shift = 0

x_start, y_start = 20, 10

img_file_back = os.path.join("img",'cave.png')
# img_file_ico = pygame.image.load(os.path.join("img",'robin.ico'))
img_file_hero = {
    "stand": tuple(pygame.image.load(os.path.join("img", "robin_stand_" + s + ".png")) for s in ("01", "02", "03", "03", "02", "01")),
    "run": tuple(pygame.image.load(os.path.join("img/robin_run_" + s + ".png")) for s in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14")),
    "jump": tuple(pygame.image.load(os.path.join("img/robin_jump_" + s + ".png")) for s in ("01", "02", "03", "04", "05", "06", "07", "08", "08")),
    "die": tuple(pygame.image.load(os.path.join("img/robin_die_" + s + ".png")) for s in ("01", "02", "03", "04", "04")),
    "shoot": tuple(pygame.image.load(os.path.join("img/robin_shoot_" + s + ".png")) for s in ("01", "01", "02", "02", "03", "03", "04", "04", "05", "05", "05", "05", "05"))
    }
img_file_boar = {
    "stand": tuple(pygame.image.load(os.path.join("img", "boar_stand_" + s + ".png")) for s in ("01", "02", "01", "03", "01")),
    "run": tuple(pygame.image.load(os.path.join("img/boar_run_" + s + ".png")) for s in ("01", "02", "03", "04", "05", "06", "07", "08")),
    "die": tuple(pygame.image.load(os.path.join("img/boar_die_" + s + ".png")) for s in ("01", "01", "01", "02", "02", "02", "03", "03", "03", "04", "04")),
    }
img_file_arrow = pygame.image.load(os.path.join("img", "arrow.png"))
img_file_princess = pygame.image.load(os.path.join("img", "princess.png"))

# цвета:
C_WHITE = (255, 255, 255)
C_DARK = (48, 48, 0)
C_YELLOW = (255, 255, 87)
C_GREEN = (32, 128, 32)
C_RED = (255, 0, 0)
C_BLACK = (0, 0, 0)

# Классы
class GameSprite(pygame.sprite.Sprite):
    def __init__(self, filename, x_speed=0, y_speed=0, x=x_start, y=y_start, width=120, height=120):
        pygame.sprite.Sprite.__init__(self)
        # картинка загружается из файла и умещается в прямоугольник нужных размеров:
        self.image = pygame.transform.scale((filename).convert_alpha(), (width, height))
                    # используем convert_alpha, нам надо сохранять прозрачность

        # каждый спрайт должен хранить свойство rect - прямоугольник. Это свойство нужно для определения касаний спрайтов. 
        self.rect = self.image.get_rect().inflate(-20,0)
        # ставим персонажа в переданную точку (x, y):
        self.rect.x = x 
        self.rect.y = y
        # создаем свойства, запоминаем переданные значения:
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.stands_on = False
        self.imgnum = 0
        self.alive = True
        self.direction = "right"
        self.action = "stand"
        self.prev_action = self.action
    
    def die(self):
        self.alive = False
        self.prev_action = self.action
        self.action = "die"

    def is_alive(self):
        return self.alive

class Hero(GameSprite):
    def __init__(self, filename, x, y):
        super().__init__(filename, x=x, y=y)

    def animate(self):
        #анимация
        if self.alive:
            filename = img_file_hero[self.action] #список с картинками спрайта
            self.imgnum += 1 #счетчик картинок
            if self.action == "run" and self.imgnum >= len(img_file_hero[self.action])*4:
                self.imgnum = 0
            if self.action == "stand" and self.imgnum >= len(img_file_hero[self.action])*4:
                self.imgnum = 0
            if self.action == "jump" and self.imgnum >= len(img_file_hero[self.action])*4:
                self.imgnum = len(img_file_hero[self.action])*3
            if self.action == "shoot" and self.imgnum >= len(img_file_hero[self.action]) * 4:
                arrow = Arrow(img_file_arrow, self.rect.x, self.rect.y, self.direction)
                arrows.add(arrow)
                all_sprites.add(arrow)
                self.action = "stand"
                self.imgnum = 0
                filename = img_file_hero[self.action]
            # каждый четвертый кадр обновление картинки
            self.image = pygame.transform.scale(filename[int(self.imgnum/4)], (120, 120)).convert_alpha() 
            # если бежим влево, то картинку отзеркалить
            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            filename = img_file_hero["die"] #список с картинками спрайта
            self.imgnum += 1 #счетчик картинок
            if self.imgnum >= len(img_file_hero["die"]) * 20:
                self.imgnum -= 1
            # каждый четвертый кадр обновление картинки
            self.image = pygame.transform.scale(filename[int(self.imgnum / 20)], (120, 120)).convert_alpha()
            # если бежим влево, то картинку отзеркалить
            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.animate()
        if self.alive:
            # движение по горизонтали
            self.move_x()
            # движение по вертикали
            self.move_y()

    def move_x(self):
        self.rect.x += self.x_speed
        if self.x_speed == 0 and self.action != "jump" and self.action != "shoot":
            self.action = "stand"
            self.prev_action = self.action
        # если зашли за стенку, то встанем вплотную к стене
        platforms_touched = pygame.sprite.spritecollide(self, barriers, False)
        if self.x_speed > 0: # идем направо, правый край персонажа - вплотную к левому краю стены
            for p in platforms_touched:
                self.rect.right = min(self.rect.right, p.rect.left) # если коснулись сразу нескольких, то правый край - минимальный из возможных
        elif self.x_speed < 0: # идем налево, ставим левый край персонажа вплотную к правому краю стены
            for p in platforms_touched:
                self.rect.left = max(self.rect.left, p.rect.right) # если коснулись нескольких стен, то левый край - максимальный

    def move_y(self):
        self.gravitate()
        self.rect.y += self.y_speed
        # если зашли за стенку, то встанем вплотную к стене
        platforms_touched = pygame.sprite.spritecollide(self, barriers, False)
        if self.y_speed > 0: # идем вниз
            for p in platforms_touched:
                self.y_speed = 0
                self.action = self.prev_action
                # Проверяем, какая из платформ снизу самая высокая, выравниваемся по ней, запоминаем её как свою опору:
                if p.rect.top < self.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.stands_on = True
        elif self.y_speed < 0: # идем вверх
            self.stands_on = False  # пошли наверх, значит, ни на чем уже не стоим!
            for p in platforms_touched:
                self.y_speed = 0  # при столкновении со стеной вертикальная скорость гасится
                self.rect.top = max(self.rect.top, p.rect.bottom) # выравниваем верхний край по нижним краям стенок, на которые наехали

    def isofflimits(self, right_bound = right_bound, left_bound = left_bound):
        return (self.rect.x > right_bound and self.x_speed > 0 or self.rect.x < left_bound and self.x_speed < 0)

    def gravitate(self):
        self.y_speed += 0.25        
    
    def jump(self, y):
        if self.stands_on:
            self.y_speed = y
            self.prev_action = self.action
            self.action = "jump"

    def runright(self):
        self.x_speed = 5
        self.direction = "right"
        self.action = "run"
        self.prev_action = self.action
        self.imgnum = 0 

    def runleft(self):
        self.x_speed = -5
        self.direction = "left"
        self.action = "run"
        self.prev_action = self.action
        self.imgnum = 0

    def stand(self):
        self.x_speed = 0
        if self.action != "jump" and self.action != "jump":
            self.action = "stand"
            self.prev_action = self.action
        self.imgnum = 0
    
    def speed(self):
        return self.x_speed
    
    def shoot(self):
        if self.stands_on:
            self.action = "shoot"
            self.imgnum = 0
            self.prev_action = self.action

    def resurrect(self):
        self.alive = True
        self.rect.x = x_start
        self.rect.y = y_start
        self.stand()

class Boar(GameSprite):
    def __init__(self, filename, x, y, action, left_x = 200, right_x = 500):
        super().__init__(filename, x=x, y=y, width=80, height=80)
        self.action = action
        self.right_x = right_x
        self.left_x = left_x
        self.prev_action = self.action
    def animate(self):
        #анимация
        filename = img_file_boar[self.action] #список с картинками спрайта
        self.imgnum += 1 #счетчик картинок
        if self.action == "run" and self.imgnum >= len(img_file_boar[self.action])*5:
            self.imgnum = 0
        if self.action == "stand" and self.imgnum >= len(img_file_boar[self.action])*5:
            self.imgnum = 0
        if self.action == "die" and self.imgnum >= len(img_file_boar[self.action])*5:
            self.imgnum -= 1
        # каждый пятый кадр обновление картинки
        self.image = pygame.transform.scale(filename[int(self.imgnum/5)], (80, 80)).convert_alpha() 
        # если бежим влево, то картинку отзеркалить
        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.animate()
        # движение по горизонтали
        if self.action == "run":
            self.x_speed = 4
            self.rect.x += self.x_speed if self.direction=="right" else -1*self.x_speed
            if self.rect.x > self.right_x+shift:
                self.direction = "left"
            elif self.rect.x < self.left_x+shift:
                self.direction = "right"
    def resurrect(self):
        self.alive = True
        self.action = self.prev_action

class Arrow(GameSprite):
    def __init__(self, filename, x, y, direction):
        super().__init__(filename, width=60, height=10)
        if direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.x = x+60 if direction == "right" else x
        self.rect.y = y+60
        self.x_speed = 10 if direction == "right" else -10
        
    def update(self):
        self.y_speed += 0.05
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed
        if 0 >= self.rect.x >= win_width:
            self.kill()

class Wall(pygame.sprite.Sprite):
    def __init__(self, x=20, y=0, width=120, height=120, color=C_GREEN):
        pygame.sprite.Sprite.__init__(self)
        # картинка - новый прямоугольник нужных размеров:
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        # создаем свойство rect 
        self.rect = self.image.get_rect().inflate(-20,0)
        self.rect.x = x 
        self.rect.y = y


# Запуск игры
pygame.init() 
pygame.display.set_caption("ARCADE")
# pygame.display.set_icon(img_file_ico)
window = pygame.display.set_mode([win_width, win_height])

back = pygame.transform.scale(pygame.image.load(img_file_back).convert(), (win_width, win_height)) 

# список всех персонажей игры:
all_sprites = pygame.sprite.Group()
# списки препятствий, стрел и врагов:
barriers = pygame.sprite.Group()
arrows = pygame.sprite.Group()
boars = pygame.sprite.Group()


# создаем персонажей, добавляем в списки спрайтов:
if 1:
    hero = Hero(img_file_hero["stand"][0], 20, 0)
    all_sprites.add(hero)
    boar1 = Boar(img_file_boar["stand"][0], 350, 320, "stand")
    boar2 = Boar(img_file_boar["run"][0], 250, 510, "run")
    boars.add(boar1, boar2)
    all_sprites.add(boar1, boar2)
    # создаем финальный спрайт, добавляем его:
    pr = GameSprite(img_file_princess, x = win_width + 500, y = win_height - 130, width = 70, height=120)
    all_sprites.add(pr)

# создаем стены, добавляем их:
if 2:
    w = Wall(50, 150, 480, 20)
    barriers.add(w)
    all_sprites.add(w)
    w = Wall(250, 100, 20, 120)
    barriers.add(w)
    all_sprites.add(w)
    w = Wall(-250, 00, 50, 600)
    barriers.add(w)
    all_sprites.add(w)
    w = Wall(700, 00, 50, 400)
    barriers.add(w)
    all_sprites.add(w)
    w = Wall(350, 400, 640, 20)
    barriers.add(w)
    all_sprites.add(w)
    w = Wall(-200, 590, 1600, 20)
    barriers.add(w)
    all_sprites.add(w)

# Основной цикл игры:
run = True 
finished = False

while run:
    # Обработка событий
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            run = False 
        if event.type == pygame.KEYDOWN and hero.is_alive(): 
            if event.key == pygame.K_LEFT:
                hero.runleft()
            elif event.key == pygame.K_RIGHT:
                hero.runright()
            elif event.key == pygame.K_UP:
                hero.jump(-7)
            elif event.key == pygame.K_SPACE:
                hero.shoot()

        if event.type == pygame.KEYUP and hero.is_alive(): 
            if event.key == pygame.K_LEFT:
                hero.stand()
            elif event.key == pygame.K_RIGHT:
                hero.stand()

    if not finished:
        # Перемещение игровых объектов
        all_sprites.update()

        # проверяем границы экрана: 
        if hero.isofflimits(): # при выходе влево или вправо переносим изменение в сдвиг экрана
            shift -= hero.speed()
            # перемещаем на общий сдвиг все спрайты:
            for s in all_sprites:
                s.rect.x -= hero.speed() # сам hero тоже в этом списке, поэтому его перемещение визуально отменится

        # Отрисовка
        # рисуем фон со сдвигом
        local_shift = shift % win_width 
        window.blit(back, (local_shift, 0)) 
        if local_shift != 0:
            window.blit(back, (local_shift - win_width, 0)) 

        # нарисуем все спрайты на экранной поверхности
        all_sprites.draw(window)

        boarshot = pygame.sprite.groupcollide(boars, arrows, False, True)
        for boar in boarshot:
            boar.die()

        boarbite = pygame.sprite.spritecollide(hero, boars, False)
        for boar in boarbite:
            if boar.is_alive() and hero.is_alive():
                hero.die()
                
        if pygame.sprite.collide_rect(hero, pr):
            finished = True
            # пишем текст на экране
            text = pygame.font.SysFont('Arial', 72).render("YOU WIN!", 1, C_RED)
            window.blit(text, (250, 200))

        if hero.is_alive():
            restart = 0
        else:
            restart += 1
            if restart >= 100:
                finished = True

    else:
        restart += 1
        text = pygame.font.SysFont('Arial', 72).render("Restarting...", 1, C_RED)
        window.blit(text, (250, 270))

        if restart >= 200:
            for s in all_sprites:
                s.rect.x -= shift
            shift = 0
            finished = False
            hero.resurrect()
            for boar in boars:
                boar.resurrect()

    pygame.display.update() 

    # Пауза
    pygame.time.delay(20)