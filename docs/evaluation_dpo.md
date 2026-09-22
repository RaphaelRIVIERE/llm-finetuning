# Évaluation DPO : avant / après

Avant : `runs/sft/complet/checkpoint-500` (SFT seul). Après : `runs/dpo/complet/checkpoint-250` (SFT + DPO).

Génération avec repetition_penalty=1.3, no_repeat_ngram_size=3.

## Exemple 1 (fr)

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

**Avant DPO (SFT seul)**

 Syndrome inflammatoire sérique (SIS) avec syndrome infectieux à pneumocystose
- Crépitation sur auscultaition 
 - Anémie hypochromique / macrocytaire , hyperleucocytoïde

**Après DPO**

 Syndrome inflammatoire sérique (SIS) avec syndrome infectieux à pneumocystose
- Crépitation sur auscultaition 
 - Anémie hypochromique mégaloblastique associée aux anticoquimines  
Justification :
Les critères suivant peuvent être présentés dans un S.I.S:
1 – Hypoxia: signes tachycardies , bradypnée ou hypercapnie . Signaux vitaux diminuées .
Signs of shock and sepsis with respiratory distress or failure in the presence o f pulmonary infiltrates on chest x-ray

ou 

signa s i nfluenzales :

Fever; cough ; dysphonia;
leucopenic / lymphopénodica ;
anorexia ;

et aussi:

Anuria;

Le fait que ce soit chez quelq ue personne ayant déjà été traiter e contre Pneumoccystosis c’est qu’il existe bien ici quelque chose qui va nous faire pens er là dessus .

Autres diagnostics possibles mais moins probables car pas justifi es selon nos données ci-dessous
 
Infection bactérieuse grave 
 
Meningoencefalopath ie

## Exemple 2 (fr)

**Instruction**

Cas clinique : Dans une polyclinique de la région on s’intéresse à deux stratégies diagnostiques lors de la prise en charge d’une douleur thoracique chez des patients de 40 à 50 ans.La première concerne la  prise en charge de patients souffrant d’une douleur rétro sternale avec irradiation dans le bras gauche dans un service d’Urgences.La deuxième concerne la prise  en charge d’une douleur thoracique atypique sans signes associés en ambulatoire.On étudie les deux examens diagnostiques suivants : Electrocardiogramme et dosage des CPK.Résultats : Population de 100 personnes :Sur 75 patients ayant un diagnostic d’infarctus certifié, 68 patients ont eu un ECG positif et 64 un dosage des CPK positif.  Six patients indemnes de maladie coronarienne avaient un ECG positif et 7 un dosage de  CPK positifs.

Question : Dans le cadre d’une prise en charge en urgence, quelle serait votre stratégie de prescriptions des examens complémentaires ? Justifier.

**Réponse attendue**

En urgence, il faut obtenir le plus rapidement possible un diagnostic fiable, on réalisera donc un ECG et un dosage des enzymes cardiaques de façon simultanée (en parallèle).
Si l’un des deux tests est positif, le diagnostic est fait, a fortiori si les deux examens sont positifs. Par contre, si les deux examens sont négatifs, on s’orientera vers une autre piste.

**Avant DPO (SFT seul)**

Électro cardiomodélisation (ECM) ou électrophysiologie du cœur

**Après DPO**

Électro cardiomodélisation (ECM) ou électrophysiologie par cathétérisme veineux droit

## Exemple 3 (fr)

**Instruction**

Cas clinique : Interne en pédiatrie à Nantes, vous effectuez le premier examen clinique de Malo, d’origine bretonne, né la veille à 38 semaines et 3 jours de vie. Son poids de naissance est de 3,310 kg.Ce bébé, 1er enfant, est né par siège après un travail de 9 heures. Aucune anomalie n’avait été notée lors du diagnostic anténatal.

Question : La maman a choisi sous nos conseils d’effectuer un allaitement maternel. Quels conseils donnez-vous à la mère vis-à-vis de l’allaitement maternel ?

**Réponse attendue**

Réaliser l’allaitement avec des horaires souples . En général une tétée toutes les 2 ou 3 heures  au début.
Pendant les tétées : installation confortable , la bouche du nouveau-né doit prendre correctement l’aréole  et non le seul mamelon
Donner les 2 seins à chaque tétée 
Hygiène de vie  : boissons abondantes , alimentation variée  et riche en protéines  et en calcium , prohiber tabac , alcool  et excitants (café, thé), 
lavage quotidien des seins  à l’eau et au savon, protéger les mamelons avec une compresse sèche   pour éviter la macération.

**Avant DPO (SFT seul)**

L'allattement doit être initié dès que possible (au plus tard au bout des premières journées). Il faut éviter les séances prolongées avec une seule mamelle pour ne pas diminuer ou arrêter complètements son désir.
Il convient également :
• De faire appel aux techniques spécifiques qui permettent notamment:
– Une bonne position mammaire
 – Un bon contact entre papa/maman/baby 
 • D'assurer régulièrement ses soins hygiendosurfaces

