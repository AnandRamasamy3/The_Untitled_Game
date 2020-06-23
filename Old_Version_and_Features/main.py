import pygame,sys,time,math,threading,json
from pygame.locals import *
import sqlite3


mission_name="mission_anand_2019_sep_22_11_31_41"



# invisible 		for 10 seconds
# plasma gun
# ghost 			for 10 seconds		moves so fast
# open gate 		for 10 seconds
# trap bomb			trap or remote system
# crystal shield	360 degree round shield for 3 second
# light marker		marks location and shows to other team mates


# total map
# chats



pygame.init()
surface=pygame.display.set_mode((1250,660),0,32)
fps=200
ft=pygame.time.Clock()
pygame.display.set_caption('')
white=(255,255,255)
black=(0,0,0)
grass=(0,150,10)
teal=(0,60,60)
blue=(0,0,255)
red=(255,0,0)
yellow=(255,255,0)
dark_block=(0,40,40)
block_img=pygame.image.load("block_of_wall.jpg")
block_gate_img=pygame.image.load("block_of_gate_1.jpg")
avatar_img=pygame.image.load("avatar.jpg")
my_team_avatar=pygame.image.load("resources/my_team_avatar.png")
enemy_team_avatar=pygame.image.load("resources/enemy_team_avatar.png")

ghost_icon=pygame.image.load("resources/ghost_icon.png")
light_marker_icon=pygame.image.load("resources/light_marker_icon.png")
invisible_icon=pygame.image.load("resources/invisible_icon.png")
trap_bomb_icon=pygame.image.load("resources/trap_bomb_icon.png")
crystal_shield_icon=pygame.image.load("resources/crystal_shield_icon.png")

crystal_shield_avatar=pygame.image.load("resources/crystal_shield_avatar.png")
gate_button=pygame.image.load("resources/gate_button.jpeg")

#music=pygame.mixer.music.load("resources/theme_3.mp3")

app_font=pygame.font.SysFont('segoe print',17,bold=True,italic=False)
name_font=pygame.font.SysFont('calibri',17,bold=True,italic=False)
chat_font=pygame.font.SysFont('calibri',17,bold=False,italic=False)

def DDA_2D_line(x1,y1,x2,y2):
	fx=x1;fy=y1;lx=x2;ly=y2
	dx=x2-x1;dy=y2-y1
	point=[[fx,fy]]
	if dx>=dy:step=dx
	else:step=dy
	dx=dx//step
	dy=dy//step
	i=1
	while i<=step:
		fx+=dx
		fy+=dy
		point.append([fx,fy])
		i+=1
	return point

def check_crash(avatar,others,walls):
	if avatar[1][0]<=0 or avatar[1][1]<=0:
		return True
	my_avatar_position=[[avatar[1][0],avatar[1][1]],
					[avatar[1][0]+25,avatar[1][1]],
					[avatar[1][0]+25,avatar[1][1]+25],
					[avatar[1][0],avatar[1][1]+25]]
	for obj in others:
		for i in my_avatar_position:
			if obj[1][0]<=i[0]<=obj[1][0]+25 and obj[1][1]<=i[1]<=obj[1][1]+25:
				return True
	for obj in walls:
		for i in my_avatar_position:
			#pygame.draw.line(surface,grass,(obj[0],obj[1]),(obj[2],obj[3]))
			if obj[0]<i[0]<obj[2] and obj[1]<i[1]<obj[3]:
				return True
	return False

