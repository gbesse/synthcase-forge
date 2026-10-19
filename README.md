# Synthcase Forge

[English](README.en.md) · [Español](README.es.md)

**Créer des cas rares avec une réponse connue, puis le plus petit changement qui fait basculer cette réponse.**

Le solveur OR-Tools génère des cas sous contraintes, répartis selon des quotas explicites. Un vérificateur Python indépendant recalcule les règles, les produits et les étiquettes. Une variante minimale change une étiquette sans modifier les faits déclarés immuables. Les données s’exportent dans SQLite avec clés étrangères et index d’étiquettes.

![Cas synthétiques et variante minimale vérifiée](docs/preview-fr.png)

## Essayer

Python 3.11 ou supérieur. Aucune clé pour générer, vérifier ou explorer les cas.

```sh
python3 -m venv .venv
.venv/bin/pip install .
.venv/bin/python -m synthcase serve --lang fr
```

Ouvrir `http://127.0.0.1:8767/?lang=fr`. Le scénario contient douze cas : quatre sans écart déclaré, trois écarts de quantité, trois de prix et deux combinés. Choisir un cas : le solveur réduit le nombre de champs modifiés puis leur distance, et recalcule le montant dérivé. Commande, réception et prix convenu restent figés.

```sh
.venv/bin/python -m synthcase generate synthcase/examples/invoice-cases.json --seed 7 --output .local/data.json
.venv/bin/python -m synthcase pair .local/data.json case-0005 quantity_exceeds_receipt
.venv/bin/python -m synthcase export .local/data.json .local/cases.sqlite
```

L’export refuse d’écraser une base existante. L’interface et les messages CLI sont en FR/EN/ES.

## Une spécification inspectable

- `variables` : bornes entières par champ ;
- `constraints` : prédicats linéaires, conjonctions, disjonctions et négations ;
- `products` : champs dérivés, par exemple quantité × prix ;
- `labels` : vérités définies par ces prédicats, pas par un modèle ;
- `cohorts` : nombre exact de cas et étiquettes requises ;
- `immutable` : faits conservés pendant les variantes.

L’exemple de facture est une spécification parmi d’autres, sans assertion de conformité fiscale. Au plus vingt variables et cent cas par demande. Les lignes sont distinctes. Une règle impossible ou un domaine épuisé produit `partial` et des quotas manquants, avec un conflit suffisant lorsqu’il est disponible ; ce conflit n’est pas nécessairement minimal.

La graine fixe des objectifs aléatoires que le solveur cherche à approcher. Ce n’est **ni un échantillonnage uniforme, ni une distribution représentative de vraies factures**. Une résolution limitée au temps peut retourner `FEASIBLE` ; son résultat peut varier entre machines. Chaque ligne conserve `solve_status`. La minimalité d’une variante n’est annoncée que lorsque le solveur la démontre, et concerne les champs indépendants ; les changements dérivés sont affichés séparément.

## Jev juge la plausibilité, sans redéfinir la vérité

La revue facultative effectue **un appel, au plus six questions**, avec un représentant par cohorte. Elle demande `plausible / implausible / uncertain`, conserve les probabilités et place les résultats peu confiants en revue. Aucune opinion ne modifie les étiquettes calculées. L’interface navigateur n’appelle aucun modèle et n’expose aucune route de clé.

```sh
.venv/bin/python -m synthcase review .local/data.json --lang fr --output .local/opinions.json
```

Le transport lit `TYPESAFE_API_KEY` dans l’environnement. L’option explicite `--env .env` accepte uniquement un fichier aux permissions `600`, ignoré par Git. Les clés, en-têtes et corps d’erreur du fournisseur ne sont jamais affichés. La vérification TLS reste active avec le magasin de certificats certifi ; aucune redirection authentifiée n’est suivie.

Essai réel du 19 octobre 2026 : Jev `jev-1.13.0` a jugé plausibles trois représentants, avec confiances **1,00 / 0,72 / 0,58**, pour **1 044 jetons entrants et 147 sortants**. Les deux derniers restent à revoir sous le seuil déclaré de 0,8. Cet essai valide le transport et la séparation des avis, **pas la qualité générale du modèle ou le réalisme du jeu**. Génération, tests et CI restent hors ligne ; aucune clé n’est publiée.

## Existant et limites

[SDV](https://docs.sdv.dev/sdv/modeling/constraint-augmented-generation-cag.md) sait déjà générer des données avec contraintes. Ce projet ne prétend pas inventer ce principe : il concentre une petite démo sur **quotas de cas rares → étiquettes connues → variante à intervention minimale → revue de plausibilité séparée**. [OR-Tools](https://developers.google.com/optimization/cp) fournit le solveur ; [TypeSafe Choice](https://docs.typesafe.ai/primitives/choice) fournit l’avis facultatif.

Une étiquette n’est vraie que relativement à la règle fournie. Des règles incomplètes peuvent produire des situations peu crédibles. Les variantes sont des modifications de dossiers sous équations déclarées, ni des actions à exécuter ni des preuves causales. Aucune confidentialité différentielle, conservation d’une distribution source, validation juridique ou supériorité SOTA n’est revendiquée.

## Validation

```sh
.venv/bin/python -m unittest discover -s tests -v
npm ci
npx playwright install chromium
PYTHON=.venv/bin/python npm run test:browser
npm run format:check
```

Quatorze tests couvrent quotas, produits, étiquettes, unicité, impossibilités, variantes face à une énumération exhaustive, export SQLite et revue Jev simulée. Parcours navigateur FR/EN/ES, mobile, quotas et absence de route secrète ; CI Python 3.11/3.12 et roue installée hors sources. Code 1 pour génération partielle ou variante impossible, 2 pour entrée/transport non valide. Licence MIT, alpha de recherche.
