github_api = 'https://api.github.com'

##########################################################################

import requests
import json
import getpass
import csv
from datetime import date, timedelta, timezone, datetime
import matplotlib.pyplot as plt
from urllib.parse import urljoin



def main():
	print("\n#### DELIGHT TEST - STAGE DATA ENGINEER ####\n")

	## authentification
	headers =  {'Authorization': 'token %s' % getToken()}
	
	## programme

	# mise en page #
	input("Press 'enter' to download contributors...")
	print("\n")
	##

	list_contributors = downloadContributors(headers)

	##
	input("Press 'enter' to monitor commits...")
	print("\n")
	##

	commitsMonitoring(headers)

	##
	input("Press 'enter' to visualize contibutions per contributors...")
	print("\n")
	##

	contributionsVisualizer(headers,list_contributors)

	##
	input("Press 'enter' to show contributors global activity...")
	print("\n")
	##

	globalActivity(headers, list_contributors)

	## fin


######

def getToken():
	### on s'identifie avec un token pour ne pas avoir de limite de requêtes (60 sur Github)

	print('# Already got a Github authentification token ? (Y/N)')

	while True:
		token_available = input('Answer: ')
		if token_available == 'Y' or token_available == 'N':
			break
		else:
			print("# Value error : please enter a valid answer (Y/N)")

	if token_available == "Y":
		while True:
			token = input('Insert token here: ')

			# requête
			headers =  {'Authorization': 'token %s' % token}
			res = requests.get(
				github_api,
				headers = headers
				)

			#parse
			j = json.loads(res.text)

			# check erreurs
			if res.status_code >= 400:
				msg = j.get('message', 'UNDEFINED ERROR (no error description from server)')
				print('ERROR:', msg)
			else:
				break

		print('# This token is valid.')
		return token

	else:
		while True:
			# entrées des identifiants
			username = input('Github username: ')
			password = getpass.getpass('Github password (hidden): ')

			# rajout d'une note pour le token
			note = input('Note (write anything): ')

			# requête
			url = urljoin(github_api, 'authorizations')
			payload = {}
			if note:
				payload['note'] = note
			res = requests.post(
				url,
				auth = (username, password),
				data = json.dumps(payload),
				)

			# parse
			j = json.loads(res.text)

			# check erreurs
			if res.status_code >= 400:
				msg = j.get('message', 'UNDEFINED ERROR (no error description from server)')
				print('ERROR:', msg)
			else:
				break

		# reception token
		token = j['token']
		print('New token (copy it for another run): ', token)
		return token

######

def downloadContributors(headers):
	###Télécharger et formater les données des contributeurs (incluant contributeurs anonymes).

	print("# Downloading contributors...")
	stop = 0
	i = 1
	while stop != 1:

		# requête
		url_download_contributors = urljoin(github_api, "/repos/facebook/react/contributors")
		res = requests.get(
			url_download_contributors,
			params = {'page': i ,'anon': True}, # 'anon : True' pour afficher les contributeurs anonymes
			headers = headers
			)

		# si il ne reste plus de contributeurs à télécharger
		if res.text == "[]":
			stop = 1

		else:
			if i == 1:
				# premier parse
				current_j = json.loads(res.text)
			else:
				# on parse et on rajoute aux contributeurs déjà collectés
				j = json.loads(res.text)
				current_j = current_j + j

		# on change de page
		i += 1

		# indicateur progression
		count = len(current_j)
		print(str(count), end="\r")

	print(str(count) + "\n# Contributors downloaded !")
	#print(json.dumps(current_j, indent = 4, sort_keys =True))
	return current_j

######

def commitsMonitoring(headers):
	### Monitorer la valeur de commits journaliers. Si le nombre de commits journaliers est inférieur à 2, on doit le détecter et remonter l'information. 

	today_date = datetime.utcnow().replace(tzinfo=timezone.utc).replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0).isoformat()
	
	# requête
	url_monitoring = urljoin(github_api, "/repos/facebook/react/commits")
	res = requests.get(
		url_monitoring,
		headers = headers,
		params = {'since' : today_date }
		)

	# parse
	list_commit = json.loads(res.text)

	# affichage du nombre de commits journaliers
	nb_commit = len(list_commit)
	#print("Daily commit(s): " + str(nb_commit)

	# report si moins de 2 commits dans la journée
	if len(list_commit) < 2:
		print("Warning : daily commits below 2")

	# écriture dans un fichier .txt
	file_name = "Report_commits_"+str(today_date)[:10]
	with open(file_name, "w") as report_file:
		report_file.write("Report for the " + str(nb_commit) + " daily commit(s) - " + str(today_date)[:10] + "\n\n")
		for i in range(len(list_commit)):
			report_file.write("################## Commit "+ str(len(list_commit)-i) + " ##################\n\n")
			report_file.write(json.dumps(list_commit[i].get('commit'), indent = 4, sort_keys =True))
			report_file.write("\n\n")
	print("Read '" + file_name + ".txt' for more informations about daily commits.")


