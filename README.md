# Test du joystick Picade

Application de test pour le [joystick Pimoroni 5 broches](https://shop.pimoroni.com/products/joystick),
un Raspberry Pi Zero et un écran HDMI avec bureau graphique. Les quatre
contacts permettent de détecter le centre, les quatre directions et les quatre
diagonales. Une combinaison contradictoire est signalée au lieu d'afficher
une position incorrecte.

## Branchement

Éteindre le Pi et débrancher son alimentation avant de câbler. Un connecteur
40 broches doit être soudé sur le Pi Zero. Utiliser un câble compatible
JST-XH 5 broches avec cinq fils vers le Pi, par exemple un faisceau JST-XH
vers Dupont femelle.

Sur le connecteur du joystick, le fabricant indique l'ordre ci-dessous, en
partant de la broche la plus proche de l'axe du joystick :

| Ordre joystick | Contact initial | Raspberry Pi, nom BCM | Broche physique Pi | Direction affichée |
|---|---|---|---|---|
| 1, près de l'axe | Haut | GPIO 5 | 29 | Gauche |
| 2 | Bas | GPIO 6 | 31 | Droite |
| 3 | Droite | GPIO 19 | 35 | Haut |
| 4 | Gauche | GPIO 13 | 33 | Bas |
| 5, loin de l'axe | Masse commune | GND | 39 | — |

Le câblage est inchangé. Le programme applique une rotation de 90 degrés
aux directions initiales : ancien haut vers gauche, ancienne droite vers haut,
ancien bas vers droite et ancienne gauche vers bas.

Les numéros de broches physiques ne sont **pas** les numéros GPIO BCM. Vérifier
les broches sur le Pi avant de brancher ; une broche GND n'est pas une broche
3,3 V ou 5 V. Ne relier le joystick ni à 3,3 V ni à 5 V : les résistances
pull-up internes sont activées par le programme. Ne pas se fier aux couleurs
du faisceau sans les vérifier. Un multimètre en mode continuité, alimentation
débranchée, permet d'identifier le fil commun : chaque direction ferme son
contact entre ce fil et l'un des quatre autres. L'orientation du joystick
une fois monté peut nécessiter d'échanger les fils de direction.

Ces GPIO doivent être libres : vérifier notamment si des accessoires ou des
fonctions de l'écran utilisent le connecteur 40 broches. L'image HDMI seule
n'utilise pas ces GPIO. Le branchement est direct : pas de Picade HAT.

## Installation sur le Raspberry Pi

Depuis une connexion SSH au Pi, avec Raspberry Pi OS et son bureau graphique :

```sh
sudo apt update
sudo apt install python3 python3-tk python3-gpiozero python3-lgpio
```

Il faut copier `joystick_test.py` sur le Pi. Par exemple, depuis le terminal du
PC où se trouve ce dossier, remplacer `UTILISATEUR` et `ADRESSE_DU_PI` :

```sh
scp joystick_test.py UTILISATEUR@ADRESSE_DU_PI:~/joystick_test.py
```

## Démarrage par SSH

Ouvrir d'abord une session sur le **bureau graphique du Pi**, puis se connecter
en SSH avec le **même utilisateur** et lancer :

```sh
DISPLAY=:0 python3 ~/joystick_test.py
```

La fenêtre apparaît en plein écran sur le Pi, pas sur le PC SSH. Le centre
doit être vert au repos ; bouger le joystick dans chaque direction et chaque
diagonale. Les contacts détectés sont aussi indiqués sous la grille.
Pour quitter, faire **Ctrl+C dans le terminal SSH**. La touche Échap fonctionne
également si un clavier est disponible.

Si l'affichage ne s'ouvre pas, vérifier que le bureau est déjà démarré, que
la session SSH utilise le même compte et que `:0` correspond bien à l'affichage
de cette session. Un bureau Wayland doit disposer de XWayland pour Tk. Ne pas
lancer le programme avec `sudo`, qui peut empêcher l'accès à la session
graphique ; vérifier à la place les permissions GPIO et les éventuels conflits
avec d'autres programmes.

Pour tester l'interface sans joystick, utiliser `--simulation` et les flèches
du clavier. Pour exécuter les tests automatisés : `python3 -m unittest -v`.
