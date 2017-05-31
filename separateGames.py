import pandas as pd
import numpy as np
import os
import pickle

#Take in the master csv, and separate it into csv by game
def separateGames():

	data = pd.read_csv("pbp.csv")

	prevID = data["game_id"][0]
	first = True

	for row in data.itertuples():
		if(first==True):
			arr = np.array(list(row)[1:])
			print(arr)
			first=False
		elif(row.game_id == prevID):
			nextRow = list(row)[1:]
			print(nextRow)
			arr = np.vstack([arr, nextRow])

		else:
			filename = str(prevID) + '.csv'
			df = pd.DataFrame(data=arr, columns=list(data))
			df.to_csv('games/'+filename, index=False)
			
			arr = np.array(list(row)[1:])
			print(arr)

		prevID = row.game_id


def getScores(score):
	index = score.index('-')
	home = int(score[0 : index-1])
	away = int(score[index+2 : ])
	return home, away

def getTime(clock):
	index = clock.index(':')
	minutes = int(clock[0:index])
	seconds = int(clock[index+1:])
	return minutes*60 + seconds


def updateArray(arr, clock, score_diff, increment):
	if clock >= 540:
		arr[0] += increment
	elif clock < 540 and clock >= 360:
		arr[1] += increment
	elif clock < 360 and clock >= 180 and score_diff > 9:
		arr[2] += increment
	elif clock < 360 and clock >=180 and score_diff <= 9:
		arr[3] += increment
	elif clock < 180 and clock >=60 and score_diff > 7:
		arr[4] += increment
	elif clock < 180 and clock >=60 and score_diff <= 7:
		arr[5] += increment
	elif clock < 60 and score_diff > 5:
		arr[6] += increment
	elif clock < 60 and score_diff <= 5:
		arr[7] += increment

	return arr


def getExpectedPPP():

	possessions = [0]*8
	points = [0]*8
	for file in os.listdir("games/"):
		print(file)
		data = pd.read_csv("games/" + file)
		prev_home, prev_away = getScores(data.irow(0).score)
		prev_score = prev_home + prev_away
		prev_clock = 720
		for i in range(1, len(data)):
			row = data.irow(i)
			clock = getTime(row.play_clock)

			if str(row.score) != 'nan':
				new_home, new_away = getScores(row.score)
				new_score = new_home + new_away
				points = updateArray(points, clock, abs(new_home - new_away), new_score-prev_score)

				prev_home = new_home
				prev_away = new_away
				prev_score = new_score

			if "Made Shot" in row.event_type or ("Rebound" in row.event_type and "Normal" not in row.event_description) or \
				("Turnover" in row.event_type and prev_clock != clock) or "Free Throw 2 of 2" in str(row.event_description) or \
				"Free Throw 3 of 3" in str(row.event_description) or "End Period" in str(row.event_type):
				possessions = updateArray(possessions, clock, abs(prev_home-prev_away), 1)

			prev_clock = clock

			

	for p in range(0,8):
		print(str(points[p]) + " --- " + str(possessions[p]) + " --- " + str(points[p]/possessions[p]))



def getTimeoutPPP():

	timeouts = 0
	timeoutPoints = 0
	for file in os.listdir("games/"):
		print(file)
		data = pd.read_csv("games/" + file)
		
		for i in range(0, len(data)):
			row = data.iloc[i]

			if str(row.score) != 'nan':
				prev_home, prev_away = getScores(row.score)
				prev_score = prev_home + prev_away

			if("Timeout" in str(row.event_type)):
				new_home, new_away = prev_home, prev_away
				new_score = new_home + new_away
				timeouts += 1
				print("Timeouts: " + str(timeouts))
				print("timeoutPoints: " + str(timeoutPoints))
				n = i+1
				nxt = data.iloc[n]
				while True:
					if str(data.iloc[n].score) != 'nan':
						new_home, new_away = getScores(data.iloc[n].score)
						new_score = new_home + new_away

					if 'Made Shot' in nxt.event_type or 'Free Throw 2 of 2' in str(nxt.event_description) \
						or 'Free Throw 3 of 3' in str(nxt.event_description):
						timeoutPoints += new_score - prev_score
						prev_home = new_home
						prev_away = new_away
						prev_score = new_score
						break
					elif 'Missed Shot' in nxt.event_type or 'Turnover' in nxt.event_type or 'End Period' in nxt.event_type:
						break
					n += 1
					nxt = data.iloc[n]

	print(timeouts)
	print(timeoutPoints)


def getGameNames():
# Get teams playing the game
	games = []
	for file in os.listdir("games/"):
		df = pd.read_csv("games/" + file)
		homeName = ''
		awayName = ''
		for i in range(0, len(df)):
			row = df.iloc[i]
			if str(row.home_description) != 'nan' and str(row.player1_team) != 'nan':
				homeName = str(row.player1_team)
			if str(row.home_description) == 'nan' and str(row.away_description) != 'nan' and str(row.player1_team) != 'nan':
				awayName = str(row.player1_team)
			if str(row.home_description) != 'nan' and str(row.away_description) != 'nan':
				homeName = str(row.player1_team)
				if str(row.player2_team) != 'nan':
					awayName = str(row.player2_team)
				else:
					awayName = str(row.player3_team)

			if len(homeName) != 0 and len(awayName) != 0:
				games.append(homeName + '-' + awayName + " (" + file + ")")
				break

	games.sort()
	print(games)
	with open('game_names.pkl', 'wb') as f:
		pickle.dump(games, f, protocol=2)


getGameNames()
# getTimeoutPPP()
# getExpectedPPP()
# separateGames()