def get_walls(mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	cursor=conn.execute("SELECT * from walls;")
	walls=[]
	for row in cursor:
		# print (row)
		walls.append([[row[0],row[1]],[row[2],row[3]],row[4]])
	fobj=open("database.json","w")
	json.dump(walls,fobj)
	fobj.close()
	return walls

def get_gates(mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	cursor=conn.execute("SELECT * from gates;")
	gates=[]
	for row in cursor:
		gates.append([[row[0],row[1]],row[2],[row[3],row[4]],[row[5],row[6]],row[7]])
	return gates

def get_total_blocks(mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	blocks=[]
	cursor=conn.execute("SELECT * from total_blocks;")
	for row in cursor:
		blocks.append(row)
	return blocks
	'''if len(blocks)==0:
		for i in total_blocks:
			#print (len(total_blocks),total_blocks[0])
			cur.execute("INSERT into total_blocks values (?,?,?,?);",(i[0],i[1],i[2],i[3]))
			conn.commit()'''

def get_avatar(my_name,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	cursor=my_conn.execute("SELECT * from main_record;")
	avatars=[]
	my_avatar=[]
	for row in cursor:
		if row[0]==my_name:
			my_avatar=[row[0],[row[1],row[2]],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]]
		else:
			avatars.append([row[0],[row[1],row[2]],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17]])
	return my_avatar,avatars

def set_all_direction_to_null(avatar,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	my_cur.execute("UPDATE main_record set move=(?) where avatar_name=(?);",("False",avatar[0]))
	#cur.execute("UPDATE "+mission_name+" set position_x=(?) where avatar_name=(?);",(500,"anand"))
	#cur.execute("UPDATE "+mission_name+" set position_y=(?) where avatar_name=(?);",(300,"anand"))
	my_conn.commit()

def set_move(avatar,status,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	my_cur.execute("UPDATE main_record set move=(?) where avatar_name=(?);",(status,avatar[0]))
	my_conn.commit()

def move_avatar(avatar,others,direction,total_blocks,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	temp=[avatar[1][0],avatar[1][1]]
	speed=20
	#if avatar[6]=="yes":
	#	speed+=30
	#print (direction)
	if avatar[10]=="True":
		if direction=="right":
			avatar[1][0]+=speed
		if direction=="left":
			avatar[1][0]-=speed
		if direction=="up":
			avatar[1][1]-=speed
		if direction=="down":
			avatar[1][1]+=speed
		if check_crash(avatar,others,total_blocks) and (not is_active(avatar,7,5)):
			avatar[1][0],avatar[1][1]=temp[0],temp[1]
			#cursor=my_conn.execute("SELECT * from main_record;")
			#for row in cursor:
			#	if row[0]==avatar[0]:
			#		direction=row[6]
			#		break
		my_cur.execute("UPDATE main_record set position_x=(?) where avatar_name=(?);",(avatar[1][0],avatar[0]))
		my_cur.execute("UPDATE main_record set position_y=(?) where avatar_name=(?);",(avatar[1][1],avatar[0]))
		my_cur.execute("UPDATE main_record set direction=(?) where avatar_name=(?);",(direction,avatar[0]))
		my_conn.commit()
		#print (direction)

def draw_avatar(avatar,direction,avatar_img):
	image_to_be_pasted=avatar_img
	if is_active(avatar,8,2):
		image_to_be_pasted=crystal_shield_avatar
		#print ("ooops")
	if direction=="right":
		image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,270)
	elif direction=="down":
		image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,180)
	elif direction=="left":
		image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,90)
	elif direction=="up":
		image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,360)
	surface.blit(image_to_be_pasted,(500,360))
	#pygame.draw.rect(surface,grass,(avatar[0],avatar[1],25,25))

'''
if character[2]=="team_1":image_to_be_pasted=my_team_avatar
else:image_to_be_pasted=enemy_team_avatar
direction=character[5]
if direction=="right":
	image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,270)
elif direction=="down":
	image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,180)
elif direction=="left":
	image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,90)
elif direction=="up":
	image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,360)
surface.blit(image_to_be_pasted,(character[1][0]-(avatar[1][0]-500),character[1][1]-(avatar[1][1]-360)))
name_text=name_font.render(character[0],False,white)
surface.blit(name_text,(character[1][0]-(avatar[1][0]-500),character[1][1]-(avatar[1][1]-360+20)))
'''

def draw_others(others,avatar,my_team_avatar,enemy_team_avatar):
	for character in others:
		if not is_active(character,7,5):
			if character[2]=="team_1":
				image_to_be_pasted=my_team_avatar
				direction=character[5]
				#print ("my = ",direction)
				if direction=="right":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,270)
				elif direction=="down":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,180)
				elif direction=="left":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,90)
				elif direction=="up":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,360)
				surface.blit(image_to_be_pasted,(character[1][0]-(avatar[1][0]-500),character[1][1]-(avatar[1][1]-360)))
			elif character[2]=="team_2" and (not is_active(character,4,10)):
				image_to_be_pasted=enemy_team_avatar
				direction=character[5]
				#print ("enemy = ",direction)
				if direction=="right":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,270)
				elif direction=="down":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,180)
				elif direction=="left":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,90)
				elif direction=="up":
					image_to_be_pasted=pygame.transform.rotate(image_to_be_pasted,360)
				surface.blit(image_to_be_pasted,(character[1][0]-(avatar[1][0]-500),character[1][1]-(avatar[1][1]-360)))
				name_text=name_font.render(character[0],False,white)
				surface.blit(name_text,(character[1][0]-(avatar[1][0]-500),character[1][1]-(avatar[1][1]-360+20)))
			name_text=name_font.render(character[0],False,white)
			surface.blit(name_text,(character[1][0]-(avatar[1][0]-500),character[1][1]-(avatar[1][1]-360+20)))

