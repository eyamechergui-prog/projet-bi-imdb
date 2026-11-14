# Expérimentation Machine Learning : prédiction de la note IMDb

## Objectif
Estimer la **note moyenne IMDb** d'un film à partir de son année de sortie, de sa durée et de ses genres. Il s'agit d'une prédiction de note utilisateur, pas d'une prédiction de recette ou de succès commercial.

## Données
Extraction observée : **321 958 films** ayant une note, une année et une durée positive. Parmi eux, **7 024** n'avaient pas de genre renseigné. Les genres manquants ont été imputés par `Unknown` ; la durée a été transformée par `log1p` ; les genres ont été encodés en indicateurs binaires.

## Protocole
- Entraînement : films sortis **avant 2015**.
- Test : films sortis **à partir de 2015**.
- Baseline : `DummyRegressor(strategy='mean')`.
- Modèle : `RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=5, random_state=42, n_jobs=-1)`.
- Random Forest entraîné sur un échantillon reproductible d'au plus 50 000 films d'entraînement ; évaluation sur tout le test.
- Variable cible : `note_moyenne`.
- Variables explicatives : année, `log1p(duree_minutes)`, genres encodés.
- `nb_votes` et `titre` ne sont pas utilisés comme variables explicatives.

## Résultats observés
| Modèle | MAE | R² |
|---|---:|---:|
| Baseline | 1,2140 | -0,0049 |
| Random Forest | 0,9996 | 0,2542 |

La MAE baisse d'environ **17,7 %** par rapport à la baseline. Cela représente une amélioration, mais le modèle n'explique qu'une part limitée des variations de notes.

## Limites
- Les données IMDb sont observées aujourd'hui ; l'année de sortie seule ne garantit pas une simulation fidèle d'une prédiction « avant sortie ».
- Les genres, l'année et la durée ne suffisent pas à expliquer la qualité ou la réception réelle d'un film.
- Les très grandes durées sont atypiques ; `log1p` réduit leur influence mais ne les valide pas.
- L'évaluation porte seulement sur des films notés avec année et durée renseignées.
- Les scores peuvent se dégrader pour les films futurs, ou si les habitudes de notation changent.
- L'importance des variables du Random Forest n'est pas une preuve de causalité.

## Améliorations envisagées
- Tester une validation temporelle à plusieurs coupures.
- Comparer des modèles plus simples et des hyperparamètres ajustés uniquement sur une validation séparée.
- Analyser les erreurs selon année, genre et volume des votes (le nombre de votes sert à analyser les erreurs, pas à prédire avant sortie).
- Reconstituer des données historiques si l'objectif est une véritable prédiction avant sortie.
