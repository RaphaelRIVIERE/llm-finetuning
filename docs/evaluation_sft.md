# Évaluation SFT

Checkpoint évalué : `runs/sft/complet/checkpoint-500`

Perplexité sur le split test (250 exemples) : 3.37 (loss moyenne 1.2155)

Génération avec repetition_penalty=1.3, no_repeat_ngram_size=3.

## Exemples sur eval_clinique

### Exemple 1

**Instruction**

Cas clinique : Patient de 49 ans, éthylisme et tabagisme chronique, pris en charge par le SAMU pour troubles de la conscience. A l’arrivée au domicile du patient : pression artérielle 60/40 mmHg, pouls presque imprenable, marbrures au niveau des genoux, pâleur intense, Glasgow 3, pâleur, T° 35°5C, Dextro 3,2 mmo/l, mydriase bilatérale réactive. L’interrogatoire de la famille révèle une hospitalisation pour ascite il y a 6 mois.

Question : Le patient est finalement extubé après 20 jours d’hospitalisation. Une insuffisance rénale persiste nécessitant une hémodialyse toutes les 48 heures. Le patient sort de réanimation et les dialyses sont suspendues pendant 4 jours malgré une anurie persistante. Au 5ème jour apparait une détresse respiratoire. A l’auscultation pulmonaire, crépitants bilatéraux.
Quel est le diagnostic le plus probable ? Justifiez. Quelles sont vos autres hypothèses diagnostiques ? Justifiez.

**Réponse attendue**

Diagnostic : 
oedème pulmonaire hémodynamique ou cardiogènique sur surcharge volémique et insuffisance rénale. 
Autres : 
SDRA, 
pneumopathie bilatérale nosocomiale 

Justifications : 
Insuffisance rénale 
Anurique 
Surcharge volémique progressive 
Pas de dialyse pendant 4 jours.

**Réponse générée**

 Syndrome inflammatoire systémique (SIS) avec syndrome infectieux à pneumocystose
- Crépitation sur auscultaition 
 - Anorexie , fièvre

### Exemple 2

**Instruction**

Cas clinique : Dans une polyclinique de la région on s’intéresse à deux stratégies diagnostiques lors de la prise en charge d’une douleur thoracique chez des patients de 40 à 50 ans.La première concerne la  prise en charge de patients souffrant d’une douleur rétro sternale avec irradiation dans le bras gauche dans un service d’Urgences.La deuxième concerne la prise  en charge d’une douleur thoracique atypique sans signes associés en ambulatoire.On étudie les deux examens diagnostiques suivants : Electrocardiogramme et dosage des CPK.Résultats : Population de 100 personnes :Sur 75 patients ayant un diagnostic d’infarctus certifié, 68 patients ont eu un ECG positif et 64 un dosage des CPK positif.  Six patients indemnes de maladie coronarienne avaient un ECG positif et 7 un dosage de  CPK positifs.

Question : Dans le cadre d’une prise en charge en urgence, quelle serait votre stratégie de prescriptions des examens complémentaires ? Justifier.

**Réponse attendue**

En urgence, il faut obtenir le plus rapidement possible un diagnostic fiable, on réalisera donc un ECG et un dosage des enzymes cardiaques de façon simultanée (en parallèle).
Si l’un des deux tests est positif, le diagnostic est fait, a fortiori si les deux examens sont positifs. Par contre, si les deux examens sont négatifs, on s’orientera vers une autre piste.

**Réponse générée**

Électro cardiomodélisation (ECM) ou électrophysiologie par cathétérisme veineux droit

### Exemple 3

**Instruction**

Cas clinique : Interne en pédiatrie à Nantes, vous effectuez le premier examen clinique de Malo, d’origine bretonne, né la veille à 38 semaines et 3 jours de vie. Son poids de naissance est de 3,310 kg.Ce bébé, 1er enfant, est né par siège après un travail de 9 heures. Aucune anomalie n’avait été notée lors du diagnostic anténatal.

Question : La maman a choisi sous nos conseils d’effectuer un allaitement maternel. Quels conseils donnez-vous à la mère vis-à-vis de l’allaitement maternel ?

**Réponse attendue**

Réaliser l’allaitement avec des horaires souples . En général une tétée toutes les 2 ou 3 heures  au début.
Pendant les tétées : installation confortable , la bouche du nouveau-né doit prendre correctement l’aréole  et non le seul mamelon
Donner les 2 seins à chaque tétée 
Hygiène de vie  : boissons abondantes , alimentation variée  et riche en protéines  et en calcium , prohiber tabac , alcool  et excitants (café, thé), 
lavage quotidien des seins  à l’eau et au savon, protéger les mamelons avec une compresse sèche   pour éviter la macération.

**Réponse générée**

L'allattement doit être initié dès que possible (au plus tard au bout des premières journées). Il faut éviter les séances prolongées avec une seule mamelle pour ne pas diminuer ou arrêter complètements son désir.
Il convient également :
• De préparer correctement ses seins
– En se lavant soigneusement avant chaque biberon 
et dans tous cas entre deux nourrissons afin qu'ils restent propres  
pour empêcher toute infection ;
 • D'appliquer régulièrement sur ces derniers quelques gouttes décongestionnantes comme Lomégil® , qui contiennent éphédrine .
Enfin il faudra surveiller attentivement sa consommation alimentaire car elle peut avoir aussi influence .

### Exemple 4

**Instruction**