**Après DPO**

L'allattement doit être initié dès que possible (au plus tard au bout des premières journées). Il faut donc faire appel aux services spécialisés pour obtenir une aide psychologico-pédagogiques.
La fréquence quotidienne recommandable sera entre deux ou trois fois/jour pendant les quatre mois qui suivent
Le nombre total estimatif journalier peut aller jusqu'à cinq litres 
Il ne faudra pas s'interrompre dans son accouchement car cela pourrait entraîner :
• Une diminution importante rapide mais transitoire,
 • Un retard important sur ce plan

## Exemple 4 (fr)

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

**Avant DPO (SFT seul)**

Diabète insipide

**Après DPO**

Diabète insipide

## Exemple 5 (fr)

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

**Avant DPO (SFT seul)**

 - Hypoglicidmie persistante avec hyperglycemies élevées après repas ;
 Hypercholestériorismos , trigylcerides bas ou très faibles ; protéo-protium en raison probablement non seulement par insuffisance glycocydrène totale comme on poussait croire avant .

**Après DPO**

 - Hypoglicidmie persistante avec hyperglycemies élevées après repas ;
 Hypercholestériorismos , trigylcerides bas ou très faibles ; protéo-protium en raison probablement non seulement par insuffisance glomérioleuse due aux complications métabolisques liées notamment à son syndrome diabétique butyrique .
 Insufi-scence fonctionnelle renale .

## Exemple 6 (en)

**Instruction**

What are the treatments for Arginase deficiency ?

**Réponse attendue**

How might arginase deficiency be treated? The treatment and management of arginase deficiency is generally focused on lowering arginine levels and preventing hyperammonemia (an accumulation of ammonia in the blood). This may be accomplished through dietary modifications and the use of certain medications (called nitrogen-scavenging drugs) under the supervision of a medical team with experience treating metabolic conditions. More specifically, people affected by arginase deficiency must restrict dietary protein and arginine. This is often achieved with the use of specialized formulas, which may account for half or more of protein intake. Although people with arginase deficiency are less prone to episodes of severe hyperammonemia than people affected by other urea cycle disorders, special treatment is needed should these episodes occur. During an episode, affected people are generally treated in the hospital and may require dialysis, nitrogen-scavenging medications, intravenous (IV) fluids/feeds and/or other treatments. These treatments are administered with the goal of rapidly reducing blood ammonia levels and preventing neurological damage. GeneReviews offers more specific information on the treatment of arginase deficiency and urea cycle disorders, in general. Please click on the links to access these resources.

**Avant DPO (SFT seul)**

How might argininases be treated? There is no cure or treatment available. Treatment may include a low-protein diet, and/or dialysis to remove excess urea from blood plasma in people with severe kidney failure (end-stage renal disease).

**Après DPO**

How might argininases be treated? There is no cure or treatment available. Treatment of affected individuals may include a low-protein diet, avoidance and/or reduction in exposure to sources that can cause an increase (hyperarginemia) such as certain medications; dialysis if kidney failure occurs early on due to hyper-arginine nephropathy which has been reported with this condition but not well documented

## Exemple 7 (en)

**Instruction**

What is (are) Amniotic band syndrome ?

**Réponse attendue**

Amniotic band syndrome refers to a condition in which bands extend from (and originating from) the inner lining of the amnion. The amnion is the sac that surrounds the baby in the womb. As the baby develops in the womb, its extremities may become entangled in the amniotic band resulting in constriction or even amputation. When this happens the baby is said to have amniotic band syndrome. Amniotic bands are thought to happen sporadically or in association with trauma to the abdomen. It can be a complication after an amniocentesis and/or it can indicate early rupture of the amniotic sac.

**Avant DPO (SFT seul)**

Amniotic bands are fibrous cords of tissue that form in the amnion, which surrounds and protects a developing fetus. These fibers can wrap around an unborn baby's limbs or other body parts as they grow inside their mother’s womb during pregnancy; this condition may cause limb deformities such as clubfoot if not treated early enough to prevent permanent damage before birth occurs.
                
The exact causes for these abnormal tissues forming within pregnant women' wombs remain unknown but researchers believe it could be related with genetic factors associated specificallywith certain ethnic groups like African Americansand Hispanics/Latinosor possibly due environmental exposuresduring gestationsuchas infectionsfrom bacteria viruses parasites fungi chemicals radiation drugs medications toxins etc..

**Après DPO**