def distance_between_points(p1,p2):
	return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))

def get_center_point(p1,p2):
	return [(p1[0]+p2[0])//2,(p1[1]+p2[1])//2]

def draw_walls(walls,avatar):
	#total_blocks=[]
	temp_walls=[]
	for i in range(len(walls)):
		temp_walls.append([[walls[i][0][0]-(avatar[1][0]-500),walls[i][0][1]-(avatar[1][1]-360)],[walls[i][1][0]-(avatar[1][0]-500),walls[i][1][1]-(avatar[1][1]-360)],walls[i][2]])
	for wall in temp_walls:
		if wall[2]=="TD":
			x=wall[0][0]-25
			init=wall[0][1]
			#total_blocks.append((x+(avatar[1][0]-500),init+(avatar[1][1]-360),x+(avatar[1][0]-500)+25,wall[1][1]+(avatar[1][1]-360)))
			#pygame.draw.line(surface,grass,(x+(avatar[1][0]-500),init+(avatar[1][1]-360)),(x+(avatar[1][0]-500)+25,wall[1][1]+(avatar[1][1]-360)),3)
			while init<wall[1][1]:
				#pygame.draw.rect(surface,dark_block,(x,init,25,24`),0)
				surface.blit(block_img,(x,init))
				#pygame.draw.rect(surface,white,(x,init,25,24),1)
				init+=25
		elif wall[2]=="SL":
			y=wall[0][1]-25
			init=wall[0][0]-25
			#total_blocks.append((init+(avatar[1][0]-500),y+(avatar[1][1]-360),wall[1][0]+(avatar[1][0]-500),y+(avatar[1][1]-360)+25))
			while init<wall[1][0]:
				#pygame.draw.rect(surface,dark_block,(init,y,24,25),0)
				surface.blit(block_img,(init,y))
				#pygame.draw.rect(surface,white,(init,y,24,25),1)
				init+=25
	#return total_blocks

def draw_gates(gates,avatar,total_blocks):
	for gate in gates:
		#pygame.draw.circle(surface,white,(gate[0][0]+30-(avatar[1][0]-500),gate[0][1]+30-(avatar[1][1]-360)),20)
		#pygame.draw.rect(surface,white,(gate[0][0]+30-(avatar[1][0]-500)-20,gate[0][1]+30-(avatar[1][1]-360)-20,50,50))
		surface.blit(gate_button,(gate[0][0]+30-(avatar[1][0]-500)-20,gate[0][1]+30-(avatar[1][1]-360)-20))
	#print (gates[0][0][0]-(avatar[1][1]-360),gates[0][0][1]-(avatar[1][1]-360))
	temp_walls=[]
	for i in range(len(gates)):
		if gates[i][1]=="no":
			temp_walls.append([[gates[i][2][0]-(avatar[1][0]-500),gates[i][2][1]-(avatar[1][1]-360)],[gates[i][3][0]-(avatar[1][0]-500),gates[i][3][1]-(avatar[1][1]-360)],gates[i][4]])
	for wall in temp_walls:
		if wall[2]=="TD":
			x=wall[0][0]-25
			init=wall[0][1]
			#total_blocks.append((x+(avatar[1][0]-500),init+(avatar[1][1]-360),x+(avatar[1][0]-500)+25,wall[1][1]+(avatar[1][1]-360)))
			while init<wall[1][1]:
				#pygame.draw.rect(surface,dark_block,(x,init,25,24),0)
				surface.blit(block_gate_img,(x,init))
				#pygame.draw.rect(surface,white,(x,init,25,24),1)
				init+=25
		elif wall[2]=="SL":
			y=wall[0][1]-25
			init=wall[0][0]-25
			#total_blocks.append((init+(avatar[1][0]-500),y+(avatar[1][1]-360),wall[1][0]+(avatar[1][0]-500),y+(avatar[1][1]-360)+25))
			while init<wall[1][0]:
				#pygame.draw.rect(surface,dark_block,(init,y,24,25),0)
				surface.blit(block_gate_img,(init,y))
				#pygame.draw.rect(surface,white,(init,y,24,25),1)
				init+=25
	#return total_blocks

def draw_miniature_map(avatar,others):
	me=[avatar[1][0],avatar[1][1]]
	my_team=avatar[2]
	pygame.draw.rect(surface,dark_block,(1000,0,250,150))
	pygame.draw.circle(surface,blue,(round(1000+((me[0]/5300)*250)),round((me[1]/4000)*150)),3)
	pygame.draw.circle(surface,blue,(round(1000+((me[0]/5300)*250)),round((me[1]/4000)*150)),10,1)
	# draw lights
	light_pos=[avatar[11],avatar[12]]
	if is_active(avatar,10,120):
		pygame.draw.circle(surface,yellow,(round(1000+((light_pos[0]/5300)*250)),round((light_pos[1]/4000)*150)),3)
	for person in others:
		light_pos=[person[11],person[12]]
		if is_active(person,10,120):
			pygame.draw.circle(surface,yellow,(round(1000+((light_pos[0]/5300)*250)),round((light_pos[1]/4000)*150)),3)
	# draw avatars
	for person in others:
		pos=[person[1][0],person[1][1]]
		if person[2]==my_team and (not is_active(person,7,5)):
			pygame.draw.circle(surface,blue,(round(1000+((pos[0]/5300)*250)),round((pos[1]/4000)*150)),3)
		else:
			#if person[3]=="no" and person[6]=="no":
			if (not is_active(person,4,10)) and (not is_active(person,7,5)):
				pygame.draw.circle(surface,red,(round(1000+((pos[0]/5300)*250)),round((pos[1]/4000)*150)),3)
	pygame.draw.rect(surface,white,(1000,0,250,150),1)

def draw_dock():
	pygame.draw.rect(surface,dark_block,(0,0,1000,60))
	apps_markers=["Light","Trap","Invis","Crys","Ghost"]
	#draw_x=300
	draw_x=275
	x=277
	for marker in apps_markers:
		#pygame.draw.circle(surface,white,(draw_x,30),25)
		pygame.draw.rect(surface,white,(draw_x,5,50,50))
		#print (marker,[draw_x,5,draw_x+50,50])
		app_icon=app_font.render(marker,False,dark_block)
		surface.blit(app_icon,(x,17))
		x+=80
		draw_x+=80
	surface.blit(light_marker_icon,(275,5))
	surface.blit(trap_bomb_icon,(355,5))
	surface.blit(invisible_icon,(435,5))
	surface.blit(crystal_shield_icon,(515,5))
	surface.blit(ghost_icon,(595,5))

def get_apt_message(message):
	result=[""]
	length=26
	message=message.split(" ",)
	while len(message)>0:
		if len(result[-1])<length:
			if (len(result[-1])+len(message[0]))<length:
				result[-1]+=" "+message[0]
				message.remove(message[0])
			elif len(result[-1])<(length/2):
				rem_length=length-len(result[-1])-1
				result[-1]+=" "+message[0][0:rem_length]
				message[0]=message[0].replace(message[0][0:rem_length],"")
			else:
				result.append("")
		else:
			result.append("")
	return result

def add_message_to_chat_app(avatar,message,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if message!="":
		my_cur.execute("INSERT into chat_app values (?,?,?);",(avatar[0],message,time.time()))
		my_conn.commit()

def draw_chat_app(avatar,new_message,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	message=[""]
	cursor=my_conn.execute("SELECT * from chat_app;")
	for row in cursor:
		if row[0]==avatar[0]:
			message.append("--- you -------")
		else:
			message.append("--- "+row[0]+" -------")
		temp=get_apt_message(row[1])
		for mess in temp:
			message.append(mess)
		message.append("")
	message.append("")
	temp=get_apt_message(new_message)
	for mess in temp:
		message.append(mess)
	#pos_y=650-len(message)*15
	pygame.draw.rect(surface,dark_block,(1000,150,250,560))
	#for mess in message:
	#	message_text=name_font.render(mess,False,white)
	#	surface.blit(message_text,(1010,pos_y))
	#	pos_y+=15
	pos_y=640
	ind=len(message)-1
	while pos_y>180 and ind>0:
		message_text=name_font.render(message[ind],False,white)
		surface.blit(message_text,(1010,pos_y))
		pos_y-=18
		ind-=1


'''
def get_current_time():
	temp_now=time.ctime()
	temp_now=temp_now.split(" ",)
	#print (temp_now)
	months={"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
	now=temp_now[5]+"-"+months[temp_now[1]]+"-"+temp_now[3]+" "+temp_now[4]
	now=now.replace("-","_")
	now=now.replace(" ","_")
	now=now.replace(":","_")
	return now
'''


def get_difference(func):
	#print (time.time(),int(func),time.time()-int(func))
	return time.time()-int(func)

def is_active(avatar,func,elapse_time):	# func = database index
	#print (func)
	data_time=avatar[func-1]
	#print (avatar,func)
	diff=get_difference(data_time)
	#print (diff)
	if diff<=elapse_time:
		return True
	return False

def is_activatable(avatar,func,elapse_time,waiting_time):	# func = database index
	if is_active(avatar,func,elapse_time):
		return False
	data_time=avatar[func-1]
	#print (data_time)
	diff=get_difference(data_time)
	#print (diff)
	if diff<(elapse_time+waiting_time):
		return False
	return True

def timer_for_apps(avatar,pos,x,elapse_time,waiting_time):
	timer=time.time()-avatar[pos]
	if timer<=elapse_time:
		elapse_percentage=timer/elapse_time
		pygame.draw.rect(surface,white,(int(x),50,50,5))
		pygame.draw.rect(surface,teal,(int(x),50,int(50*elapse_percentage),5))
		#print ("ooops----------------------")
	if timer>elapse_time:
		if (timer-elapse_time)<=waiting_time:
			waiting_percentage=(timer-elapse_time)/waiting_time
			pygame.draw.rect(surface,white,(int(x),50,50,5))
			pygame.draw.rect(surface,red,(int(x),50,50*int(waiting_percentage),5))

def trap_bomb(avatar,mission_name,activate=False):#data=9 avatar=8 elapse_time=120 waiting_time=60
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if activate==True:
		if is_activatable(avatar,9,120,60):
			my_cur.execute("UPDATE main_record set trap_bomb=(?) where avatar_name=(?);",(time.time(),avatar[0]))
			my_cur.execute("UPDATE main_record set trap_x=(?) and trap_y=(?) where avatar_name=(?);",(avatar[1][0],avatar[1][1],avatar[0]))
			my_conn.commit()
		else:
			if is_active(avatar,9,120):
				#print ("bomb blasted")		# data=17 avatar=16 elapse_time=10 waiting_time=10
				my_cur.execute("UPDATE main_record set trap_is_active=(?) where avatar_name=(?);",(time.time(),avatar[0]))
				pass
	timer_for_apps(avatar,8,355,120,60)
	#print (elapse_percentage,waiting_percentage)

def light_marker(avatar,mission_name,activate=False):#data=10 avatar=9 elapse_time=120 waiting_time=10
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if activate==True:
		if is_activatable(avatar,10,120,10):
			my_cur.execute("UPDATE main_record set light_marker=(?) where avatar_name=(?);",(time.time(),avatar[0]))
			my_cur.execute("UPDATE main_record set light_x=(?) where avatar_name=(?);",(avatar[1][0],avatar[0]))
			my_cur.execute("UPDATE main_record set light_y=(?) where avatar_name=(?);",(avatar[1][1],avatar[0]))
			my_conn.commit()
		else:
			if is_active(avatar,10,120):
				#print ("light marked")		# data=16 avatar=15 elapse_time=10 waiting_time=10
				#my_cur.execute("UPDATE main_record set light_is_active=(?) where avatar_name=(?);",(time.time(),avatar[0]))
				pass
	if is_activatable(avatar,10,120,10):
		my_cur.execute("UPDATE main_record set light_is_active=(?) where avatar_name=(?);",("False",avatar[0]))
		my_conn.commit()
	timer_for_apps(avatar,9,275,120,10)

def invisible(avatar,mission_name,activate=False):#data=4 avatar=3 elapse_time=10 waiting_time=10
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if activate==True:
		if is_activatable(avatar,4,10,10):
			my_cur.execute("UPDATE main_record set invisible=(?) where avatar_name=(?);",(time.time(),avatar[0]))
			my_conn.commit()
	timer_for_apps(avatar,3,435,10,10)

def crystal_shield(avatar,mission_name,activate=False):#data=8 avatar=7 elapse_time=2 waiting_time=2
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if activate==True:
		if is_activatable(avatar,8,2,2):
			my_cur.execute("UPDATE main_record set crystal_shield=(?) where avatar_name=(?);",(time.time(),avatar[0]))
			my_conn.commit()
	timer_for_apps(avatar,7,515,2,2)

def ghost(avatar,mission_name,activate=False):#data=7 avatar=6 elapse_time=5 waiting_time=240
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if activate==True:
		if is_activatable(avatar,7,5,240):
			my_cur.execute("UPDATE main_record set ghost=(?) where avatar_name=(?);",(time.time(),avatar[0]))
			my_conn.commit()
	timer_for_apps(avatar,6,595,5,240)


def click_buttons(mouse,click,avatar):
	#print (click)  (left,___,right)
	x,y,cl=mouse[0],mouse[1],click[0]
	if 5<=y<=50 and cl==1:
		if 275<=x<=325:
			light_marker(avatar,True)
			#print ("light_marker")
		if 355<=x<=405:
			trap_bomb(avatar,True)
			#print ("trap_bomb")
		if 435<=x<=485:
			invisible(avatar,True)
			#print ("invisible")
		if 515<=x<=565:
			crystal_shield(avatar,True)
			#print ("crystal_shield")
		if 595<=x<=645:
			ghost(avatar,True)
			#print ("ghost")

def shoot(avatar,direction,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	if direction=="null" or direction=="pause":direction="up"
	my_cur.execute("INSERT into plasma_radiation values (?,?,?,?,?);",(avatar[2],avatar[1][0]+12,avatar[1][1]+12,direction,time.time()))
	my_conn.commit()

def is_shooting_active(avatar,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	cursor=my_conn.execute("SELECT * from plasma_radiation;")
	for row in cursor:
		distance=int((time.time())*100-(row[4])*100)
		if distance<=100:
			return True
	return False

def draw_pixel_of_plasma(row,avatar,angle,distance):
	plasma_color=(0,100,255)
	point=[int(row[1]+math.sin(math.radians(angle))*distance/10)-(avatar[1][0]-500),int(row[2]+math.cos(math.radians(angle))*distance/10)-(avatar[1][1]-360)]
	surface.set_at(point,plasma_color)
	point=[int(row[1]+math.sin(math.radians(angle))*distance/5)-(avatar[1][0]-500),int(row[2]+math.cos(math.radians(angle))*distance/5)-(avatar[1][1]-360)]
	surface.set_at(point,plasma_color)
	point=[int(row[1]+math.sin(math.radians(angle))*distance/2)-(avatar[1][0]-500),int(row[2]+math.cos(math.radians(angle))*distance/2)-(avatar[1][1]-360)]
	surface.set_at(point,plasma_color)
	point=[int(row[1]+math.sin(math.radians(angle))*distance)-(avatar[1][0]-500),int(row[2]+math.cos(math.radians(angle))*distance)-(avatar[1][1]-360)]
	surface.set_at(point,plasma_color)

def plasma_gun(avatar,others,mission_name):
	conn=sqlite3.connect('master_data.db')
	my_conn=sqlite3.connect(mission_name+'.db')
	cur=conn.cursor()
	my_cur=my_conn.cursor()
	cursor=my_conn.execute("SELECT * from plasma_radiation;")
	for row in cursor:
		distance=int((time.time())*1000-(row[4])*1000)
		if distance<=300:
			if row[3]=="up":
				for angle in range(135,226):
					draw_pixel_of_plasma(row,avatar,angle,distance)
			elif row[3]=="right":
				for angle in range(45,136):
					draw_pixel_of_plasma(row,avatar,angle,distance)
			elif row[3]=="down":
				for angle in range(315,360):
					draw_pixel_of_plasma(row,avatar,angle,distance)
				for angle in range(1,46):
					draw_pixel_of_plasma(row,avatar,angle,distance)
			elif row[3]=="left":
				for angle in range(225,316):
					draw_pixel_of_plasma(row,avatar,angle,distance)
		else:
			my_cur.execute("DELETE from plasma_radiation where source_point_x=(?) and source_point_y=(?);",(row[1],row[2]))
			my_conn.commit()

def do_display_operations(avatar,others,direction,walls,gates,total_blocks,mission_name):#
	draw_walls(walls,avatar)
	draw_gates(gates,avatar,total_blocks)
	#set_total_blocks(total_blocks,mission_name)
	mouse=pygame.mouse.get_pos()
	click=pygame.mouse.get_pressed()
	plasma_gun(avatar,others,mission_name)
	click_buttons(mouse,click,avatar)
	#print (message)
	#print (mouse)
	if is_shooting_active(avatar,mission_name):
		set_move(avatar,"False",mission_name)
	move_avatar(avatar,others,direction,total_blocks,mission_name)
	ghost(avatar,mission_name)
	trap_bomb(avatar,mission_name)
	invisible(avatar,mission_name)
	#crystal_shield(mission_name,avatar,activate=True)
	crystal_shield(avatar,mission_name)
	light_marker(avatar,mission_name)

def play_musics():
	#a
    pass
	#if(pygame.mixer.music.get_busy()==1):
	#	pygame.mixer.music.unpause()
	#elif(pygame.mixer.music.get_busy()==0):
	#	pygame.mixer.music.play()
	#pygame.mixer.music.set_volume(0.6)

def home(my_name,avatar_img,mission_name):
	play=True#
	walls=get_walls(mission_name)
	gates=get_gates(mission_name)
	total_blocks=get_total_blocks(mission_name)
	avatar,others=get_avatar(my_name,mission_name)
	#for i in gates:
	#	print (i)
	message=""
	direction=avatar[5]
	while play:
		surface.fill(teal)
		avatar,others=get_avatar(my_name,mission_name)
		#print (direction)
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()
			if event.type==KEYDOWN:
				if event.key==K_F10:
					play=False
				if event.key==K_BACKSPACE:
					if len(message)>0:
						message=message[0:-1]
				if event.key==K_a:
					message+="a"
				if event.key==K_b:
					message+="b"
				if event.key==K_c:
					message+="c"
				if event.key==K_d:
					message+="d"
				if event.key==K_e:
					message+="e"
				if event.key==K_f:
					message+="f"
				if event.key==K_g:
					message+="g"
				if event.key==K_h:
					message+="h"
				if event.key==K_i:
					message+="i"
				if event.key==K_j:
					message+="j"
				if event.key==K_k:
					message+="k"
				if event.key==K_l:
					message+="l"
				if event.key==K_m:
					message+="m"
				if event.key==K_n:
					message+="n"
				if event.key==K_o:
					message+="o"
				if event.key==K_p:
					message+="p"
				if event.key==K_q:
					message+="q"
				if event.key==K_r:
					message+="r"
				if event.key==K_s:
					message+="s"
				if event.key==K_t:
					message+="t"
				if event.key==K_u:
					message+="u"
				if event.key==K_v:
					message+="v"
				if event.key==K_w:
					message+="w"
				if event.key==K_x:
					message+="x"
				if event.key==K_y:
					message+="y"
				if event.key==K_z:
					message+="z"
				if event.key==K_0:
					message+="0"
				if event.key==K_1:
					message+="1"
				if event.key==K_2:
					message+="2"
				if event.key==K_3:
					message+="3"
				if event.key==K_4:
					message+="4"
				if event.key==K_5:
					message+="5"
				if event.key==K_6:
					message+="6"
				if event.key==K_7:
					message+="7"
				if event.key==K_8:
					message+="8"
				if event.key==K_9:
					message+="9"
				if event.key==K_F1:
					light_marker(avatar,mission_name,True)
				if event.key==K_F2:
					trap_bomb(avatar,mission_name,True)
				if event.key==K_F3:
					invisible(avatar,mission_name,True)
				if event.key==K_F4:
					crystal_shield(avatar,mission_name,True)
				if event.key==K_F5:
					ghost(avatar,mission_name,True)
				if event.key==K_RETURN:
					add_message_to_chat_app(avatar,message)
					message=""
				if event.key==K_RIGHT:
					set_move(avatar,"True",mission_name)
					direction="right"
				if event.key==K_LEFT:
					set_move(avatar,"True",mission_name)
					direction="left"
				if event.key==K_UP:
					set_move(avatar,"True",mission_name)
					direction="up"
				if event.key==K_DOWN:
					set_move(avatar,"True",mission_name)
					direction="down"
				if event.key==K_SPACE:
					set_move(avatar,"False",mission_name)
					message+=" "
				if event.key==K_RCTRL or event.key==K_LCTRL:
					if not is_active(avatar,7,5):shoot(avatar,direction,mission_name)
		#-----
		tid1=threading.Thread(target=do_display_operations,args=(avatar,others,direction,walls,gates,total_blocks,mission_name))
		tid2=threading.Thread(target=play_musics,args=())
		tid3=threading.Thread(target=draw_avatar,args=(avatar,direction,avatar_img))
		tid4=threading.Thread(target=draw_dock,args=())
		tid5=threading.Thread(target=draw_others,args=(others,avatar,my_team_avatar,enemy_team_avatar))
		tid6=threading.Thread(target=draw_chat_app,args=(avatar,message,mission_name))
		tid7=threading.Thread(target=draw_miniature_map,args=(avatar,others))
		tid1.start()
		tid2.start()
		tid3.start()
		tid4.start()
		tid5.start()
		tid6.start()
		tid7.start()
		tid1.join()
		tid2.join()
		tid3.join()
		tid4.join()
		tid5.join()
		tid6.join()
		tid7.join()
		#temp=check_a_point_inside_a_circle(300,30,25,mouse[0],mouse[1])
		#print (avatar)
		#for i in others:
		#	print (i)
		#print ("\n\n")
		'''
		avatar=['anand', [1840, 3600], 'team_1', 1570105126.55345, 'yes', 'null', 1570105126.55345, 1570106587.0638835, 1570105126.55345, 1570106532.1752808]
		others=[
			['ram', [1300, 700], 'team_1', 1570105126.55345, 'yes', 'null', 1570105126.55345, 1570105126.55345, 1570105126.55345, 1570105126.55345]
			['alien_x', [400, 1500], 'team_2', 1570105126.55345, 'yes', 'null', 1570105126.55345, 1570105126.55345, 1570105126.55345, 1570105126.55345]
		]
		'''
		#print (is_active(avatar,7,5))
		#-----
		pygame.display.update()
		ft.tick(fps)
	set_move(avatar,"False",mission_name)


my_name="anand"

if __name__=="__main__":
	home(my_name,avatar_img,mission_name)











#----------------
