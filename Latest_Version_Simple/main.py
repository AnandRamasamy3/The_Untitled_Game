# print ("Anand Ramasamy")



import pygame,sys,time,threading,json
from pygame.locals import *
from math import *

# "invisible","ghost","trap_bomb","crystal_shield","light_marker"

pygame.init()
WIDTH,HEIGHT=1250,660
surface=pygame.display.set_mode((WIDTH,HEIGHT),0,32)
fps=200
ft=pygame.time.Clock()
pygame.display.set_caption('The Untitled Game')

app_font=pygame.font.SysFont('segoe print',17,bold=True,italic=False)

images={}

images.update({"avatar":pygame.image.load("src/avatar.png")})
images.update({"enemy":pygame.image.load("src/enemy.png")})
images.update({"background_image":pygame.image.load("src/background.jpg")})
images.update({"theme_image":pygame.image.load("src/theme_image.png")})

images["theme_image"]=pygame.transform.scale(images["theme_image"],(WIDTH,HEIGHT))


class game:
	def __init__(self,surface=surface,images=images):
		pass
		self.surface=surface
		self.images=images
		self.color=[]
		self.walls=[]
		self.powers={}
		self.doors_and_buttons=[]
		self.doors_for_collision_detection=[]
		self.enemies=[]
		self.get_database()
		self.x=self.init_x_position=WIDTH//2-1000
		self.y=self.init_y_position=HEIGHT//2-2100
		self.move_session=[None,None]
		self.time_last_to_move=10
		self.speed=2.8
		self.avatar_size=40
		self.images["enemy"]=pygame.transform.scale(self.images["enemy"],(self.avatar_size,self.avatar_size))
		self.avatar_facing_direction="up"
		self.main_map_width=WIDTH//5
		self.main_map_height=HEIGHT//5
		self.main_map_x=WIDTH-self.main_map_width
		self.main_map_y=0
		self.is_invisble=False
		self.is_ghost=False
		self.duration_for_door_open=30
		self.undo_moves=[]
		self.bullet_gun_shots=[]
		self.bullet_gun_range=100
		self.bomb=[None,None,None]
		self.bomb_effective_range=600
		# print (self.x,self.y)
		# print ()
	def get_database(self):
		f_obj=open("src/database.json",)
		data=json.load(f_obj)
		self.color=data["general_colors"]
		self.walls=data["walls"]
		self.powers=data["powers"]
		self.doors_and_buttons=data["doors_and_buttons"]
		self.enemies=data["enemies"]
		# print (self.powers)
		# print (self.walls)
		x,y,size=500,40,30
		for power in self.powers:#power_button
			self.powers[power].update({
				"x":x,
				"y":y,
				"radius":size,
				"last_triggered":time.time()-self.powers[power]["availability"]
			})
			image=pygame.image.load(self.powers[power]["icon_url"])
			image=pygame.transform.scale(image,(self.powers[power]["radius"]*2,self.powers[power]["radius"]*2))
			self.powers[power].update({
				"image":image
			})
			x+=size*2+10
		# print (self.powers)
		f_obj.close()
	def circle(self,point,radius,angle):
		x=int(point[0]+radius*cos(angle))
		y=int(point[0]+radius*sin(angle))
		return [x,y]
	def angle(self,point_1,point_2,point_3):
		ang = degrees(
			atan2(point_3[1]-point_2[1],point_3[0]-point_2[0])-atan2(point_1[1]-point_2[1],point_1[0]-point_2[0]))
		return ang + 360 if ang < 0 else ang
	def euclidean_distance(self,point_1,point_2):
		point=sqrt( ((point_1[0]-point_2[0])**2)+((point_1[1]-point_2[1])**2) )
		return point
	def check_collision_for_avatar_and_wall(self):
		if self.is_ghost:
			return False
		for enemy in self.enemies:
			# print  (self.x+enemy["position"][0]-self.avatar_size//2,WIDTH//2-self.avatar_size//2,self.x+enemy["position"][0]+self.avatar_size//2)
			avatar_boundaries=[
				(self.x+enemy["position"][0]-self.avatar_size//2<=(WIDTH//2-self.avatar_size//2)<=self.x+enemy["position"][0]+self.avatar_size//2 and self.y+enemy["position"][1]-self.avatar_size//2<=(HEIGHT//2-self.avatar_size//2)<=self.y+enemy["position"][1]+self.avatar_size//2),
				(self.x+enemy["position"][0]-self.avatar_size//2<=(WIDTH//2-self.avatar_size//2)<=self.x+enemy["position"][0]+self.avatar_size//2 and self.y+enemy["position"][1]-self.avatar_size//2<=(HEIGHT//2+self.avatar_size//2)<=self.y+enemy["position"][1]+self.avatar_size//2),
				(self.x+enemy["position"][0]-self.avatar_size//2<=(WIDTH//2+self.avatar_size//2)<=self.x+enemy["position"][0]+self.avatar_size//2 and self.y+enemy["position"][1]-self.avatar_size//2<=(HEIGHT//2-self.avatar_size//2)<=self.y+enemy["position"][1]+self.avatar_size//2),
				(self.x+enemy["position"][0]-self.avatar_size//2<=(WIDTH//2+self.avatar_size//2)<=self.x+enemy["position"][0]+self.avatar_size//2 and self.y+enemy["position"][1]-self.avatar_size//2<=(HEIGHT//2+self.avatar_size//2)<=self.y+enemy["position"][1]+self.avatar_size//2)
			]
			if True in avatar_boundaries:
				return True
		for doors in self.doors_for_collision_detection:
			avatar_boundaries=[
				(doors[0]<=(WIDTH//2-self.avatar_size//2)<=doors[0]+doors[2] and doors[1]<=(HEIGHT//2-self.avatar_size//2)<=doors[1]+doors[3]),
				(doors[0]<=(WIDTH//2-self.avatar_size//2)<=doors[0]+doors[2] and doors[1]<=(HEIGHT//2+self.avatar_size//2)<=doors[1]+doors[3]),
				(doors[0]<=(WIDTH//2+self.avatar_size//2)<=doors[0]+doors[2] and doors[1]<=(HEIGHT//2-self.avatar_size//2)<=doors[1]+doors[3]),
				(doors[0]<=(WIDTH//2+self.avatar_size//2)<=doors[0]+doors[2] and doors[1]<=(HEIGHT//2+self.avatar_size//2)<=doors[1]+doors[3])
			]
			if True in avatar_boundaries:
				return True
		for wall in self.walls:
			# print (wall)
			avatar_boundaries=[
				(self.x+wall[0][0]<=(WIDTH//2-self.avatar_size//2)<=self.x+wall[1][0] and self.y+wall[0][1]<=(HEIGHT//2-self.avatar_size//2)<=self.y+wall[1][1]),
				(self.x+wall[0][0]<=(WIDTH//2-self.avatar_size//2)<=self.x+wall[1][0] and self.y+wall[0][1]<=(HEIGHT//2+self.avatar_size//2)<=self.y+wall[1][1]),
				(self.x+wall[0][0]<=(WIDTH//2+self.avatar_size//2)<=self.x+wall[1][0] and self.y+wall[0][1]<=(HEIGHT//2-self.avatar_size//2)<=self.y+wall[1][1]),
				(self.x+wall[0][0]<=(WIDTH//2+self.avatar_size//2)<=self.x+wall[1][0] and self.y+wall[0][1]<=(HEIGHT//2+self.avatar_size//2)<=self.y+wall[1][1])
			]
			if True in avatar_boundaries:
				# print (wall)
				return True
		return False
	def draw_avatar(self):
		avatar=pygame.transform.scale(self.images["avatar"],(self.avatar_size,self.avatar_size))
		if self.avatar_facing_direction=="right":
			avatar=pygame.transform.rotate(avatar,270)
		elif self.avatar_facing_direction=="down":
			avatar=pygame.transform.rotate(avatar,180)
		elif self.avatar_facing_direction=="left":
			avatar=pygame.transform.rotate(avatar,90)
		elif self.avatar_facing_direction=="up":
			avatar=pygame.transform.rotate(avatar,0)
		self.surface.blit(avatar,(WIDTH//2-self.avatar_size//2,HEIGHT//2-self.avatar_size//2))
		# pygame.draw.rect(self.surface,self.color["white"],(WIDTH//2-self.avatar_size//2,HEIGHT//2-self.avatar_size//2,self.avatar_size,self.avatar_size))
	def draw_enemies(self):
		for enemy in self.enemies:
			# print (enemy)
			if enemy["alive"]=="True":
				# pygame.draw.rect(self.surface,self.color["red"],(self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2,self.avatar_size,self.avatar_size))
				self.surface.blit(self.images["enemy"],(self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2))
				# print (self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2)
	def move_avatar(self):
		if self.move_session[0]!=None and self.move_session[1]!=None:
			if time.time()<=self.move_session[1]:
				before=[self.x,self.y]
				if self.move_session[0]=="right":
					self.x-=self.speed
					if self.check_collision_for_avatar_and_wall():
						# print ("congradulations right got back")
						self.x+=self.speed
				elif self.move_session[0]=="left":
					self.x+=self.speed
					if self.check_collision_for_avatar_and_wall():
						# print ("congradulations left got back")
						self.x-=self.speed
				elif self.move_session[0]=="up":
					self.y+=self.speed
					if self.check_collision_for_avatar_and_wall():
						# print ("congradulations up got back")
						self.y-=self.speed
				elif self.move_session[0]=="down":
					self.y-=self.speed
					if self.check_collision_for_avatar_and_wall():
						# print ("congradulations down got back")
						self.y+=self.speed
				# print (self.undo_moves)
				if abs(self.x-before[0])==0 and abs(self.y-before[1])==0:
					if len(self.undo_moves)==0:
						self.undo_moves.append([before[0]-self.x,before[1]-self.y])
					else:
						self.x+=self.undo_moves[-1][0]
						self.y+=self.undo_moves[-1][1]
						self.undo_moves.pop(-1)
						self.move_session=[None,None]
				else:
					self.undo_moves.append([before[0]-self.x,before[1]-self.y])
					if len(self.undo_moves)>10:
						self.undo_moves.pop(0)
			else:
				self.move_session=[None,None]
	def draw_main_map(self):
		pygame.draw.rect(self.surface,self.color["black"],(self.main_map_x,self.main_map_y,self.main_map_width+2,self.main_map_height+1))
		pygame.draw.rect(self.surface,self.color["garden"],(self.main_map_x,self.main_map_y,self.main_map_width,self.main_map_height))
		avatar_x=int(self.main_map_x+((WIDTH//2-self.x)/5300)*self.main_map_width)
		avatar_y=int(self.main_map_y+((HEIGHT//2-self.y)/4000)*self.main_map_height)
		main_map=pygame.transform.scale(self.images["background_image"],(self.main_map_width,self.main_map_height))
		# print (int(self.x),int(self.y),x,y)
		self.surface.blit(main_map,(self.main_map_x,self.main_map_y))
		for doors_and_button in self.doors_and_buttons:
			x=int(self.main_map_x+(doors_and_button["button_position"][0]/5300)*self.main_map_width)
			y=int(self.main_map_y+(doors_and_button["button_position"][1]/4000)*self.main_map_height)
			radius=int((doors_and_button["button_radius"]/5300)*self.main_map_width)
			pygame.draw.circle(self.surface,self.color["button"],(x,y),radius)
			x=int(self.main_map_x+((doors_and_button["door_position"][0])/5300)*self.main_map_width)
			y=int(self.main_map_y+((doors_and_button["door_position"][1])/4000)*self.main_map_height)
			width=(doors_and_button["door_position"][2]/5300)*self.main_map_width
			height=(doors_and_button["door_position"][3]/4000)*self.main_map_height
			if time.time()<=doors_and_button["last_triggered"]+doors_and_button["duration_for_door_open"]:#self.duration_for_door_open:
				pass
			else:
				pass
				# print (x,y,width,height)
				pygame.draw.rect(self.surface,self.color["door"],(x,y,width,height))
		for enemy in self.enemies:
			if enemy["alive"]=="True":
				x=int(self.main_map_x+((enemy["position"][0]-self.avatar_size//2)/5300)*self.main_map_width)
				y=int(self.main_map_y+((enemy["position"][1]-self.avatar_size//2)/4000)*self.main_map_height)
				pygame.draw.circle(self.surface,self.color["red"],(x,y),1)
		# bomb
		if self.bomb!=[None,None,None]:
			x=int(self.main_map_x+((self.bomb[0][0])/5300)*self.main_map_width)
			y=int(self.main_map_y+((self.bomb[0][1])/4000)*self.main_map_height)
			radius=int((self.bomb[1]/5300)*self.main_map_width)
			pygame.draw.circle(self.surface,self.color["bullet"],(x,y),radius)
		# avatar
		pygame.draw.circle(self.surface,self.color["green"],(avatar_x,avatar_y),2)
	def trigger_doors_via_buttons(self):
		pass
		for button in self.doors_and_buttons:
			dist=self.euclidean_distance([WIDTH//2,HEIGHT//2],(self.x+button["button_position"][0],self.y+button["button_position"][1]))
			# print (dist,button["button_radius"])
			if dist<=button["button_radius"]:
				# print ("==================>>>>>>>>>>>>>>>>>>>>>>>.oooops")
				self.doors_and_buttons[self.doors_and_buttons.index(button)]["last_triggered"]=time.time()
	def draw_doors_and_buttons(self):
		self.doors_for_collision_detection=[]
		for doors_and_button in self.doors_and_buttons:
			pygame.draw.circle(self.surface,self.color["button"],(int(self.x)+doors_and_button["button_position"][0],int(self.y)+doors_and_button["button_position"][1]),doors_and_button["button_radius"])
			# print (time.time()<=doors_and_button["last_triggered"]+self.duration_for_door_open)
			if time.time()<=doors_and_button["last_triggered"]+doors_and_button["duration_for_door_open"]:#self.duration_for_door_open:
				pass
				# print ("hahahaha")
			else:
				pass
				pygame.draw.rect(self.surface,self.color["door"],(self.x+doors_and_button["door_position"][0],self.y+doors_and_button["door_position"][1],doors_and_button["door_position"][2],doors_and_button["door_position"][3]))
				self.doors_for_collision_detection.append([self.x+doors_and_button["door_position"][0],self.y+doors_and_button["door_position"][1],doors_and_button["door_position"][2],doors_and_button["door_position"][3]])
	def draw_powers_menu(self):
		for power_button in self.powers:
			pygame.draw.circle(self.surface,self.color["black"],(self.powers[power_button]["x"],self.powers[power_button]["y"]),self.powers[power_button]["radius"]+2)
			pygame.draw.circle(self.surface,self.color["garden"],(self.powers[power_button]["x"],self.powers[power_button]["y"]),self.powers[power_button]["radius"])
			self.surface.blit(self.powers[power_button]["image"],(self.powers[power_button]["x"]-self.powers[power_button]["radius"],self.powers[power_button]["y"]-self.powers[power_button]["radius"]))
	def invisible(self,activate=False):
		pass
		# print (int(time.time()),int(self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]),int(self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["time_to_reboot"]))
		if time.time()<=self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]:
			# print ("already in active")
			pass
			init=self.powers["invisible"]["last_triggered"]
			now=time.time()
			last=self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]
			active_percentage_of_bar=(now-init)/(last-init)
			# print ("active",active_percentage_of_bar)
			pygame.draw.rect(self.surface,self.color["red"],(self.powers["invisible"]["x"]-self.powers["invisible"]["radius"],self.powers["invisible"]["y"]+self.powers["invisible"]["radius"]+5,self.powers["invisible"]["radius"]*2*active_percentage_of_bar,10))
			pygame.draw.rect(self.surface,self.color["black"],(self.powers["invisible"]["x"]-self.powers["invisible"]["radius"],self.powers["invisible"]["y"]+self.powers["invisible"]["radius"]+5,self.powers["invisible"]["radius"]*2,10),1)
			pass
		else:
			if time.time()<=self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]+self.powers["invisible"]["time_to_reboot"]:
				# print ("rebooting")
				pass
				init=self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]
				now=time.time()
				last=self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]+self.powers["invisible"]["time_to_reboot"]
				reboot_percentage_of_bar=(now-init)/(last-init)
				# print ("reboot",reboot_percentage_of_bar)
				pygame.draw.rect(self.surface,self.color["green"],(self.powers["invisible"]["x"]-self.powers["invisible"]["radius"],self.powers["invisible"]["y"]+self.powers["invisible"]["radius"]+5,self.powers["invisible"]["radius"]*2*reboot_percentage_of_bar,10))
				pygame.draw.rect(self.surface,self.color["black"],(self.powers["invisible"]["x"]-self.powers["invisible"]["radius"],self.powers["invisible"]["y"]+self.powers["invisible"]["radius"]+5,self.powers["invisible"]["radius"]*2,10),1)
				pass
			else:
				# print ("available")
				if activate:
					self.is_invisble=True
					self.powers["invisible"]["last_triggered"]=time.time()
	def ghost(self,activate=False):
		# print ("Anand Ramasamy")
		pass
		# print (int(time.time()),int(self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]),int(self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["time_to_reboot"]))
		if time.time()<=self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"]:
			# print ("already in active")
			# print (time.time(),time.time()-self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"])
			init=self.powers["ghost"]["last_triggered"]
			now=time.time()
			last=self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"]
			active_percentage_of_bar=(now-init)/(last-init)
			# print ("active",active_percentage_of_bar)
			pygame.draw.rect(self.surface,self.color["red"],(self.powers["ghost"]["x"]-self.powers["ghost"]["radius"],self.powers["ghost"]["y"]+self.powers["ghost"]["radius"]+5,self.powers["ghost"]["radius"]*2*active_percentage_of_bar,10))
			pygame.draw.rect(self.surface,self.color["black"],(self.powers["ghost"]["x"]-self.powers["ghost"]["radius"],self.powers["ghost"]["y"]+self.powers["ghost"]["radius"]+5,self.powers["ghost"]["radius"]*2,10),1)
			pass
		else:
			if time.time()<=self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"]+self.powers["ghost"]["time_to_reboot"]:
				# print ("rebooting")
				init=self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"]
				now=time.time()
				last=self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"]+self.powers["ghost"]["time_to_reboot"]
				reboot_percentage_of_bar=(now-init)/(last-init)
				# print ("reboot",reboot_percentage_of_bar)
				pygame.draw.rect(self.surface,self.color["green"],(self.powers["ghost"]["x"]-self.powers["ghost"]["radius"],self.powers["ghost"]["y"]+self.powers["ghost"]["radius"]+5,self.powers["ghost"]["radius"]*2*reboot_percentage_of_bar,10))
				pygame.draw.rect(self.surface,self.color["black"],(self.powers["ghost"]["x"]-self.powers["ghost"]["radius"],self.powers["ghost"]["y"]+self.powers["ghost"]["radius"]+5,self.powers["ghost"]["radius"]*2,10),1)
				pass
				self.speed=2.8
				self.is_ghost=False
				pass
			else:
				# print ("available")
				if activate:
					self.is_invisble=True
					self.is_ghost=True
					self.powers["ghost"]["last_triggered"]=time.time()
					self.speed=4
	def trap_bomb(self,activate=False):
		# print ("Anand Ramasamy")
		pass
		# print (int(time.time()),int(self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["availability"]),int(self.powers["invisible"]["last_triggered"]+self.powers["invisible"]["time_to_reboot"]))
		if time.time()<=self.powers["trap_bomb"]["last_triggered"]+self.powers["trap_bomb"]["availability"]:
			# print ("already in active")
			# print (time.time(),time.time()-self.powers["ghost"]["last_triggered"]+self.powers["ghost"]["availability"])
			init=self.powers["trap_bomb"]["last_triggered"]
			now=time.time()
			last=self.powers["trap_bomb"]["last_triggered"]+self.powers["trap_bomb"]["availability"]
			active_percentage_of_bar=(now-init)/(last-init)
			# print ("active",active_percentage_of_bar)
			pygame.draw.rect(self.surface,self.color["red"],(self.powers["trap_bomb"]["x"]-self.powers["trap_bomb"]["radius"],self.powers["trap_bomb"]["y"]+self.powers["trap_bomb"]["radius"]+5,self.powers["trap_bomb"]["radius"]*2*active_percentage_of_bar,10))
			pygame.draw.rect(self.surface,self.color["black"],(self.powers["trap_bomb"]["x"]-self.powers["trap_bomb"]["radius"],self.powers["trap_bomb"]["y"]+self.powers["trap_bomb"]["radius"]+5,self.powers["trap_bomb"]["radius"]*2,10),1)
			pass
			if activate:
				self.bomb[2]=True
			pass
		else:
			if time.time()<=self.powers["trap_bomb"]["last_triggered"]+self.powers["trap_bomb"]["availability"]+self.powers["trap_bomb"]["time_to_reboot"]:
				# print ("rebooting")
				init=self.powers["trap_bomb"]["last_triggered"]+self.powers["trap_bomb"]["availability"]
				now=time.time()
				last=self.powers["trap_bomb"]["last_triggered"]+self.powers["trap_bomb"]["availability"]+self.powers["trap_bomb"]["time_to_reboot"]
				reboot_percentage_of_bar=(now-init)/(last-init)
				# print ("reboot",reboot_percentage_of_bar)
				pygame.draw.rect(self.surface,self.color["green"],(self.powers["trap_bomb"]["x"]-self.powers["trap_bomb"]["radius"],self.powers["trap_bomb"]["y"]+self.powers["trap_bomb"]["radius"]+5,self.powers["trap_bomb"]["radius"]*2*reboot_percentage_of_bar,10))
				pygame.draw.rect(self.surface,self.color["black"],(self.powers["trap_bomb"]["x"]-self.powers["trap_bomb"]["radius"],self.powers["trap_bomb"]["y"]+self.powers["trap_bomb"]["radius"]+5,self.powers["trap_bomb"]["radius"]*2,10),1)
				pass
				self.bomb=[None,None,None]
				pass
			else:
				# print ("available")
				if activate:
					self.powers["trap_bomb"]["last_triggered"]=time.time()
					self.bomb=[[int(0-self.x+WIDTH//2),int(0-self.y+HEIGHT//2)],0,False]
					# print (self.bomb)
		if self.bomb!=[None,None,None]:
			speed=5
			if self.bomb[2]:
				if self.bomb[1]<self.bomb_effective_range:
					self.bomb[1]+=speed
					# print (self.bomb)
					radius=self.bomb[1]
					center=[int(self.x+self.bomb[0][0]),int(self.y+self.bomb[0][1])]
					# print (center)
					for radius_many in range(1,radius,10):
						# print (radius_many)
						pygame.draw.circle(self.surface,self.color["bullet"],center,radius_many,1)
					enemies_to_be_killed=[]
					for enemy in self.enemies:
						avatar_boundaries=[
							self.euclidean_distance([self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2],center)<=radius,
							self.euclidean_distance([self.x+enemy["position"][0]+self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2],center)<=radius,
							self.euclidean_distance([self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]+self.avatar_size//2],center)<=radius,
							self.euclidean_distance([self.x+enemy["position"][0]+self.avatar_size//2,self.y+enemy["position"][1]+self.avatar_size//2],center)<=radius
						]
						# print (avatar_boundaries)
						if True in avatar_boundaries:
							# print ("ooops",time.time())
							enemies_to_be_killed.append(self.enemies.index(enemy))
					for enemy_index in enemies_to_be_killed:
						self.enemies.pop(enemy_index)
				else:
					self.bomb=[None,None,None]
	def trigger_powers(self,key):
		# print (key)
		if key=="1":
			self.invisible(activate=True)
		elif key=="2":
			self.ghost(activate=True)
		elif key=="3":
			self.trap_bomb(activate=True)
	def run_powers(self):
		self.invisible()
		self.ghost()
		self.trap_bomb()
	def restart_position(self):
		self.x=self.init_x_position
		self.y=self.init_y_position
	def draw_bullet_rays(self):
		# print (self.bullet_gun_shots)
		speed=10
		to_be_ended=[]
		for shot in self.bullet_gun_shots:
			x,y=int(self.x+shot[0][0]),int(self.y+shot[0][1])
			radius=shot[1]
			direction=shot[2]
			if direction=="up":
				target=[x,y-radius+speed]
			elif direction=="down":
				target=[x,y+radius+speed]
			elif direction=="right":
				target=[x+radius+speed,y]
			elif direction=="left":
				target=[x-radius+speed,y]
			# print (self.euclidean_distance((x,y),target))
			enemies_to_be_killed=[]
			for enemy in self.enemies:
				# print (self.euclidean_distance([self.x+enemy["position"][0]-self.avatar_size,self.y+enemy["position"][1]-self.avatar_size],target))
				# print ([self.x+enemy["position"][0]+self.avatar_size//2,self.y+enemy["position"][1]+self.avatar_size//2],target[0]+self.avatar_size//2)
				avatar_boundaries=[
					self.euclidean_distance([self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2],target)<=20,
					self.euclidean_distance([self.x+enemy["position"][0]+self.avatar_size//2,self.y+enemy["position"][1]-self.avatar_size//2],target)<=20,
					self.euclidean_distance([self.x+enemy["position"][0]-self.avatar_size//2,self.y+enemy["position"][1]+self.avatar_size//2],target)<=20,
					self.euclidean_distance([self.x+enemy["position"][0]+self.avatar_size//2,self.y+enemy["position"][1]+self.avatar_size//2],target)<=20
				]
				# print (avatar_boundaries)
				if True in avatar_boundaries:
					# print ("ooops",time.time())
					enemies_to_be_killed.append(self.enemies.index(enemy))
			for enemy_index in enemies_to_be_killed:
				self.enemies.pop(enemy_index)
			# edge_points=[[x,y]]
			# for angle in [315,45]:
			# 	edge_points.append(self.circle(target,radius,angle))
			# pygame.draw.polygon(self.surface,self.color["bullet"],edge_points)
			pygame.draw.circle(self.surface,self.color["bullet"],target,20)
			self.bullet_gun_shots[self.bullet_gun_shots.index(shot)][1]+=speed
			if radius>300:
				to_be_ended.append(self.bullet_gun_shots.index(shot))
			# pygame.draw.circle(self.surface,self.color["bullet"],(x,y),10)#self.
		for index in to_be_ended:
			self.bullet_gun_shots.pop(index)
	def count_remaining_enemies(self):
		# print (self.enemies)
		remaining=0
		for enemy in self.enemies:
			remaining+=1 if enemy["alive"]=="True" else 0
		return remaining
	def do_main_operations(self):
		pass
		self.move_avatar()
		self.draw_doors_and_buttons()
		self.draw_avatar()
		self.draw_enemies()
		self.draw_powers_menu()
		self.draw_main_map()
		self.run_powers()
		self.trigger_doors_via_buttons()
		self.draw_bullet_rays()
		# print (self.bullet_gun_shots)
		# print (self.doors_for_collision_detection)
		# print (self.undo_moves)
	def play_musics(self):
		pass
	def draw_question_bar(self,message):
		pygame.draw.rect(self.surface,self.color["question_bar"],(960,30,240,80))
		click=pygame.mouse.get_pressed()
		mouse=pygame.mouse.get_pos()
		# if click[0]==1:
		if 960<=mouse[0]<=1200 and 30<=mouse[1]<=110:
			pygame.draw.rect(self.surface,self.color["question_bar_hover"],(960,30,240,80))
		temp_font=pygame.font.SysFont("Menlo, Consolas, DejaVu Sans Mono, monospace",33,bold=True,italic=False)
		object_temp_font=temp_font.render(message,False,self.color["white"])
		if message=="Play":
			self.surface.blit(object_temp_font,(1020,50))
		else:
			self.surface.blit(object_temp_font,(980,50))
		if click[0]==1:
			if 960<=mouse[0]<=1200 and 30<=mouse[1]<=110:
				return True
		# draw exit
		pygame.draw.rect(self.surface,self.color["exit_bar"],(1150,620,90,30))
		if 1150<=mouse[0]<=1240 and 620<=mouse[1]<=650:
			pygame.draw.rect(self.surface,self.color["exit_bar_hover"],(1150,620,90,30))
		temp_font=pygame.font.SysFont("Menlo, Consolas, DejaVu Sans Mono, monospace",17,bold=True,italic=False)
		object_temp_font=temp_font.render("Exit",False,self.color["white"])
		self.surface.blit(object_temp_font,(1170,625))
		if click[0]==1:
			if 1150<=mouse[0]<=1240 and 620<=mouse[1]<=650:
				return False
		return None
	def menu(self,message):
		play=True#
		continue_playing=False
		while play:
			self.surface.blit(self.images["theme_image"],(0,0))
			for event in pygame.event.get():
				if event.type==QUIT:
					pygame.quit()
					sys.exit()
				elif event.type==KEYDOWN:
					if event.key==K_TAB:
						play=False
			#-----
			continue_playing=self.draw_question_bar(message)
			if continue_playing==None:
				pass
			elif continue_playing:
				break
			else:
				break
			#-----
			pygame.display.update()
			ft.tick(fps)
		return continue_playing
	def run(self):
		play=True#
		while play:
			# print (self.color)
			self.surface.fill(self.color["garden"])
			self.surface.blit(self.images["background_image"],(self.x,self.y))
			for event in pygame.event.get():
				if event.type==QUIT:
					pygame.quit()
					sys.exit()
				elif event.type==KEYDOWN:
					if event.key==K_TAB:
						play=False
					elif event.key==K_RIGHT:
						self.move_session=["right",time.time()+self.time_last_to_move]
						self.avatar_facing_direction="right"
					elif event.key==K_LEFT:
						self.move_session=["left",time.time()+self.time_last_to_move]
						self.avatar_facing_direction="left"
					elif event.key==K_UP:
						self.move_session=["up",time.time()+self.time_last_to_move]
						self.avatar_facing_direction="up"
					elif event.key==K_DOWN:
						self.move_session=["down",time.time()+self.time_last_to_move]
						self.avatar_facing_direction="down"
					elif event.key==K_SPACE:
						self.move_session=[None,None]
					elif 49<=event.key<=53:
						self.trigger_powers(chr(event.key))
					elif event.key==K_F5:
						self.restart_position()
						# print (self.move_session)
						self.move_session=[None,None]
					elif event.key==K_LSHIFT or event.key==K_RSHIFT:
						# print ("shoot")
						self.move_session=[None,None]
						# print (self.avatar_facing_direction)
						self.bullet_gun_shots.append([[int(0-self.x+WIDTH//2),int(0-self.y+HEIGHT//2)],0,self.avatar_facing_direction])
			#-----
			tid1=threading.Thread(target=self.do_main_operations,args=())
			tid2=threading.Thread(target=self.play_musics,args=())
			tid1.start()
			tid2.start()
			tid1.join()
			tid2.join()
			remaining=self.count_remaining_enemies()
			# print (remaining)
			if remaining<=0:
				return True
			#-----
			pygame.display.update()
			ft.tick(fps)
		return False


if __name__=="__main__":
	my_game=game(surface=surface,images=images)
	message="Play"
	continue_playing=True
	while continue_playing:
		continue_playing=my_game.menu(message)
		if continue_playing:
			my_game=game(surface=surface,images=images)
			continue_playing=my_game.run()
		message="Play Again"


#----------------
