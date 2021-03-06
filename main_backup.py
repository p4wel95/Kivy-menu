#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import threading
import os
os.environ['KIVY_GL_BACKEND'] = 'sdl2'
os.environ['KIVY_VIDEO'] = 'gstplayer'

from configparser import ConfigParser

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, TransitionBase, NoTransition
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config
from random import randint
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.image import AsyncImage
from kivy.uix.switch import Switch
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.videoplayer import VideoPlayer
from kivy.graphics import Color
from kivy.graphics import Line

RoAPin = 11    # pin11
RoBPin = 12    # pin12
RoSPin = 13    # pin13
PrePin = 10  # pin10

counter = 0

clickFlag = 0  # zmienna pomocnicza do klikniecia encoderem
flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0
stop = 0 # zmiana tego na 1 spowoduje zatrzymanie watku zajmujacego sie skanowaniem encodera

files = [] # lista plikow w folderze galeria
path = os.path.dirname(os.path.realpath(__file__))+'/galeria' # sciezka do folderu galeria
for r,d,f in os.walk(path):
	for file in f:
		files.append(os.path.join(r,file)) # dodanie plikow do files[]
files = sorted(files) # sortowanie zdjec w files[] alfabetycznie
fileslen=len(files) # ile zdjec w file[]
currentpic=0 #aktualnie wyswietlane zdjecie w galeri