Amnion bands are fibrous cords of tissue that form around the developing fetus during pregnancy. They can cause a variety or birth defects, including limb abnormalities and other malformations such as heart disease; however they may not be associated with any specific condition in some cases.The exact mechanism by which amnio-ticbands develop remains unknown but it has been suggested to involve abnormal implantation into an area where there was previously no placenta formation resulting from failure for one sideofthe uterusto grow normally after fertilization.Amniocentesisis usually performed between 10-25 weeks gestational age when fetal growths have reached about half their final size at full term.This procedure involves insertinga thin needle through abdominal wall skinandintoamembraintosextractfetal fluidwhichcanbe analyzedfor genetic disordersor chromosomalabnormalities.Ifan abnormally large amount offetalfiuldissolvesintheneedle tipbeforeit reachesthefetus,the riskoffebrile convulsionsduring surgery increases significantly.Thus,in order toprevent this complication,a small incision isthroughout thenearby uterine muscle layer before extracting fetafluidfrom themembrane.In addition,tobeforementioned risks,further complications include infection

## Exemple 8 (en)

**Instruction**

How many people are affected by neonatal onset multisystem inflammatory disease ?

**Réponse attendue**

NOMID is a very rare disorder; approximately 100 affected individuals have been reported worldwide.

**Avant DPO (SFT seul)**

Neonatal ONMD is a rare condition; its exact prevalence has not been determined.

**Après DPO**

The exact prevalence of NOMID is unknown. It has been estimated that 1 in every million newborns may have this condition, but the true incidence could be as high or lower than these estimates because some cases go undiagnosed and others with milder signs might not meet diagnostic criteria for a diagnosis such as systemic juvenile idiopathic arthritis (SJIA).

## Exemple 9 (en)

**Instruction**

What is the outlook for Arteriovenous Malformation ?

**Réponse attendue**

The greatest potential danger posed by AVMs is hemorrhage. Most episodes of bleeding remain undetected at the time they occur because they are not severe enough to cause significant neurological damage. But massive, even fatal, bleeding episodes do occur. Whenever an AVM is detected, the individual should be carefully and consistently monitored for any signs of instability that may indicate an increased risk of hemorrhage. Individuals who are treated require brain imaging afterwards to evaluate if the AVM has been completely removed or destroyed. The risk of hemorrhage remains if some of the AVM persists despite treatment.

**Avant DPO (SFT seul)**

The prognosis (chance of recovery) depends on whether a person has symptoms and how severe they are. Some people have no signs or problems, while others may develop seizures that can be life-threatening if not treated promptly with anticonvulsant medications.
                
People who do well after surgery usually recover completely without any long-term effects from their condition; however some patients experience neurological deficits such as weakness in one sideofthe bodyor difficulty walkingand these conditions often require ongoing treatment to prevent recurrence

**Après DPO**

The prognosis (chance of recovery) depends on whether a patient has symptoms and how severe they are. Some people with AVMs have no signs or problems, while others may develop serious complications such as stroke due to bleeding in an AVM that blocks blood flow from one side ot he brain.
                
People who do not experience any health issues relatedto their arteriovenular malformations generally recover fully after surgeryor other treatment if needed

## Exemple 10 (en)

**Instruction**

What is (are) Gum (Periodontal) Disease ?

**Réponse attendue**

Gum disease is an infection of the tissues that hold your teeth in place. In its early stages, it is usually painless, and many people are not aware that they have it. But in more advanced stages, gum disease can lead to sore or bleeding gums, painful chewing problems, and even tooth loss.

**Avant DPO (SFT seul)**

Gum disease, also called periodontitis or gingivitis. It's a common condition that affects millions of people in the United States and worldwide.
                
The gums are soft tissue around your teeth where they meet inside each jawbone to form tooth sockets; these tissues hold up on topof themthe enamel-covered crownsof our natural white front-facing incisorsand two rows behindthemour back molarsor premolarswhich we call caninesin between 28incisorsto fourmolarstotaling about14teeththat makeup all adult humans' jawsfrom age30to59years oldas well as wisdom teething which begins at this same time but ends when you're67 yearsoldon averagefor most adultswho have had no dental problems before thenbut it does not affect childrens mouthsat any stage during their developmentbecause there aren't enough permanent ones yet for usadultsmust wait until after birthwhen both sets come togetherinto one setwith only six more baby bits leftoverbefore going through pubertywhereby everyones mouth will be filled with twenty eightpermanent morselsafterwardsuntil reaching adulthoodwherethey'll still need regular checkups from dentists who specialize innurseryears-oldchildrenwhose parents should take

**Après DPO**

Gum disease, also called periodontitis or gum infection and sometimes referred to as "gummy" jaw syndrome because of the appearance it can cause in some people. It occurs when plaque builds up along your teeth's roots below their surfaces where they meet gums.
                
Plaque buildup causes inflammation that leads eventually into bone loss around each tooth which may result from a breakdown caused by bacteria within pockets between them & surrounding tissues; this condition results if you do not remove these harmful substances through regular brushing with fluoride-containing products such an electric-activated brushes designed for cleaning undercuts on lower molars;
                
                
The two main types are:
                

                 - Gingivitis
                
                The first stage involves redness , swelling  bleeding easily during flossing . If left untreated gingival diseases progresses slowly over years until irreversible damage has occurred before symptoms become apparent .
               
              

              
              More information about how we treat dental problems related specificallyto Periodontology
