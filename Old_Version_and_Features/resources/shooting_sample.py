import pygame,sys,time,math
from pygame.locals import *

pygame.init()
WIDTH,HEIGHT=800,500
surface=pygame.display.set_mode((WIDTH,HEIGHT),0,32)
fps=100
ft=pygame.time.Clock()
pygame.display.set_caption('')
white=(255,255,255)
black=(0,0,0)
blue=(0,0,255)
plasma_color=(0,100,255)

def DDA_2D_line(x1,y1,x2,y2,point=[]):
	fx=x1;fy=y1;lx=x2;ly=y2
	dx=x2-x1;dy=y2-y1
	point.append([fx,fy])
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

# down, left, up, right

def main(plasma_color):
	player_pos=[400,250]
	direction="right"
	play=True
	radius=10
	bullets=[]
	angles_left=[]
	for angle in range(45,135):
		angles_left.append(angle)
	block=[480,260,500,300]
	block_border_points=[]
	block_border_points=DDA_2D_line(block[0],block[1],block[2],block[1],block_border_points)
	block_border_points=DDA_2D_line(block[0],block[1],block[0],block[3],block_border_points)
	block_border_points=DDA_2D_line(block[2],block[1],block[2],block[3],block_border_points)
	block_border_points=DDA_2D_line(block[0],block[3],block[2],block[3],block_border_points)
	while play:
		surface.fill(white)
		for event in pygame.event.get():
			if event.type==QUIT:
				pygame.quit()
				sys.exit()
			if event.type==KEYDOWN:
				if event.key==K_F10:
					play=False
				if event.key==K_RIGHT:
					direction,radius,bullets="right",10,[]
				if event.key==K_DOWN:
					direction,radius,bullets="down",10,[]
				if event.key==K_LEFT:
					direction,radius,bullets="left",10,[]
				if event.key==K_UP:
					direction,radius,bullets="up",10,[]
		#------work here------
		pygame.draw.circle(surface,blue,player_pos,10)
		pygame.draw.rect(surface,black,(block[0],block[1],block[2]-block[0],block[3]-block[1]))
		#pygame.draw.circle(surface,blue,point,5)
		for angle in angles_left:
			tar_point=[int(player_pos[0]+math.sin(math.radians(angle))*radius),int(player_pos[1]+math.cos(math.radians(angle))*radius)]
			pygame.draw.circle(surface,blue,tar_point,2)
		radius+=1
		#---------------------
		pygame.display.update()
		ft.tick(fps)

if __name__=="__main__":
	main(plasma_color)
