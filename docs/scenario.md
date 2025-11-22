# Scénario et spécifications fonctionnelles — Frontend Vue.js

Date : 2025-11-18

Objectif
--------
Ce document reformule et complète le scénario fonctionnel pour l'interface utilisateur de l'application (frontend) qui sera développée en Vue.js. Il décrit le flux d'authentification, la structure du menu principal, les vues et sections principales (Home, Bande, Dashboard, Consommation, Chatbot, Infos, etc.), les composants proposés, les routes et les points d'API nécessaires.

Résumé utilisateur
------------------
- L'utilisateur (éleveur) doit se connecter pour utiliser l'application.
- Lors de la connexion, s'il n'a pas coché « Se rappeler de moi », la session est limitée (ex : cookie de session). S'il a demandé « Se rappeler de moi », on crée un cookie persistant sécurisé.
- S'il n'a pas de compte, il peut s'inscrire (formulaire). Après inscription, il est dirigé vers le menu principal (Home).
- Depuis le menu principal (Home) l'utilisateur voit :
  - Un tableau de bord global (agrégat sur toutes les bandes de l'utilisateur) avec KPI et prédictions.
  - La possibilité de créer une nouvelle bande (formulaire).
  - La liste des bandes déjà créées (carte/liste). Cliquer sur une bande ouvre la vue `Bande` dédiée.

Vue `Home` (Menu principal)
---------------------------
Contenu recommandé :
- Header : logo, barre de recherche globale, icône profil (avatar + menu déroulant : Profil, Paramètres, Déconnexion).
- Sidebar (ou menu top) : navigation vers `Home`, `Bandes`, `Consommations`, `Dépenses`, `Traitements`, `Interventions`, `Predictions`, `Workers`, `Chatbot`, `Dashboard global`.
- Main area :
  - Section Dashboard global : graphiques (évolution poids moyen, coût total, taux mortalité, IC), petit tableau de KPI, boutons « Calculer KPI », « Lancer prédiction ».
  - Section Création de bande : formulaire compact (nom, date arrivée, race, fournisseur, nombre initial, poids moyen initial).
  - Section Liste des bandes : cartes avec résumé (nom, statut, nb animaux, date arrivée, lien 'Ouvrir').
- Footer : mentions, version de l'application, liens d'aide.

Vue `Bande` (page dédiée à une bande)
------------------------------------
Structure principale : onglets ou sous-navigation -> `Dashboard`, `Consommation / Alimentation`, `Chatbot`, `Infos`, `Traitements`, `Interventions`, `Animaux`, `Dépenses`, `Predictions`.

1) Onglet `Dashboard` :
   - KPI spécifiques à la bande (poids moyen actuel, coût cumulé, IC, taux mortalité).
   - Graphiques temporels (poids, consommation d'aliment, mortalité hebdo).
   - Boutons pour recalculer KPI et lancer prédictions (ou visualiser prédictions existantes).

2) Onglet `Consommation / Alimentation` :
   - Formulaire pour ajouter une consommation (date, type aliment, kg, eau litres, coût).
   - Liste/tableau des consommations enregistrées avec filtres par période.

3) Onglet `Chatbot` :
   - Interface de chat texte pour échanger avec une IA via une API externe (prévoir envoi du contexte bande / eleveur si besoin).

4) Onglet `Infos` :
   - Métadonnées : date création, date arrivée, fournisseur, race.
   - Statistiques de qualité : nombre actuels, age moyen, nombre nouveaux nés, nombre morts totaux.
   - Détails sur les animaux : liste sommaire ou lien vers `Animaux` détaillé.

5) Autres onglets :
   - `Traitements` : historique des traitements, formulaire d'ajout.
   - `Interventions` : historique des interventions, formulaire d'ajout.
   - `Dépenses` : liste et ajout de dépenses liés à la bande.
   - `Predictions` : historique des prédictions pour la bande et indicateurs de fiabilité.

Composants Vue.js proposés
--------------------------
- `AppHeader` : logo, recherche, profil.
- `AppFooter` : footer global.
- `Sidebar` / `TopNav` : navigation.
- `LoginForm` : gestion login + checkbox `rememberMe`.
- `RegisterForm` : inscription.
- `HomeDashboard` : agrégats et contrôles globaux.
- `BandeCard` : composant réutilisable pour la liste des bandes.
- `BandeView` : wrapper pour la page `Bande`, contient les onglets.
- `KPIWidget` : widget réutilisable pour afficher un KPI.
- `Chart` : wrapper pour bibliothèques (Chart.js, ECharts, ApexCharts).
- `ChatbotBox` : interface chat.
- `Form*` : `FormConsommation`, `FormDepense`, `FormTraitement`, etc.