######

def contributionsVisualizer(headers,list_contributors):
	### Produire une visualisation, pour chaque nombre de contributions, la proportion des contributeurs qui ont réalisé ce nombre de contributions (le plot log-log peut être intéressant).
	
	total_contributions = 0
	proportion_contributors = {}
	nb_contributors = len(list_contributors)

	# création d'un dictionnaire avec pour clé le nombre de contributions et pour valeur le nombre de contributeurs 
	for i in range(nb_contributors):
		current_contributions = list_contributors[i].get('contributions')

		if (current_contributions in proportion_contributors):
			proportion_contributors[current_contributions] += 1
		else:
			proportion_contributors[current_contributions] = 1

		total_contributions = total_contributions + current_contributions
	
	#print ("Total contributions :" + str(total_contributions))

	# tracé
	plt.figure(figsize=(10,5), dpi=100)
	y = list(proportion_contributors.values())
	x = list(proportion_contributors.keys())
	plt.loglog(x,y, '-s')
	plt.fill_between( x, y, color="skyblue", alpha=0.4)
	plt.xlabel("Contributors")
	plt.ylabel("Contributions")
	plt.grid()
	plt.savefig("contributors_distribution.png")
	plt.show()

######

def globalActivity(headers, list_contributors):
	### Bonus : créer un aperçu de l'activité globale de ces contributeurs. 
	### réponse : représentation du nombre de commits sur la durée pour un ou tout les contributeurs
	
	url_commit = urljoin(github_api, "/repos/facebook/react/commits")
	commit_per_date = {}
	stop = 0
	i = 1


	print("# Show global activity of : \n (1) All users (long) \n (2) One user")
	while True:
		choice = input("Answer (enter a integer) : ")
		if choice == '1' or choice == '2':
			break
		else:
			print("# Value error : please enter a valid integer")

	# téléchargement de tout les commits du repos (long car 30 par 30)
	if choice == '1':
		while stop != 1:

			# requête
			res = requests.get(
				url_commit, 
				params = {'page': i}, 
				headers = headers
				)

			# si il ne reste plus de commits à télécharger
			if res.text == "[]":
				stop = 1

			else:
				if i == 1:
					# premier parse
					list_commit_user = json.loads(res.text)
				else:
					# on parse et on rajoute aux commits déjà collectés
					list_commit_user_temp = json.loads(res.text)
					list_commit_user = list_commit_user + list_commit_user_temp

			i += 1

			# compte progression
			nb_commit = len(list_commit_user)
			print(str(nb_commit), end="\r")

	# téléchargement des commits d'un utilisateur
	if choice == '2':

		print("# Show global activity of one of the top10 contributors : ")
		for j in range(10):
			print("#" + str(j+1) + " " + list_contributors[j].get('login'))
		
		while True:
			choice_user = input("Answer (enter a integer) : ")
			if choice_user in ['1','2','3','4','5','6','7','8','9','10']:
				break
			else:
				print("# Value error : please enter a valid integer")

		print("# Downloading commits...")
		while stop != 1:

			# requête
			choice_user_name = list_contributors[int(choice_user)].get('login')
			res = requests.get(
					url_commit, 
					params = {'page': i ,'author': choice_user_name},
					headers = headers
					)

			# si il ne reste plus de commits à télécharger
			if res.text == "[]":
				stop = 1

			else:
				if i == 1:
					# premier parse
					list_commit_user = json.loads(res.text)
				else:
					# on parse et on rajoute aux commits déjà collectés
					list_commit_user_temp = json.loads(res.text)
					list_commit_user = list_commit_user + list_commit_user_temp

			i += 1

			# compte progression
			nb_commit = len(list_commit_user)
			print(str(nb_commit), end="\r")

	print(str(nb_commit) + "\n# Downloading complete !")

	# création d'un dictionnaire avec pour clé la date et pour valeur le nombre de commits effectués à cette date
	for i in range(nb_commit):
		date_commit_string = list_commit_user[i].get('commit').get('author').get('date')[:10]
		date_commit = datetime.strptime(date_commit_string, '%Y-%m-%d')
		if (date_commit in commit_per_date):
			commit_per_date[date_commit] += 1
		else:
			commit_per_date[date_commit] = 1
	#print(commit_per_date)

	# visualisation
	plt.figure(figsize=(10,5), dpi=100)
	x,y = zip(*sorted(commit_per_date.items()))
	plt.stem(x,y,markerfmt=' ')
	plt.xlabel("Date")
	plt.ylabel("Contributions")
	plt.show()
	plt.savefig("global_activity.png")



if __name__ == '__main__':
	main()