def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(RoAPin, GPIO.IN)    # input mode
	GPIO.setup(RoBPin, GPIO.IN)
	GPIO.setup(PrePin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def rotaryDeal(*args):
	while True:
		time.sleep(0.01)
		global clickFlag
		global flag
		global stop
		global Last_RoB_Status
		global Current_RoB_Status
		global counter
		Last_RoB_Status = GPIO.input(RoBPin)
		while (not GPIO.input(RoAPin)):
			Current_RoB_Status = GPIO.input(RoBPin)
			flag = 1
		if flag == 1:
			flag = 0
			if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
				counter = counter + 1
				print("counter : ", counter)
			if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
				counter = counter - 1
				print("counter : ", counter)
		if stop==1: # konczy petle a nastepnie ten watek
			break

		# po puszczeniu przycisku encodera odpala sie zke.click():
		if GPIO.input(RoSPin) == 0:
			time.sleep(0.1)
			clickFlag = 1
		if GPIO.input(RoSPin) == 1 and clickFlag == 1:
			time.sleep(0.1)
			clickFlag = 0
			zke.click()

setup()
t = threading.Thread(target=rotaryDeal, name='thread1') # utworzenie watku od encodera
t.start() # start watku od encodera


class ZaznaczanieKlikanieEncoderem(): # metody wywolywane przez ruchy encoderem:

	def __init__(self):
		self.aktywny_ekran = 'main1' # ekran na ktory ma oddzialywac encoder, main1 to menu po lewej stronie ekranu glownego
		self.n = 0 # liczba elementow na ekranie na ktory ma oddzialywac encoder

	def click(self,*args): # ta metoda odpala sie po odpuszczeniu przycisku encodera
		global counter
		global stop
		global currentpic
		global fileslen
		global files
		if self.aktywny_ekran == 'main1':
			self.n = 6
			if counter % self.n == 0:
				self.aktywny_ekran = 'main2' # main2 to prawa czesc ekranu glownego
				counter = 0
				mainWindow.button1.opacity = 0
				mainWindow.switch1_backimage.opacity = 1
				return True
			if counter % self.n == 1:
				self.aktywny_ekran = 'second'
				sm.current = 'second'
				mainWindow.button2.opacity = 0
				counter = 0
				Clock.schedule_interval(secondWindow.chart, 0.5) # odpala odswiezanie wykresu co 0.5 sek
				return True
			if counter % self.n == 2:
				self.aktywny_ekran = 'third'
				sm.current = 'third'
				mainWindow.button3.opacity = 0
				counter = 0
				#tworzy widget Video do odtwarzania filmu:
				thirdWindow.videoplayerfloatlayout.add_widget(Video(source='bunny.mp4', pos_hint={"x": 0, "y": 0}, size_hint=(1, 1),state='play'))
				return True
			if counter % self.n == 3:
				self.aktywny_ekran = 'fourth'
				sm.current = 'fourth'
				# wyswietla widget galeri
				fourthWindow.galeria = AsyncImage(source=files[0], pos_hint={"x": 0, "y": 0}, size_hint=(1, 1),nocache = True)
				fourthWindow.imagefloatlayout.add_widget(fourthWindow.galeria)
				currentpic=0
				mainWindow.button4.opacity = 0
				counter = 0
				return True
			if counter % self.n == 4:
				self.aktywny_ekran = 'fifth'
				sm.current = 'fifth'
				mainWindow.button5.opacity = 0
				counter = 0
				# co 0.1sek odpala metode do obslugi strzalek na ekranie 5:
				Clock.schedule_interval(fifthWindow.hold, 0.1)
				return True
			if counter % self.n == 5:
				self.aktywny_ekran = 'sixth'
				sm.current = 'sixth'
				mainWindow.button6.opacity = 0
				counter = 0
				sixthWindow.anim = AsyncImage(source='bobpng.zip', pos_hint={"x": 0, "y": 0.1}, size_hint=(1, 0.9),nocache = True)
				sixthWindow.anim.anim_delay = 0.05
				sixthWindow.floatlayout.add_widget(sixthWindow.anim)
				return True

		if self.aktywny_ekran == 'main2':
			self.n = 8

			if counter % self.n == 0:
				if mainWindow.switch1.active == False:
					mainWindow.switch1.active = True
				else:
					mainWindow.switch1.active = False
				return True
			if counter % self.n == 1:
				if mainWindow.switch2.active == False:
					mainWindow.switch2.active = True
				else:
					mainWindow.switch2.active = False
				return True
			if counter % self.n == 2:
				if mainWindow.switch3.active == False:
					mainWindow.switch3.active = True
				else:
					mainWindow.switch3.active = False
				return True
			if counter % self.n == 3:
				if mainWindow.switch4.active == False:
					mainWindow.switch4.active = True
				else:
					mainWindow.switch4.active = False
				return True
			if counter % self.n == 4:
				if mainWindow.switch5.active == False:
					mainWindow.switch5.active = True
				else:
					mainWindow.switch5.active = False
				return True
			if counter % self.n == 5:
				if mainWindow.switch6.active == False:
					mainWindow.switch6.active = True
				else:
					mainWindow.switch6.active = False
				return True
			if counter % self.n == 6:
				self.aktywny_ekran = 'main1'
				counter = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.button1.opacity = 1
				return True
			if counter % self.n == 7:
				saveConfig()
				return True

		if self.aktywny_ekran == 'second':
			self.n = 5
			if counter % self.n == 0:
				Clock.unschedule(secondWindow.chart) # zatrzymuje odswiezanie wykresu
				self.aktywny_ekran = 'main1'
				sm.current = 'main'
				counter = 0
				return True
			if counter % self.n == 1:
				self.aktywny_ekran = 'secondWindowSlider1'
				secondWindow.slider1.img1.opacity = 0
				secondWindow.slider1.img2.opacity = 1
				counter = secondWindow.slider1.slider.value
				return True
			if counter % self.n == 2:
				self.aktywny_ekran = 'secondWindowSlider2'
				secondWindow.slider2.img1.opacity = 0
				secondWindow.slider2.img2.opacity = 1
				counter = secondWindow.slider2.slider.value
				return True
			if counter % self.n == 3:
				self.aktywny_ekran = 'secondWindowSlider3'
				secondWindow.slider3.img1.opacity = 0
				secondWindow.slider3.img2.opacity = 1
				counter = secondWindow.slider3.slider.value
				return True
			if counter % self.n == 4:
				self.aktywny_ekran = 'secondWindowSlider4'
				secondWindow.slider4.img1.opacity = 0
				secondWindow.slider4.img2.opacity = 1
				counter = secondWindow.slider4.slider.value
				return True

		if self.aktywny_ekran == 'secondWindowSlider1':
			self.aktywny_ekran = 'second'
			secondWindow.slider1.img1.opacity = 1
			secondWindow.slider1.img2.opacity = 0
			counter = 1
			return True
		if self.aktywny_ekran == 'secondWindowSlider2':
			self.aktywny_ekran = 'second'
			secondWindow.slider2.img1.opacity = 1
			secondWindow.slider2.img2.opacity = 0
			counter = 2
			return True
		if self.aktywny_ekran == 'secondWindowSlider3':
			self.aktywny_ekran = 'second'
			secondWindow.slider3.img1.opacity = 1
			secondWindow.slider3.img2.opacity = 0
			counter = 3
			return True
		if self.aktywny_ekran == 'secondWindowSlider4':
			self.aktywny_ekran = 'second'
			secondWindow.slider4.img1.opacity = 1
			secondWindow.slider4.img2.opacity = 0
			counter = 4
			return True

		if self.aktywny_ekran == 'third':
			thirdWindow.videoplayerfloatlayout.clear_widgets() #usuwa widget wyswietlajacy film
			self.aktywny_ekran = 'main1'
			counter = 0
			sm.current = 'main'
			return True

		if self.aktywny_ekran == 'fourth':
			self.n = 3
			if counter % self.n == 0:
				fourthWindow.imagefloatlayout.remove_widget(fourthWindow.galeria) #usuwa widget wyswietlajacy zdjecie
				fourthWindow.galeria = ObjectProperty(None)
				self.aktywny_ekran = 'main1'
				counter = 0
				sm.current = 'main'
				return True
			if counter % self.n == 1:
				if currentpic == 0:
					fourthWindow.galeria.source = files[fileslen-1]
					currentpic=fileslen-1
				else:
					fourthWindow.galeria.source = files[currentpic-1]
					currentpic -= 1
				return True
			if counter % self.n == 2:
				if currentpic == fileslen-1:
					fourthWindow.galeria.source = files[0]
					currentpic = 0
				else:
					fourthWindow.galeria.source = files[currentpic+1]
					currentpic += 1
				return True

		if self.aktywny_ekran == 'fifth':
			self.n = 5
			if counter % self.n == 0:
				Clock.unschedule(fifthWindow.hold) # anuluje odpalanie funckji od strzalek na ekranie 5
				self.aktywny_ekran = 'main1'
				counter = 0
				sm.current = 'main'
				return True
			if counter % self.n == 0:
				return True
			if counter % self.n == 0:
				return True
			if counter % self.n == 0:
				return True
			if counter % self.n == 0:
				return True
			return True

		if self.aktywny_ekran == 'sixth':
			self.n = 1
			if counter % self.n == 0:
				sixthWindow.floatlayout.remove_widget(sixthWindow.anim)
				sixthWindow.anim = ObjectProperty(None)
				self.aktywny_ekran = 'main1'
				counter = 0
				sm.current = 'main'
				return True

	def update(self,*args):  # aktualizuje zaznaczone elementy
		global counter
		if self.aktywny_ekran == 'main1':
			if counter % 6 == 0:
				mainWindow.button1.opacity = 1
				mainWindow.button2.opacity = 0
				mainWindow.button3.opacity = 0
				mainWindow.button4.opacity = 0
				mainWindow.button5.opacity = 0
				mainWindow.button6.opacity = 0
				return True
			if counter % 6 == 1:
				mainWindow.button1.opacity = 0
				mainWindow.button2.opacity = 1
				mainWindow.button3.opacity = 0
				mainWindow.button4.opacity = 0
				mainWindow.button5.opacity = 0
				mainWindow.button6.opacity = 0
				return True
			if counter % 6 == 2:
				mainWindow.button1.opacity = 0
				mainWindow.button2.opacity = 0
				mainWindow.button3.opacity = 1
				mainWindow.button4.opacity = 0
				mainWindow.button5.opacity = 0
				mainWindow.button6.opacity = 0
				return True
			if counter % 6 == 3:
				mainWindow.button1.opacity = 0
				mainWindow.button2.opacity = 0
				mainWindow.button3.opacity = 0
				mainWindow.button4.opacity = 1
				mainWindow.button5.opacity = 0
				mainWindow.button6.opacity = 0
				return True
			if counter % 6 == 4:
				mainWindow.button1.opacity = 0
				mainWindow.button2.opacity = 0
				mainWindow.button3.opacity = 0
				mainWindow.button4.opacity = 0
				mainWindow.button5.opacity = 1
				mainWindow.button6.opacity = 0
				return True
			if counter % 6 == 5:
				mainWindow.button1.opacity = 0
				mainWindow.button2.opacity = 0
				mainWindow.button3.opacity = 0
				mainWindow.button4.opacity = 0
				mainWindow.button5.opacity = 0
				mainWindow.button6.opacity = 1
				return True
			return True

		if self.aktywny_ekran == 'main2':
			self.n = 8
			if counter % self.n == 0:
				mainWindow.switch1_backimage.opacity = 1
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 1:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 1
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 2:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 1
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 3:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 1
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 4:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 1
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 5:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 1
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 6:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 1
				mainWindow.btn_saveconfig.img2.opacity = 0
				return True
			if counter % self.n == 7:
				mainWindow.switch1_backimage.opacity = 0
				mainWindow.switch2_backimage.opacity = 0
				mainWindow.switch3_backimage.opacity = 0
				mainWindow.switch4_backimage.opacity = 0
				mainWindow.switch5_backimage.opacity = 0
				mainWindow.switch6_backimage.opacity = 0
				mainWindow.btn_goback.img2.opacity = 0
				mainWindow.btn_saveconfig.img2.opacity = 1
				return True
			return True

		if self.aktywny_ekran == 'second':
			if counter % 5 == 0:
				secondWindow.button1.opacity = 1
				secondWindow.slider1.img1.opacity = 0
				secondWindow.slider2.img1.opacity = 0
				secondWindow.slider3.img1.opacity = 0
				secondWindow.slider4.img1.opacity = 0
				return True
			if counter % 5 == 1:
				secondWindow.button1.opacity = 0
				secondWindow.slider1.img1.opacity = 1
				secondWindow.slider2.img1.opacity = 0
				secondWindow.slider3.img1.opacity = 0
				secondWindow.slider4.img1.opacity = 0
				return True
			if counter % 5 == 2:
				secondWindow.button1.opacity = 0
				secondWindow.slider1.img1.opacity = 0
				secondWindow.slider2.img1.opacity = 1
				secondWindow.slider3.img1.opacity = 0
				secondWindow.slider4.img1.opacity = 0
				return True
			if counter % 5 == 3:
				secondWindow.button1.opacity = 0
				secondWindow.slider1.img1.opacity = 0
				secondWindow.slider2.img1.opacity = 0
				secondWindow.slider3.img1.opacity = 1
				secondWindow.slider4.img1.opacity = 0
				return True
			if counter % 5 == 4:
				secondWindow.button1.opacity = 0
				secondWindow.slider1.img1.opacity = 0
				secondWindow.slider2.img1.opacity = 0
				secondWindow.slider3.img1.opacity = 0
				secondWindow.slider4.img1.opacity = 1
				return True
			return True

		# zmiana wartosci sliderow za pomoca krecenia encoderem
		if self.aktywny_ekran == 'secondWindowSlider1':
			if counter < 0: counter = 0
			if counter > 100: counter = 100
			secondWindow.slider1.slider.value = counter
			return True
		if self.aktywny_ekran == 'secondWindowSlider2':
			if counter < 0: counter = 0
			if counter > 100: counter = 100
			secondWindow.slider2.slider.value = counter
			return True
		if self.aktywny_ekran == 'secondWindowSlider3':
			if counter < 0: counter = 0
			if counter > 100: counter = 100
			secondWindow.slider3.slider.value = counter
			return True
		if self.aktywny_ekran == 'secondWindowSlider4':
			if counter < 0: counter = 0
			if counter > 100: counter = 100
			secondWindow.slider4.slider.value = counter
			return True


		if self.aktywny_ekran == 'third':
			if counter % 1 == 0:
				thirdWindow.button1.opacity = 1
			return True

		if self.aktywny_ekran == 'fourth':
			if counter % 3 == 0:
				fourthWindow.btn_goback.opacity = 1
				fourthWindow.btn_prevpic.opacity = 0
				fourthWindow.btn_nextpic.opacity = 0
				return True
			if counter % 3 == 1:
				fourthWindow.btn_goback.opacity = 0
				fourthWindow.btn_prevpic.opacity = 1
				fourthWindow.btn_nextpic.opacity = 0
				return True
			if counter % 3 == 2:
				fourthWindow.btn_goback.opacity = 0
				fourthWindow.btn_prevpic.opacity = 0
				fourthWindow.btn_nextpic.opacity = 1
				return True
			return True

		if self.aktywny_ekran == 'fifth':
			if counter % 5 == 0:
				fifthWindow.btn_goback.opacity = 1
				fifthWindow.btn_up_tlo1.opacity = 0
				fifthWindow.btn_left_tlo1.opacity = 0
				fifthWindow.btn_right_tlo1.opacity = 0
				fifthWindow.btn_down_tlo1.opacity = 0
				return True
			if counter % 5 == 1:
				fifthWindow.btn_goback.opacity = 0
				fifthWindow.btn_up_tlo1.opacity = 1
				fifthWindow.btn_left_tlo1.opacity = 0
				fifthWindow.btn_right_tlo1.opacity = 0
				fifthWindow.btn_down_tlo1.opacity = 0
				return True
			if counter % 5 == 2:
				fifthWindow.btn_goback.opacity = 0
				fifthWindow.btn_up_tlo1.opacity = 0
				fifthWindow.btn_left_tlo1.opacity = 1
				fifthWindow.btn_right_tlo1.opacity = 0
				fifthWindow.btn_down_tlo1.opacity = 0
				return True
			if counter % 5 == 3:
				fifthWindow.btn_goback.opacity = 0
				fifthWindow.btn_up_tlo1.opacity = 0
				fifthWindow.btn_left_tlo1.opacity = 0
				fifthWindow.btn_right_tlo1.opacity = 0
				fifthWindow.btn_down_tlo1.opacity = 1
				return True
			if counter % 5 == 4:
				fifthWindow.btn_goback.opacity = 0
				fifthWindow.btn_up_tlo1.opacity = 0
				fifthWindow.btn_left_tlo1.opacity = 0
				fifthWindow.btn_right_tlo1.opacity = 1
				fifthWindow.btn_down_tlo1.opacity = 0
				return True
			return True

		if self.aktywny_ekran == 'sixth':
			self.n = 1
			if counter & self.n == 0:
				sixthWindow.btn_goback.img2.opacity = 1

	# Przycisk zlozony z 2 zdjec i napisu na srodku, 1 zdj - przycisk nie zaznaczony, 2 zdj - przycisc zaznaczony
class CustomButton(FloatLayout):
	def __init__(self,poshint,sizehint,labeltext='button'):
		super(CustomButton, self).__init__()
		self.pos_hint=poshint
		self.size_hint=sizehint
		self.img1 = Image(pos_hint = {"x":0, "y": 0},size_hint =(1,1),source='button_normal.png',allow_stretch=True)
		self.img2 = Image(pos_hint = {"x":0, "y": 0},size_hint =(1,1),source='button_down.png',allow_stretch=True,opacity=0)
		self.label = Label(pos_hint = {"x":0, "y": 0},size_hint =(1,1),text=labeltext)
		self.add_widget(self.img1)
		self.add_widget(self.img2)
		self.add_widget(self.label)

# custom slider zlozony z slidera, 2 zdjec i napisu nad nim
class CustomSlider(FloatLayout):
	def __init__(self,poshint,sizehint,labeltext='slider'):
		super(CustomSlider, self).__init__()
		self.pos_hint =poshint
		self.size_hint = sizehint
		self.labeltext=labeltext
		self.slider = Slider(pos_hint = {"x":0, "y": 0},size_hint =(1,0.5),min= 0, max = 100,value = 40)
		self.label = Label(pos_hint={"x": 0, "y": 0.5}, size_hint=(1, 0.5), text=labeltext+' = '+str(self.slider.value))
		self.img1 = Image(pos_hint = {"x":0, "y": 0},size_hint =(1,1),source='tlo.png',allow_stretch=True,keep_ratio=False,opacity=0)
		self.img2 = Image(pos_hint = {"x":0, "y": 0},size_hint =(1,1),source='tlo_down.png',allow_stretch=True,keep_ratio=False,opacity=0)
		self.add_widget(self.img1)
		self.add_widget(self.img2)
		self.add_widget(self.slider)
		self.add_widget(self.label)
		self.slider.bind(value=self.valueUpdate) # zmiana wartosci slidera automatycznie odpala funkcje valueUpdate()

	def valueUpdate(self,b,c):
		self.label.text = self.labeltext+' = '+str(c)


class MainWindow(Screen):
	button1 = ObjectProperty(None)
	button2 = ObjectProperty(None)
	button3 = ObjectProperty(None)
	button4 = ObjectProperty(None)
	button5 = ObjectProperty(None)
	button6 = ObjectProperty(None)

	switch1 = ObjectProperty(None)
	switch2 = ObjectProperty(None)
	switch3 = ObjectProperty(None)
	switch4 = ObjectProperty(None)
	switch5 = ObjectProperty(None)
	switch6 = ObjectProperty(None)
	switch1_label = ObjectProperty(None)
	switch2_label = ObjectProperty(None)
	switch3_label = ObjectProperty(None)
	switch4_label = ObjectProperty(None)
	switch5_label = ObjectProperty(None)
	switch6_label = ObjectProperty(None)
	switch1_backimage = ObjectProperty(None)
	switch2_backimage = ObjectProperty(None)
	switch3_backimage = ObjectProperty(None)
	switch4_backimage = ObjectProperty(None)
	switch5_backimage = ObjectProperty(None)
	switch6_backimage = ObjectProperty(None)

	floatlayout3 = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(MainWindow, self).__init__(**kwargs)

		# bindowanie zmiany wartosci switchow do funkcji
		# zmiana stanu switcha odpala automatycznie funkcje switch1_callback
		self.switch1.bind(active=self.switch1_callback)
		self.switch2.bind(active=self.switch2_callback)
		self.switch3.bind(active=self.switch3_callback)
		self.switch4.bind(active=self.switch4_callback)
		self.switch5.bind(active=self.switch5_callback)
		self.switch6.bind(active=self.switch6_callback)

		# utworzenie przycisku save config:
		self.btn_saveconfig = CustomButton(poshint={"x":0.75, "y": 0.02},sizehint=(0.2,0.1),labeltext='save config')
		# dodanie go do layouta
		self.floatlayout3.add_widget(self.btn_saveconfig)

		self.btn_goback = CustomButton(poshint={"x": 0.5, "y": 0.02}, sizehint=(0.2, 0.1), labeltext='go back')
		self.floatlayout3.add_widget(self.btn_goback)

	# Funkcje odpalanie przy zmianie stanu switchy
	def switch1_callback(self,a,value):
		print('the switch', self, 'is', value)
	def switch2_callback(self,a,value):
		print('the switch', self, 'is', value)
	def switch3_callback(self,a,value):
		print('the switch', self, 'is', value)
	def switch4_callback(self,a,value):
		print('the switch', self, 'is', value)
	def switch5_callback(self,a,value):
		print('the switch', self, 'is', value)
	def switch6_callback(self,a,value):
		print('the switch', self, 'is', value)

class SecondWindow(Screen):
	floatlayout1 = ObjectProperty(None)
	button1 = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(SecondWindow, self).__init__(**kwargs)
		self.slider1 = CustomSlider(poshint={"x":0.5, "y": 0.8},sizehint=(0.5,0.15),labeltext='slider 1')
		self.slider2 = CustomSlider(poshint={"x": 0.5, "y": 0.6}, sizehint=(0.5, 0.15))
		self.slider3 = CustomSlider(poshint={"x": 0.5, "y": 0.4}, sizehint=(0.5, 0.15))
		self.slider4 = CustomSlider(poshint={"x": 0.5, "y": 0.2}, sizehint=(0.5, 0.15))
		self.floatlayout1.add_widget(self.slider1)
		self.floatlayout1.add_widget(self.slider2)
		self.floatlayout1.add_widget(self.slider3)
		self.floatlayout1.add_widget(self.slider4)

		# napisy przy wykresie:
		self.floatlayout1.add_widget(Label(pos=(0,255), size_hint=(0.05, 0.05), text='0'))
		self.floatlayout1.add_widget(Label(pos=(0, 450), size_hint=(0.05, 0.05), text='100'))
		self.floatlayout1.add_widget(Label(pos=(30, 220), size_hint=(0.05, 0.05), text='-25s'))
		self.floatlayout1.add_widget(Label(pos=(380, 220), size_hint=(0.05, 0.05), text='0s'))
		self.floatlayout1.add_widget(Label(pos=(150, 220), size_hint=(0.05, 0.05), text='slider 1 chart'))

		# lista points zawiera punkty lini wykresu [x1,y1,x2,y2,x3,y3 ... ]
		# x sa stale, y sa aktualizowanie
		self.points = []
		for i in range(0, 50):
			self.points.append(50+i * 7)
			self.points.append(270)

		# osie wykresu
		self.canvas.add(Color(1, 1, 0))
		self.canvas.add(Line(points=[48, 250,48,260,400,260,400,250,400,260,48,260,48,270,40,270,48,270, 48, 470, 40, 470], width=2))

		# linia wykresu
		self.canvas.add(Color(1, 0, 0))
		self.line = Line(points=self.points,width=2)
		self.canvas.add(self.line)


	# funkcja aktualizujaca linie wykresu
	def chart(self,*args):
		# przesunie sie wartosci y w lewo
		for i in range (1,99,2):
			self.points[i]=self.points[i+2]

		#dodanie nowej wartosci y na koniec listy
		self.points[99]=int(self.slider1.slider.value)*2+270
		self.canvas.remove(self.line) # usuniecie linie
		self.line = Line(points=self.points,width=2) # utworzenie nowej linie
		self.canvas.add(self.line) # wyswietlenie lini


class ThirdWindow(Screen):
	floatlayout1 = ObjectProperty(None)
	videoplayerfloatlayout = ObjectProperty(None)
	button1 = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(ThirdWindow, self).__init__(**kwargs)


class FourthWindow(Screen):
	floatlayout1 = ObjectProperty(None)
	imagefloatlayout = ObjectProperty(None)
	btn_goback = ObjectProperty(None)
	btn_prevpic = ObjectProperty(None)
	btn_nextpic = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(FourthWindow, self).__init__(**kwargs)
		self.galeria = ObjectProperty(None)

		#self.galeria = AsyncImage(source=files[0], pos_hint={"x": 0, "y": 0}, size_hint=(1, 1))
		#self.imagefloatlayout.add_widget(self.galeria)


class FifthWindow(Screen):
	btn_goback=ObjectProperty(None)

	btn_up_tlo1=ObjectProperty(None)
	btn_up_tlo2=ObjectProperty(None)
	btn_left_tlo1=ObjectProperty(None)
	btn_left_tlo2=ObjectProperty(None)
	btn_right_tlo1=ObjectProperty(None)
	btn_right_tlo2=ObjectProperty(None)
	btn_down_tlo1=ObjectProperty(None)
	btn_down_tlo2=ObjectProperty(None)

	img_ball = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(FifthWindow, self).__init__(**kwargs)

	# przesuwanie obrazka strzalkami
	def hold(self,*args):
		global counter
		self.btn_up_tlo2.opacity = 0
		self.btn_left_tlo2.opacity = 0
		self.btn_right_tlo2.opacity = 0
		self.btn_down_tlo2.opacity = 0
		if counter % 5 == 1:
			if GPIO.input(RoSPin) == 0:
				self.img_ball.pos[1]+=10
				self.btn_up_tlo2.opacity = 1
			return True
		if counter % 5 == 2:
			if GPIO.input(RoSPin) == 0:
				self.img_ball.pos[0]-=10
				self.btn_left_tlo2.opacity = 1
			return True
		if counter % 5 == 3:
			if GPIO.input(RoSPin) == 0:
				self.img_ball.pos[1]-=10
				self.btn_down_tlo2.opacity = 1
			return True
		if counter % 5 == 4:
			if GPIO.input(RoSPin) == 0:
				self.img_ball.pos[0]+=10
				self.btn_right_tlo2.opacity = 1
			return True

class SixthWindow(Screen):
	floatlayout = ObjectProperty(None)
	def __init__(self, **kwargs):
		super(SixthWindow, self).__init__(**kwargs)

		self.btn_goback = CustomButton(poshint={"x": 0.05, "y": 0}, sizehint=(0.2, 0.1), labeltext='go back')
		self.floatlayout.add_widget(self.btn_goback)

		self.anim = ObjectProperty(None)


# zapis ustawien do pliku config.ini
label = Label(pos_hint = {"x":0.75, "y": 0.12},size_hint =(0.2,0.1),text='SAVED')
saveConfigAllow = 1
def saveConfig():
	global label
	global saveConfigAllow
	if saveConfigAllow == 1:
		saveConfigAllow = 0
		config = ConfigParser()
		config['settings'] = {
			'switch1': mainWindow.switch1.active,
			'switch2': mainWindow.switch2.active,
			'switch3': mainWindow.switch3.active,
			'switch4': mainWindow.switch4.active,
			'switch5': mainWindow.switch5.active,
			'switch6': mainWindow.switch6.active,
			'slider1': secondWindow.slider1.slider.value,
			'slider2': secondWindow.slider2.slider.value,
			'slider3': secondWindow.slider3.slider.value,
			'slider4': secondWindow.slider4.slider.value,
			'img_ballposx': fifthWindow.img_ball.pos[0],
			'img_ballposy': fifthWindow.img_ball.pos[1],
		}
		with open('config.ini', 'w') as f:
			config.write(f)
		mainWindow.floatlayout3.add_widget(label)
		Clock.schedule_once(removelabel, 3)
def removelabel(*args):
	global label
	global saveConfigAllow
	mainWindow.floatlayout3.remove_widget(label)
	saveConfigAllow = 1


# zaladowanie pliku kv
kv = Builder.load_file("kiwi.kv")

sm = ScreenManager(transition=NoTransition())

mainWindow = MainWindow(name='main')
secondWindow = SecondWindow(name='second')
thirdWindow = ThirdWindow(name='third')
fourthWindow = FourthWindow(name='fourth')
fifthWindow = FifthWindow(name='fifth')
sixthWindow = SixthWindow(name='sixth')

sm.add_widget(mainWindow)
sm.add_widget(secondWindow)
sm.add_widget(thirdWindow)
sm.add_widget(fourthWindow)
sm.add_widget(fifthWindow)
sm.add_widget(sixthWindow)

sm.current = 'main'

zke = ZaznaczanieKlikanieEncoderem()

class MyApp(App):
	# funkcja wywoluwana przy starcie aplikacji laduje ustawienia
	def on_start(self):
		config = ConfigParser()
		config.read('config.ini')
		mainWindow.switch1.active = config.getboolean('settings','switch1',fallback=False)
		mainWindow.switch2.active = config.getboolean('settings', 'switch2',fallback=False)
		mainWindow.switch3.active = config.getboolean('settings', 'switch3',fallback=False)
		mainWindow.switch4.active = config.getboolean('settings', 'switch4',fallback=False)
		mainWindow.switch5.active = config.getboolean('settings', 'switch5',fallback=False)
		mainWindow.switch6.active = config.getboolean('settings', 'switch6',fallback=False)
		secondWindow.slider1.slider.value = config.getint('settings', 'slider1',fallback=50)
		secondWindow.slider2.slider.value = config.getint('settings', 'slider2',fallback=50)
		secondWindow.slider3.slider.value = config.getint('settings', 'slider3',fallback=50)
		secondWindow.slider4.slider.value = config.getint('settings', 'slider4',fallback=50)
		fifthWindow.img_ball.pos = (config.getint('settings', 'img_ballposx',fallback=400),config.getint('settings', 'img_ballposy',fallback=240))

	# funkcja wywolywana przy zatrzymaniu aplikacji
	def on_stop(self):
		global stop
		print("stop : ",stop)
		print("on stop called")
		stop = 1 # zatrzymanie petli od encodera
		print("stop : ", stop)

	def build(self):
		Clock.schedule_interval(zke.update, 0.1) # wywoluje funkcje zke.update co 0.1s
		return sm

if __name__ == "__main__":
	MyApp().run()

t.join() # zakonczenie watku od encodera