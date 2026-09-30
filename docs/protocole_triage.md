# Protocole de triage

Ce protocole fixe les règles des labels de triage. Il est donné à Mistral Large, qui
annote les cas, et il sert de grille pour relire le jeu d'évaluation.

Je ne suis pas soignant : ce protocole n'a pas été validé médicalement. Il reprend
les grandes lignes de l'échelle de tri FRENCH (Société française de médecine
d'urgence), ramenée aux trois niveaux de la mission.

## Les trois niveaux

On se place à l'accueil des urgences et on se demande : ce patient peut il attendre
sans risque ?

- `maximum` : danger vital ou risque de séquelle, il faut le voir tout de suite
  (tri 1 et 2 de FRENCH).
- `moderate` : problème aigu à voir dans les heures qui viennent, sans danger
  immédiat (tri 3).
- `deferred` : rien d'urgent, une consultation ou un suivi suffit (tri 4 et 5).

## Les règles

1. En cas de doute entre deux niveaux, prendre le plus urgent. Rater une urgence est
   plus grave que faire passer quelqu'un trop tôt.
2. Juger seulement sur ce qui est écrit dans le cas, sans supposer de signe absent.
3. Juger le patient au début du cas, tel qu'il arrive. Ne pas tenir compte du
   traitement ou de l'évolution racontés ensuite, ni des pistes de diagnostic
   données par l'énoncé. Les résultats d'examens (prise de sang, imagerie) ne
   comptent que s'ils montrent un danger immédiat.
4. Un symptôme grave qui a disparu reste un signe d'alerte (paralysie passagère,
   malaise avec perte de connaissance).
5. Un terrain fragile (nourrisson, personne très âgée, grossesse, immunodépression)
   peut faire monter le niveau d'un cran.
6. La gravité de la maladie n'est pas l'urgence. Un cancer possible, une maladie
   chronique ou une anomalie trouvée sur un bilan, sans symptôme aigu, donnent
   `deferred`, même si un bilan rapide est utile.
7. Des symptômes présents depuis des semaines ou des mois, sans aggravation
   brutale, donnent `deferred`.

## Ce qui donne `maximum`

Des constantes très anormales (tension effondrée, détresse respiratoire, coma,
convulsions), ou une situation qui peut tuer ou laisser des séquelles rapidement :
suspicion d'infarctus ou d'AVC, méningite, traumatisme grave, hémorragie abondante,
réaction allergique grave, tentative de suicide.

## Remplir le JSON

- `specialty` : la spécialité d'orientation, uniquement parmi les valeurs de la
  liste. Si aucune ne convient (endocrinologie, dermatologie, hématologie...),
  mettre `general_medicine`. Un nouveau né ou un enfant va dans la spécialité de
  son problème.
- `key_symptoms` : les symptômes du cas, en quelques mots, sans rien inventer.
- `red_flags` : seulement les signes de danger immédiat présents dans le cas,
  comme ceux de la section `maximum`. Pas les facteurs de risque (tabac,
  antécédents) ni les suspicions de maladie grave. Au moins un pour un cas
  `maximum`, aucun pour un `deferred`.
- `justification` : 2 ou 3 phrases qui expliquent le niveau, dans la langue du cas.
- `recommendation` : une phrase courte pour l'équipe, dans la langue du cas.

## Exemples

Cas MediQAl résumés.

| Cas | Niveau | Pourquoi |
|---|---|---|
| Homme de 78 ans, diabétique, douleur au creux de l'estomac avec sueurs depuis 2 heures | `maximum` | Peut être un infarctus |
| Vision trouble et main engourdie quelques secondes, puis jambe qui ne porte plus le lendemain | `maximum` | Signes d'AVC, même passagers |
| Femme de 65 ans, fracture du col du fémur après une chute, état général conservé | `moderate` | À opérer, mais sans danger immédiat |
| Crise d'asthme qui ne cède pas, sans autre signe de gravité | `moderate` | Serait `maximum` avec une détresse respiratoire |
| Homme de 55 ans, gros fumeur, adressé à l'ORL pour une voix enrouée | `deferred` | Un cancer possible se bilante en consultation |
| Femme de 28 ans qui consulte pour une contraception | `deferred` | Pas de problème aigu |
| Insuffisance rénale modérée découverte sur un bilan de routine | `deferred` | Rien d'aigu |
