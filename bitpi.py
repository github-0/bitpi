"""

Loads Bitcoin and Ethereum values from Bitstamp.net API and presents them on the PiTFT 2.8" TFT 320x240 Capacitive Touchscreen (but works on other screens as well). 

"""

# -*- coding: utf-8 -*-

import json, requests
import pygame
import os
from time import sleep
import time
from timeout import timeout
from requests.exceptions import ConnectionError

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((320, 240))
screen.fill((0,0,0))
pygame.display.update()

btc = "https://www.bitstamp.net/api/ticker"
eth = "https://www.bitstamp.net/api/v2/ticker/ethusd"

WHITE = (255,255,255)
RED = (255,0,0)
L_RED = (200,0,0)
GREEN = (0,255,0)
L_GREEN = (0,180,0)

def epochtodatetime(epoch): #convert epoch to local time
	conv = time.strftime('%H:%M:%S', time.localtime(epoch))
	return conv

@timeout(5) #to prevent 6min timeout with exception "OpenSSL.SSL.ZeroReturnError" which happens every now and then, don't know why
def ticker(addr): #get data from Bitstamp HTTP API
	url = requests.get(addr)
	get = json.loads(url.text) 
	value = get['last']
	volume_str = get['volume']
	volume_float = float(volume_str)
	volume_int = int(volume_float)
	volume = str(volume_int)
	high = get['high']
	low = get['low']
	timestamp_epoch = float(get['timestamp'])
	timestamp = epochtodatetime(timestamp_epoch)
	open = get['open']
	dchange = (float(value) - float(open)) / float(open) * 100
	return (value, volume, high, low, timestamp, dchange)


def drawtext(text, size, color, x, y):
	try:
		font = pygame.font.SysFont(None, size)
		text_surface = font.render(text, True, color)
		rect = text_surface.get_rect(center=(x,y))
		screen.blit(text_surface, rect)
	except:
		print "Text draw error"
def drawtext_inst(text, size, color, x, y):
	try:
		font = pygame.font.SysFont(None, size)
		text_surface = font.render(text, True, color)
		rect = text_surface.get_rect(center=(x,y))
		screen.fill((0,0,0), rect)
		screen.blit(text_surface, rect)
		pygame.display.update(rect)
	except:
		print "Text draw error"

debugger = 1
last_value_btc = 0
last_value_eth = 0
last_color_btc = "L_GREEN"
last_color_eth = "L_GREEN"
btc_eth = "eth"
start_time = time.time()

while True:
	try:
		if time.time() - start_time > 14:
			if btc_eth == "btc": 
				btc_eth = "eth"
			else:
				btc_eth = "btc"
			start_time = time.time()
			
		screen.fill((0,0,0))
		if btc_eth == "btc": 
			value_btc, volume, high, low, timestamp, dchange = ticker(btc)
			screen.blit(pygame.image.load('/home/pi/bitcoin.png'),(0,0))
			if dchange < -5.00 or dchange > 5.00: pygame.draw.lines(screen, (255,140,0), False, [(60,0), (320,0), (320,240), (0,240), (0,65)], 18)
		else:
			value_eth, volume, high, low, timestamp, dchange = ticker(eth)
			screen.blit(pygame.image.load('/home/pi/ethereum.png'),(0,0))
			if dchange < -5.00 or dchange > 5.00: pygame.draw.lines(screen, (220,220,255), False, [(60,0), (320,0), (320,240), (0,240), (0,65)], 18)

		drawtext("@" +timestamp, 40, WHITE, 160, 42)

		drawtext("Volume", 30, WHITE, 70, 185)
		drawtext(volume, 40, WHITE, 70, 212)
		
		drawtext("Change", 30, WHITE, 230, 185)
		if dchange < 0:
			drawtext(" " + str(round(dchange,2)) + "% ", 40, L_RED, 232, 212)
		else:
			drawtext(" " + str(round(dchange,2)) + "% ", 40, L_GREEN, 232, 212)
		
		drawtext(low + " - " + high, 30, WHITE, 160, 150)

		if debugger == 1:
			debugger_p = pygame.draw.circle(screen, WHITE, (231,42), 2, 0)
			debugger_p
			debugger = 0
		else:
			screen.fill((0,0,0), debugger_p)
			debugger = 1
		pygame.display.update()
		
		if btc_eth == "btc":
			if value_btc == last_value_btc:
				drawtext(value_btc, 110, last_color_btc, 160, 100)
			elif value_btc < last_value_btc:
				drawtext_inst(value_btc, 110, RED, 160, 100)
				sleep(0.1)
				drawtext(value_btc, 110, L_RED, 160, 100)
				last_color_btc = L_RED
			else:
				drawtext_inst(value_btc, 110, GREEN, 160, 100)
				sleep(0.1)
				drawtext(value_btc, 110, L_GREEN, 160, 100)
				last_color_btc = L_GREEN
			last_value_btc = value_btc
		else:
			if value_eth == last_value_eth:
				drawtext(value_eth, 110, last_color_eth, 160, 100)
			elif value_eth < last_value_eth:
				drawtext_inst(value_eth, 110, RED, 160, 100)
				sleep(0.1)
				drawtext(value_eth, 110, L_RED, 160, 100)
				last_color_eth = L_RED
			else:
				drawtext_inst(value_eth, 110, GREEN, 160, 100)
				sleep(0.1)
				drawtext(value_eth, 110, L_GREEN, 160, 100)
				last_color_eth = L_GREEN
			last_value_eth = value_eth
			
		last_value_eth = value_eth
		pygame.display.update()
		print "OK @ " + time.strftime("%H:%M:%S")
		sleep(5)
	except KeyboardInterrupt:
		raise
	except ConnectionError:
		print "Connection error @ " + time.strftime("%H:%M:%S")
		screen.fill((255,0,0))
		font = pygame.font.SysFont(None, 30)
		text_surface = font.render("CONNECTION ERROR", True, WHITE)
		rect = text_surface.get_rect(center=(160,120))
		screen.blit(text_surface, rect)
		pygame.display.update()
		sleep(5)
	except:
		print "Unspecified Exception @ " + time.strftime("%H:%M:%S")
		import traceback, sys
		traceback.print_exc(file=sys.stdout)
		sleep(1)
