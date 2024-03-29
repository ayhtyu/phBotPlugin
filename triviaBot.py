from phBot import *
from threading import Timer
from random import randrange
import os
import phBotChat
import QtBind

pName = 'triviaBot'
pVersion = '0.1.8'
pUrl = 'https://raw.githubusercontent.com/ayhtyu/phBotPlugin/master/triviaBot.py'

#######################################################################
server = "pearl" 						# pearl,xeon				  #
qafolder = "triviaBot" 					# Subfolder of Plugins folder #
qafile = "triviaBot.txt" 				# Place of saved Q & A file   #
qacache = "cache.txt"					# if character cannot joined  #
answertime = [3,9]						# Random interval to answer	  #
#######################################################################

# if folder and files doesn't exists
path = os.getcwd()
if not os.path.exists(path+"/Plugins/"+server+"_"+qafolder+"/"):
    os.makedirs(path+"/Plugins/"+server+"_"+qafolder+"/")
open("Plugins/"+server+"_"+qafolder+"/"+qafile, 'a+').close()

# clear qacache file
open("Plugins/"+server+"_"+qafolder+"/"+qacache, 'w').close()

# GUI
gui = QtBind.init(__name__, pName)
QtBind.createLabel(gui, 'triviaBot is automatically answers trivia event questions and automatically adds new questions.', 10, 10)
QtBind.createLabel(gui, 'Questions List', 11, 38)
QtBind.createButton(gui, 'gui_qlist', '   Refresh List   ', 448, 35)
QtBind.createButton(gui, 'gui_answer', '   Selected Question\'s Answer    ', 534, 35)
QtBind.createLabel(gui, 'Added Questions:', 587, 255)
qlist = QtBind.createList(gui, 10, 55, 680, 190)
qnumber = QtBind.createLabel(gui, '0', 680, 255)
qanswer = QtBind.createLabel(gui, 'Answer: ', 11, 255)

# its need to avoid conflict
def joined_game():
	global qacache
	qacache = get_character_data()['name']+"_cache.txt"
	open("Plugins/"+server+"_"+qafolder+"/"+qacache, 'w').close()
	return False

def gui_qlist():
	a = 0
	while True:
		if a == get_qa('l',0):
			break
		b = get_qa("q",a)
		if not gui_check_qlist(b):
			QtBind.append(gui,qlist,b)
		a += 1
	return False

# [a] value is a question, need check for data added to list
def gui_check_qlist(a):
	b = QtBind.getItems(gui,qlist)
	for i in range(len(b)):
		if b[i].lower() == a.lower():
			return True
	return False

def gui_answer():	
	selectedItem = QtBind.text(gui,qlist)
	a = 0
	if selectedItem == "":
		QtBind.setText(gui, qanswer,"Answer: Choose a question!")
	else:
		while True:
			if a == get_qa('l',0):
				QtBind.setText(gui, qanswer,"Error: Please check [Plugins/"+qafolder+"/"+qafile+"] file!")
				break
			else:
				if get_qa('q',a) == selectedItem:
					QtBind.setText(gui, qanswer,"Answer: "+get_qa('a',a))
					break
				a += 1
	return False

# value of [a]: q(question), a(answer), l(lenght), all for array
# value of [b]: row number
# value of [c]: 0 for any questions, 1 for country questions, 2 need for adding qacache to qafile
def get_qa(a,b,c=0):
	qdosya = "Plugins/"+server+"_"+qafolder+"/"+qafile
	ayrac = "--"
	if c == 2: 
		qdosya = "Plugins/"+server+"_"+qafolder+"/"+qacache
		ayrac = "--"
	qlen = 0
	qarray = []
	with open(qdosya) as f:
		for line in f:
			inner_list = [elt.strip() for elt in line.split(ayrac)]
			qarray.append(inner_list)
		qlen = len(qarray)
	f.close()
	if a == "q":
		return qarray[b][0]
	elif a == "a":
		return qarray[b][1]
	elif a == "l":
		return qlen
	elif a == "all":
		return qarray

# adds qacache rows to qafile rows
def add_newq():
	a = 0
	b = 0
	while True:
		if get_qa("l",0,2) == a:
			if b == 0:
				log("triviaBot: Not found new question.")
			else:
				log("triviaBot: "+ str(b) + " question(s) automatically added.")
			break
		else:
			if get_qa("q",a,2) not in str(get_qa("all",0)):
				if get_qa("a",a,2) != "":
					file = open("Plugins/"+server+"_"+qafolder+"/"+qafile,"a")
					file.write('--\n'+get_qa("q",a,2)+'--'+get_qa("a",a,2))
					file.close()
					QtBind.append(gui,qlist,get_qa("q",a,2))
					log("triviaBot: "+ get_qa("q",a,2) + " automatically added to list.")
					QtBind.setText(gui, qnumber,str(int(QtBind.text(gui,qnumber)) + 1))
					b += 1		
		a += 1

# saving questions to qacache
def save_q2_cache(a):
	# this is need for if you press the reload plugins button
	global qacache
	qacache = get_character_data()['name']+"_cache.txt"
	file = open("Plugins/"+server+"_"+qafolder+"/"+qacache,"a")
	if server == "pearl":
		if "Silks" in a:
			s = a.find('wrote') + 7
			e = a.find('won', s) - 6
			answer = a[s:e]
			file.write(answer)
		elif "Nobody" in a and "correct" in a and "answer" in a:
			file.write(a[63:-2])
		else:
			file.write('--\n'+a+'--')
	elif server == "xeon":
		if "winner of this round" not in a and "Correct answer" not in a:
			file.write('--\n'+a+'--')
		elif "Correct answer" in a:
			s = a.find('was') + 5
			answer = a[s:-1]
			file.write(answer)		
	file.close()
	return False

def handle_chat(t, player, msg):
	if t == 6: # global message
		if server == "pearl":
			if player == "[BOT]Events":
				a = 0
				while True:
					if a == get_qa('l',0):
						save_q2_cache(msg) # save question if dont know
						Timer(randrange(30,80), add_newq, ()).start() # automatically add questions to qafile and gui list
						break
					else:
						if get_qa('q',a) == msg:
							reply = get_qa('a',a)
							Timer(randrange(answertime[0],answertime[1]), phBotChat.Private, (player,reply)).start()
							log("triviaBot: ["+msg+"] question replied as ["+reply+"]")
							break
						a += 1
		elif server == "xeon":
			if player == "[BOT]" and "winner of this round" not in msg and "no winner for this" not in msg:
				a = 0
				while True:
					if a == get_qa('l',0):
						save_q2_cache(msg) # save question if dont know
						Timer(randrange(30,80), add_newq, ()).start() # automatically add questions to qafile and gui list
						break
					else:
						if get_qa('q',a) == msg:
							reply = get_qa('a',a)
							Timer(randrange(answertime[0],answertime[1]), phBotChat.Private, (player,reply)).start()
							log("triviaBot: ["+msg+"] question replied as ["+reply+"]")
							break
						a += 1

log("Plugin: triviaBot v"+pVersion+" plugin successfully loaded.")
#gui_qlist()
