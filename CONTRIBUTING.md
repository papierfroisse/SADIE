# Guide de contribution

Merci de votre intérêt pour contribuer à sadie ! Ce document fournit les lignes directrices pour contribuer au projet.

## Code de conduite

Ce projet et tous ses participants sont régis par notre [Code de conduite](CODE_OF_CONDUCT.md). En participant, vous acceptez de respecter ce code.

## Comment contribuer

### Signaler des bugs

1. Vérifiez d'abord si le bug n'a pas déjà été signalé
2. Créez une issue en utilisant le template "Bug Report"
3. Décrivez clairement le problème et les étapes pour le reproduire
4. Incluez les logs et captures d'écran pertinents

### Proposer des améliorations

1. Vérifiez si l'amélioration n'a pas déjà été proposée
2. Créez une issue en utilisant le template "Feature Request"
3. Expliquez clairement l'amélioration et ses bénéfices
4. Attendez la validation avant de commencer le développement

### Soumettre des modifications

1. Fork le projet
2. Créez une branche pour votre modification (`git checkout -b feature/amazing`)
3. Faites vos modifications
4. Ajoutez ou mettez à jour les tests
5. Mettez à jour la documentation si nécessaire
6. Exécutez les tests (`pytest`)
7. Commitez vos changements (`git commit -m 'Add amazing feature'`)
8. Poussez vers votre fork (`git push origin feature/amazing`)
9. Ouvrez une Pull Request

## Style de code

- Suivez PEP 8 pour le style Python
- Utilisez des noms explicites en français
- Commentez le code en français
- Documentez les fonctions et classes avec docstrings
- Limitez les lignes à 88 caractères (black)
- Utilisez des annotations de type

## Tests

- Ajoutez des tests pour chaque nouvelle fonctionnalité
- Maintenez une couverture de code > 80%
- Les tests doivent passer sur toutes les versions Python supportées
- Utilisez pytest pour les tests

## Documentation

- Mettez à jour la documentation pour les nouvelles fonctionnalités
- Suivez le style de documentation existant
- Incluez des exemples d'utilisation
- Vérifiez l'orthographe et la grammaire

## Process de revue

1. Au moins un mainteneur doit approuver les changements
2. Les tests doivent passer
3. La couverture de code doit être maintenue
4. Le style de code doit être respecté
5. La documentation doit être à jour

## Versionnement

Nous utilisons [SemVer](http://semver.org/) pour le versionnement :

- MAJOR : changements incompatibles
- MINOR : nouvelles fonctionnalités compatibles
- PATCH : corrections de bugs compatibles

## Questions

Pour toute question :

1. Consultez d'abord la documentation
2. Vérifiez les issues existantes
3. Ouvrez une nouvelle issue avec le tag "question" 