Routing (vue-router)
--------------------
- `/login` → `LoginForm`
- `/register` → `RegisterForm`
- `/` or `/home` → `Home` (requiresAuth)
- `/bandes` → liste des bandes
- `/bandes/create` → formulaire création
- `/bandes/:id` → `BandeView`
- `/bandes/:id/consommation` etc. (ou gérer via onglets côté client)

Etat & Auth
-----------
- Utiliser `Pinia` (ou Vuex) pour l'état global : user, token, listes (bandes, animaux, consommations), UI state.
- Auth : API d'authentification renvoie un JWT ou session token. Stocker token en mémoire + `httpOnly` cookie si possible. Si `rememberMe` sélectionné : créer cookie persistant (ex : 30 jours) ou rafraîchir via refresh token.
- Middleware route : rediriger vers `/login` si non authentifié.

API & Endpoints recommandés (backend)
-------------------------------------
- POST `/api/auth/login` {email, password, rememberMe} → {token, refreshToken?, user}
- POST `/api/auth/register` {nom, email, password, ...} → {user, token}
- GET `/api/bandes` → liste bandes de l'utilisateur
- POST `/api/bandes` → création bande
- GET `/api/bandes/:id` → détail bande
- GET `/api/bandes/:id/kpi` → KPIs calculés pour la bande
- POST `/api/bandes/:id/consommations` → ajouter consommation
- GET `/api/bandes/:id/consommations` → liste consommations
- POST `/api/bandes/:id/predictions` → lancer prédiction (ou endpoint ML séparé)
- POST `/api/chatbot` → send message to AI (context includes eleveur_id, bande_id optional)

Workflow utilisateur exemples
-----------------------------
1) Inscription : utilisateur remplit `RegisterForm` → backend crée eleveur → token renvoyé → redirigé vers `Home`.
2) Création d'une bande : depuis `Home` remplir `CreateBande` → backend crée bande → rafraîchir liste bandes → ouvrir `BandeView`.
3) Saisie consommation : accéder à `BandeView` → onglet `Consommation` → remplir formulaire → backend stocke → recalculer KPI (backend ou frontend).

Calculs & prédictions
---------------------
- KPI : à définir précisément (IC, poids moyen, coût total, taux mortalité). Les calculs peuvent être faits côté backend et stockés dans `kpi_dashboard` ou bien calculés à la volée.
- Prédictions : prévoir un endpoint qui accepte des features agrégées (consommations historiques, poids, mortalité) et renvoie des valeurs prédites + fiabilité.

UI / UX — recommandations
-------------------------
- Design moderne, responsive, mobile-first.
- Couleurs contrastées pour lisibilité, icônes claires pour sections (profil, recherche, ajout).
- Utiliser composants accessibles (aria labels), validations et messages d'erreur conviviaux.
- Afficher loaders pour opérations réseau longues (calcul KPI, prédictions).

Extensions proposées (si vous voulez ajouter)
-----------------------------------------
- Export CSV / Excel des consommations, traitements, dépenses.
- Import de lots d'animaux via fichier CSV.
- Notifications en temps réel (WebSocket) pour interventions ou alertes.
- Multi-éleveur / multi-roles (permissions) : gestion des workers et rôles.

Fichiers HEAD/BODY/FOOT (structure HTML)
----------------------------------------
- `index.html` : standard `<!doctype html>` avec meta viewport, link CSS, bundle JS.
- `HEAD` : title, meta description, favicon, liens CSS (tailwind / bootstrap / custom), tags OpenGraph si besoin.
- `BODY` : `#app` root, `AppHeader`, `Sidebar`, `RouterView`, `AppFooter`.

Checklist avant implémentation Vue.js
-----------------------------------
- Choix de stack : Vue 3 + Vite, Pinia, Vue Router, Axios/Fetch, Chart library.
- Choix CSS : TailwindCSS ou BootstrapVue ou Vuetify.
- Définir conventions d'API (format, erreurs, pagination).
- Définir stratégie d'auth (JWT + refresh token ou session cookie httpOnly).
- Créer maquettes (Figma / Sketch) des écrans clés (`Home`, `Bande`, `Formulaire création`).

Prochaine étape
---------------
- Valider ce scénario — indiquer si vous voulez que je :
  1) Génère les composants Vue.js de base (scaffolding) et les routes, ou
  2) Génère une maquette HTML/CSS statique des écrans, ou
  3) Convertisse ce document en PDF et l'ajoute au repo (je peux essayer de convertir si `pandoc` est installé), ou
  4) Autre chose (précisez).

---

Fin du document.
