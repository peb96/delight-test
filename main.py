github_api = 'https://api.github.com'

##########################################################################

import requests
import json
import getpass
import csv
import datetime
import matplotlib.pyplot as plt
from urllib.parse import urljoin


def main():
	# authentification
	headers =  {'Authorization': 'token %s' % getToken()}
	#

	list_contributors = downloadContributors(headers)
	# commitsMonitoring(headers)
	contributionsVisualizer(headers,list_contributors)
	globalActivity(headers,list_contributors)


def downloadContributors(headers):
	# Télécharger et formater les données des contributeurs (incluant contributeurs anonymes).
	stop = 0
	i = 1
	while stop != 1:
		res = requests.get(github_api+"/repos/facebook/react/contributors", params={'page': i ,'anon': True}, headers=headers)
		if res.text == "[]":
			stop = 1
		else:
			if i == 1:
				current_j = json.loads(res.text)
			else:
				j = json.loads(res.text)
				current_j = current_j + j
		i += 1
	print("Contributors downloaded !")
	#print(json.dumps(current_j, indent = 4, sort_keys =True))
	return current_j

def commitsMonitoring(headers):
	# Monitorer la valeur de commits journaliers. Si le nombre de commits journaliers est inférieur à 2, on doit le détecter et remonter l'information. 
	today_date = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0).isoformat()
	res = requests.get(github_api+"/repos/facebook/react/commits", headers= headers, params= {'since' : today_date })
	j = json.loads(res.text)
	print(json.dumps(j, indent = 4, sort_keys =True))
	print("Nombre de commits journaliers: " + len(j))


	if len(j) < 2 :
		print("DETECT")
		#ECRIRE UN FICHIER TEXTE AVEC DATE ET NOMBRE DE COMMITS + NOM

def contributionsVisualizer(headers,list_contributors):
	# Produire une visualisation, pour chaque nombre de contributions, la proportion des contributeurs qui ont réalisé ce nombre de contributions (le plot log-log peut être intéressant).
	proportion_contributeurs = {}
	for i in range(len(list_contributors)):
		current_contributions = list_contributors[i].get('contributions')
		if (current_contributions in proportion_contributeurs):
			proportion_contributeurs[current_contributions] += 1
		else:
			proportion_contributeurs[current_contributions] = 1
	plt.figure(figsize=(10,10), dpi=70)
	y = list(proportion_contributeurs.values())
	x = list(proportion_contributeurs.keys())
	plt.loglog(x,y,'ro')
	plt.savefig("out.png")

def globalActiviy():
	# Bonus : créer un aperçu de l'activité globale de ces contributeurs. 
	


def WriteDictToCSV(csv_file,csv_columns,dict_data):
	try:
		with open(csv_file, 'w') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
			writer.writeheader()
			for data in dict_data:
				writer.writerow(data)
	except IOError as err:
		print("I/O error({0})".format(err))  
	return     


# on s'identifie pour pas avoir de limite de requêtes ( 60 sur Github )
def getToken():
	token_available = input('Already got a Github authentification token ? (Y/N) \n')
	if token_available == "Y":
		token = input('insert token: ')
		return token

	else:
		# input
		username = input('Github username: ')
		password = getpass.getpass('Github password: ')
		note = input('Note (option): ')

		# request
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

		# checking errors
		if res.status_code >= 400:
			msg = j.get('message', 'UNDEFINED ERROR (no error description from server)')
			print('ERROR: %s', msg)
			return

		# getting token
		token = j['token']
		print('New token : ', token)
		return token


if __name__ == '__main__':
	main()