Cas clinique : Une femme de 28 ans, 69,5 kg pour 1,73 m, consulte pour une prise de poids rapide sans augmentation d'appétit et pour asthénie (difficultés à monter des escaliers). Elle se plaint également d'une augmentation de la pilosité du visage, de la ligne ombilico-pubienne et du dos, associée à une acné kystique rebelle qui a nécessité la prise de Roaccutane® (isotrétinoïne).
 L'examen clinique met en évidence :
 - Une obésité facio-tronculaire
 - Des vergetures pourpres
 - Une fragilité capillaire (lésion lors de ponctions veineuses) 
 - Un comblement des creux sus-claviculaires
 - Une pression artérielle à 170/100 mmHg.
 Dans ses antécédents, on relève : une primoinfection tuberculeuse à l'âge de 8 ans et une hépatite virale A.
 Résultats du bilan biologique sanguin effectué à jeun : 
 Biochimie :
 Pl Glucose : 6,1 mmol/L
 Pl Sodium : 146 mmol/L
 Pl Potassium : 3,0 mmol/L 
 Pl Bicarbonate : 30 mmol/L 
 Pl Chlorure : 100 mmol/L 
 Pl Calcium : 2,11 mmol/L 
 Se Protéines : 69 g/L
 Pl Phosphate : 1,02 mmol/L
 Pl Créatinine : 81 μmol/L
 Se Cholestérol total : 6,5 mmol/L 
 Se Triglycérides : 1,60 mmol/L
 Hémogramme :
 Sg Erythrocytes : 4,2 T/L
 Sg Leucocytes : 10,7 G/L
 Sg Hématocrite : 0,38
 Sg VGM : 91 fL
 Formule leucocytaire :
 Polynucléaires neutrophiles : 9,6 G/L 
 Polynucléaires éosinophiles : 0,02 G/L 
 Polynucléaires basophiles : 0,05 G/L 
 Monocytes : 0,05 G/L
 Lymphocytes : 0,93 G/L

Question : Quel diagnostic peut être envisagé au vu des signes cliniques et biologiques ?

**Réponse attendue**

Le diagnostic envisagé est un hypercorticisme (syndrome de Cushing) car : Prise de poids
 Syndrome dysmorphique (obésité faciotronculaire)
 Hyperandrogénie (hirsutisme-acné)
 Biologie : hyperglycémie à jeun, hypertriglycéridémie et hypercholestérolémie modérées - augmentation des bicarbonates (suspiscion d'alcalose métabolique), hypokaliémie, hypocalcémie (protéinémie normale), hyperleucocytose à polynucléaires neutrophiles - éosinopénie.

**Réponse générée**

Diabète insipide

### Exemple 5

**Instruction**

Cas clinique : Une femme de 64 ans, veuve depuis un an, ménopausée à 52, est mère de 2 enfants de 40 et 27 ans. Sa mère, atteinte d'un DNID est décédée à 78 ans d'un infarctus du myocarde.
 La malade consulte pour un intertigo (inflammation de la peau au niveau des plis) sous-mammaire et inguinal bilatéral. Elle pèse 80 kg pour 1,65 m et présente une obésité de type androïde. La malade dit faire des efforts pour perdre du poids qui s'est accru régulièrement depuis sa dernière maternité et qui a augmenté de 8 kg au cours des 3 dernières années. Depuis 6 mois environ, elle se plaint d'une asthénie physique et psychique inhabituelle, mais ne présente pas de syndrôme dépressif vrai. Elle ne fume pas mais peut boire de l'alcool à l'excès quand l'occasion se présente.
 L'examen clinique ne révèle aucune autre anomalie que les lésions cutanées et une HTA modérée, chiffrée à 150/100 mmHg, mesurée dans des conditions correctes de détermination. Le bilan biologique effectué le lendemain est le suivant :
 Pl Glycémie à jeun 8,60 mmol/L
 Pl Glycémie post-prandiale 12,76 mmol/L (N : 11,1 mmol/L)
 Se Cholestérol total 6,70 mmol/L
 Se Triglycérides 3,65 mmol/L
 L'aspect du sérum n'est pas précisé 
 Pl Créatinine 130 μmol/L
 Les enzymes hépatiques, l'hémogramme et l'exploration thyroïdienne sont normaux, de même que l'examen des urines, à l'exception d'une discrète cétonurie au moment de la consultation, alors que la malade était à jeun depuis la veille pour les examens sanguins.
 Le diagnostic retenu est celui de DNID.

Question : 6 mois plus tard, le bilan biologique est le suivant :
 Pl Glycémie à jeun 9,99 mmol/L
 Pl Glycémie post-prandiale 12,48 mmol/L (N : 11,1 mmol/L)
 Sg Hémoglobines glyquées 9 %
 Se Cholestérol total 5,93 mmol/L
 Se Triglycérides 1,82 mmol/L
 Pl Créatinine 170 μmol/L
 Protéinurie 0,15 g/24 h
 Commentez le bilan biologique
 Quelle attitude thérapeutique logique devra être adoptée ? Justifiez votre réponse.

**Réponse attendue**

Bien qu'il n'existe pas d'argument clinique ni biologique en faveur d'une évolution vers un diabète insulinodépendant, il est justifié d'instaurer une insulinothérapie afin d'améliorer le contrô1e glycémique qui n'a pas pu être établi par les hypoglycémiants oraux associés au régime. La présence d'une insuffisance rénale avec apparition d'une protéinurie justifie l'abandon des sulfamides hypoglycémiants au profit de l'insulinothérapie.

**Réponse générée**

 - Hypoglicidmie persistante avec hyperglycemies élevées après repas ;
 Hypercholestériorism , trigylcerides bas ou très faibles ; protéo-protium en raison probablement non seulement par insuffisance glycocydrène totale comme on poussait croire avant,
 augmentation significative survenue peu aprs début syndrome diabétique . Il y aurais donc lieu éventuellement envisager traitement anti-diabéticien .
 En cas confirmatoire il faut chercher cause chez cette patiente:
