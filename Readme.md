🌾 Agridata OSINT Explorer
Un outil d'extraction de données publiques pour le journalisme d'investigation (Projet Ba7ath)

Agridata OSINT Explorer est une application de bureau de bureau open-source conçue pour interroger, filtrer et extraire de manière ciblée ou massive les bases de données du portail national agridata.tn via son API CKAN.

Cet outil a été développé pour contourner les limitations des moteurs de recherche administratifs et les formats de données complexes, permettant ainsi aux chercheurs et journalistes de se concentrer sur l'analyse factuelle plutôt que sur le nettoyage de données.

✨ Fonctionnalités Principales
🔍 Exploration API CKAN : Interrogation directe des serveurs pour identifier les jeux de données tabulaires exploitables sans saturer la bande passante.

👁️ Aperçu Rapide (Frappe Chirurgicale) : Affichage instantané des 5 premières lignes d'un dataset pour auditer la structure des colonnes avant tout téléchargement lourd.

🎯 Filtrage Local Robuste (Moteur Pandas) :

Nettoyage OSINT : Suppression automatique des lignes "fantômes" ou vides (courantes dans les exports administratifs).

Filtre Géographique : Sélection multicritères couvrant les 24 gouvernorats tunisiens.

Détection Intelligente (Wide Format) : Le filtre temporel s'adapte automatiquement si les années sont formatées en colonnes plutôt qu'en lignes.

Filtre Tolérant (Forgiving Filter) : Si un filtre géographique ou temporel échoue (ex: erreur orthographique dans la base source), l'outil préserve les données brutes au lieu de renvoyer un fichier vide.

📦 Extraction par Lot (Batch Download) : Capacité d'aspirer en un clic l'intégralité des résultats d'une recherche vers un dossier local, avec nommage sécurisé des fichiers.

🖥️ Interface Moderne et Autonome : Interface sombre (Dark Mode) intuitive conçue avec CustomTkinter, compilée en un exécutable autonome ne requérant aucune installation technique.

🚀 Guide d'Installation
Option A : Pour les utilisateurs (Journalistes / Chercheurs)
Aucune compétence en programmation n'est requise.

Téléchargez le fichier agridata_osint_pro.exe depuis la section [Releases].

Double-cliquez sur le fichier pour lancer l'application (sous Windows, si SmartScreen affiche un avertissement, cliquez sur "Informations complémentaires" puis "Exécuter quand même").

Option B : Pour les développeurs (Code Source)
Clonez ce dépôt :

Bash
git clone https://github.com/votre-compte/agridata-osint-explorer.git
cd agridata-osint-explorer
Installez les dépendances :

Bash
pip install -r requirements.txt
# (requests, pandas, openpyxl, customtkinter)
Lancez le script :

Bash
python agridata_osint_pro.py
🛠️ Workflow d'Investigation (Méthodologie)
Rechercher : Entrez un mot-clé (ex: cheptel, céréales, subventions).

Inspecter : Sélectionnez un jeu de données et cliquez sur "👁️ Aperçu rapide" pour comprendre comment l'administration a structuré l'information.

Cibler : Si la structure convient, ajustez les filtres (Années, Gouvernorats) dans le panneau de gauche.

Extraire : * Pour un fichier unique : Cliquez sur "Télécharger le Dataset sélectionné" et choisissez le format (.csv ou .xlsx).

Pour une investigation large : Cliquez sur "Télécharger TOUT (Lot)" pour aspirer tous les fichiers liés à votre mot-clé d'un seul coup.

⚖️ Éthique et Légalité (OSINT)
Cet outil est conçu dans le strict respect des méthodologies de l'Open Source Intelligence (OSINT) et du journalisme de données éthique. Il interroge exclusivement des données publiques ouvertes (Open Data) via les points d'accès API officiels (/api/3/action/package_search et datastore_search), conformément aux directives de la plateforme source. La pagination intégrée garantit que les serveurs gouvernementaux ne sont jamais surchargés par les requêtes.

Projet développé dans le cadre de l'initiative Ba7ath pour la vulgarisation de l'OSINT.