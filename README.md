# [Test stage] Data Engineer

L'objectif est d'analyser la distribution des contributions par contributeur au repository de React.js (https://github.com/facebook/react), une bibliothèque Javascript.

## Bibliothèques utilisées

```bash
requests
json
getpass
datetime
matplotlib
urllib
```

## Usage

1/ Lancer l'éxecutable 'main.py' à l'aide de Python 3.

2/ Rentrer ses identifiants pour recevoir un token permettant l'envoi de requêtes multiples. (ou rentrer directement un token)

3/ Téléchargement des contributeurs

4/ Création à la racine d'un fichier texte rapportant les commits journaliers (une alerte apparait si il y en a moins de 2)

5/ Création à la racine d'un fichier 'contributors.distribution.png'  permettant la visualisation de la proportion des contributeurs qui ont réalisé un nombre de contributions.

6/ Création à la racine d'un fichier 'global_activity.png' permettant de visualiser le nombre de commits effectués depuis la création du repository.


## Rapport

- Seulement 30 contributeurs au maximum sont accessibles pour une seule requête : pour télécharger la liste complète des contributeurs de respository, je n'ai pas trouvé une autre manière de faire que de parcourir les différentes pages de contributeurs, ce qui ralentit le processus.

- J'ai eu dans un premier temps un doute sur la signification de la donnée 'contributions' fourni pour un contributeur : est-ce que cette donnée représente toutes les contributions de l'utilisateur sur Github dans sa globalité, ou est-ce que cela représente seulement ces contributions sur le repos ?

Après avoir compté le nombre de commits fait par l'utilisateur, je tombe cependant bien sur le nombre de contributions affichées sur Github. 

Malgré une différence entre le nombre de commits affichés pour un utilisateur sur le site et dans l'API, on retombe cependant bien sur le nombre de contributions totales affichées sur le site en additionnant les 'contributions' (dans l'API) de chaque utilisateur.

