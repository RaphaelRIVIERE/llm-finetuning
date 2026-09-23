# Test des paramètres de décodage vLLM, passage 2

Modèle : `runs/final`. Greedy (temperature=0), max_tokens=512.
Référence Transformers : colonne « Après DPO » de `docs/evaluation_dpo.md`.

## Configurations

- `frequence_0.3` : {'frequency_penalty': 0.3}
- `frequence_0.5` : {'frequency_penalty': 0.5}
- `frequence_0.7` : {'frequency_penalty': 0.7}

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

**frequence_0.3** (330 tokens, arrêt : stop)

 Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insuffisance cardiaque. Syndrome de l’insuffisance rénale aiguë avec syndrome de l’insufficience cardiaque. Syndrome d'hyperkaliémie et d'hypernatrémie (ou hypernatrémie et d'hyperkaliémie)

**frequence_0.5** (60 tokens, arrêt : stop)

 Syndrome de l’insuffisance rénale aiguë avec syndrome de l’hyperkaliémie et de l’acidose métabolique. La détresse respiratoire est due à une hyperkaliémie qui provoque une dépression musculaire.

**frequence_0.7** (64 tokens, arrêt : stop)

 Syndrome de l’insuffisance rénale aiguë avec syndrome de l’hyperkaliémie, de l’acidose métabolique et de la déshydratation. La détresse respiratoire est due à une insuffisance respiratoire aiguë.

## Exemple 2 (fr)

**Instruction**

Cas clinique : Dans une polyclinique de la région on s’intéresse à deux stratégies diagnostiques lors de la prise en charge d’une douleur thoracique chez des patients de 40 à 50 ans.La première concerne la  prise en charge de patients souffrant d’une douleur rétro sternale avec irradiation dans le bras gauche dans un service d’Urgences.La deuxième concerne la prise  en charge d’une douleur thoracique atypique sans signes associés en ambulatoire.On étudie les deux examens diagnostiques suivants : Electrocardiogramme et dosage des CPK.Résultats : Population de 100 personnes :Sur 75 patients ayant un diagnostic d’infarctus certifié, 68 patients ont eu un ECG positif et 64 un dosage des CPK positif.  Six patients indemnes de maladie coronarienne avaient un ECG positif et 7 un dosage de  CPK positifs.

Question : Dans le cadre d’une prise en charge en urgence, quelle serait votre stratégie de prescriptions des examens complémentaires ? Justifier.

**Réponse attendue**

En urgence, il faut obtenir le plus rapidement possible un diagnostic fiable, on réalisera donc un ECG et un dosage des enzymes cardiaques de façon simultanée (en parallèle).
Si l’un des deux tests est positif, le diagnostic est fait, a fortiori si les deux examens sont positifs. Par contre, si les deux examens sont négatifs, on s’orientera vers une autre piste.

**frequence_0.3** (69 tokens, arrêt : stop)

1) ECG : examen obligatoire en urgence car il est le plus rapide et le plus précis pour diagnostiquer un infarctus. 2) Dosage des CPK : examen obligatoire en urgence car il est le plus rapide et le plus précis pour diagnostiquer un infarctus.

**frequence_0.5** (69 tokens, arrêt : stop)

1) ECG : examen obligatoire en urgence car il est le plus rapide et le plus précis pour diagnostiquer un infarctus. 2) Dosage des CPK : examen obligatoire en urgence car il est le plus rapide et le plus précis pour diagnostiquer un infarctus.

**frequence_0.7** (69 tokens, arrêt : stop)

1) ECG : examen obligatoire en urgence car il est le plus rapide et le plus précis pour diagnostiquer un infarctus. 2) Dosage des CPK : examen obligatoire en urgence car il est le plus rapide et le plus précis pour diagnostiquer une myopatie.

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

**frequence_0.3** (45 tokens, arrêt : stop)

L’allaitement maternel est recommandé. Il est important de le pratiquer dès la naissance. Il est recommandé de pratiquer l’allaitement maternel en allant au lait maternel.

**frequence_0.5** (57 tokens, arrêt : stop)

L’allaitement maternel est recommandé. Il est important de le pratiquer dès la naissance. Il est conseillé de pratiquer l’allaitement maternel en allant au lait maternel, en préférant le lait maternel frais.

**frequence_0.7** (76 tokens, arrêt : stop)

L’allaitement maternel est recommandé. Il est important de le pratiquer dès la naissance et de le faire avec un soutien vocal. La mère doit être informée des risques pour la santé du fœtus, notamment en cas d’hyperglycémie maternelle ou d’hyperinsulinémie maternelle.

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

**frequence_0.3** (7 tokens, arrêt : stop)

Diabète insipide

**frequence_0.5** (7 tokens, arrêt : stop)

Diabète insipide

**frequence_0.7** (7 tokens, arrêt : stop)

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

**frequence_0.3** (143 tokens, arrêt : stop)

 La glycémie à jeun et post-prandiale sont augmentées, la créatinine est augmentée, la protéinurie est présente. Il s'agit d'une hyperglycémie diabétique, probablement de type 2. La malade est obèse et présente une HTA. Le bilan biologique montre une hyperglycémie diabétique de type 2 avec un syndrome hyperinsulinémique (hyperglycémie à jeun et post-prandiale) et une insuffisance rénale (créatininurie). Il faut donc envisager un traitement par l'insuline.

**frequence_0.5** (134 tokens, arrêt : stop)

 La glycémie à jeun et post-prandiale sont augmentées, la créatinine est augmentée, la protéinurie est présente. Il s'agit d'une hyperglycémie diabétique, probablement de type 2. L'hyperglycémie diabétique de type 2 est associée à une hypercholestérolémie et à une protéinurie. La malade doit être traitée par un régime hypocalorique (1500 kcal/j) et par un traitement médicamenteux adapté (insuline ou antidiabétiques oraux).

**frequence_0.7** (96 tokens, arrêt : stop)

 La glycémie à jeun et post-prandiale sont augmentées, la créatinine est augmentée, la protéinurie est présente. Il s'agit d'une hyperglycémie diabétique. La malade doit être hospitalisée pour réaliser un suivi clinique et biologique régulier, une surveillance de l'évolution de la protéinurie et une surveillance des complications cardio-vasculaires.

## Exemple 6 (en)

**Instruction**

What are the treatments for Arginase deficiency ?

**Réponse attendue**

How might arginase deficiency be treated? The treatment and management of arginase deficiency is generally focused on lowering arginine levels and preventing hyperammonemia (an accumulation of ammonia in the blood). This may be accomplished through dietary modifications and the use of certain medications (called nitrogen-scavenging drugs) under the supervision of a medical team with experience treating metabolic conditions. More specifically, people affected by arginase deficiency must restrict dietary protein and arginine. This is often achieved with the use of specialized formulas, which may account for half or more of protein intake. Although people with arginase deficiency are less prone to episodes of severe hyperammonemia than people affected by other urea cycle disorders, special treatment is needed should these episodes occur. During an episode, affected people are generally treated in the hospital and may require dialysis, nitrogen-scavenging medications, intravenous (IV) fluids/feeds and/or other treatments. These treatments are administered with the goal of rapidly reducing blood ammonia levels and preventing neurological damage. GeneReviews offers more specific information on the treatment of arginase deficiency and urea cycle disorders, in general. Please click on the links to access these resources.

**frequence_0.3** (107 tokens, arrêt : stop)

How might arginase deficiency be treated? Arginase deficiency is a rare condition that is characterized by a buildup of urea in the blood (hyperuricemia) and a buildup of ammonia in the blood (hyperammonemia). The condition is caused by mutations in the ARG1 gene and is inherited in an autosomal recessive manner. Treatment for arginase deficiency focuses on managing the symptoms of hyperuricemia and hyperammonemia. Treatment may include dietary changes, medications, and/or other therapies.

**frequence_0.5** (178 tokens, arrêt : stop)

How might arginase deficiency be treated? Arginase deficiency is a rare condition that is characterized by a buildup of urea in the blood (hyperuricemia) and a shortage of urea in the urine (oliguria). The condition is caused by mutations in the ARG1 gene, which provides instructions for making an enzyme called arginase. This enzyme plays an important role in breaking down a chemical called arginine, which is found in many foods. Arginine is also used to make other important molecules such as proteins and hormones.  Arginase deficiency can be treated with medications that help remove excess urea from the body. These medications include sodium phenylbutyrate, sodium phenylacetate, and sodium or potassium orotate. These medications are usually given intravenously (through a vein) and are most effective when given early in life.

**frequence_0.7** (118 tokens, arrêt : stop)

How might arginase deficiency be treated? Arginase deficiency is a rare condition that is characterized by a buildup of urea in the blood (hyperuricemia) and an accumulation of ammonia in the brain (encephalopathy). The treatment for arginase deficiency depends on the severity of the condition. In mild cases, treatment may consist of dietary changes to reduce protein intake, which can help reduce hyperuricemia. In more severe cases, treatment may include medications to lower ammonia levels in the blood and/or provide nutritional support through feeding tubes or parenteral nutrition.

## Exemple 7 (en)

**Instruction**

What is (are) Amniotic band syndrome ?

**Réponse attendue**

Amniotic band syndrome refers to a condition in which bands extend from (and originating from) the inner lining of the amnion. The amnion is the sac that surrounds the baby in the womb. As the baby develops in the womb, its extremities may become entangled in the amniotic band resulting in constriction or even amputation. When this happens the baby is said to have amniotic band syndrome. Amniotic bands are thought to happen sporadically or in association with trauma to the abdomen. It can be a complication after an amniocentesis and/or it can indicate early rupture of the amniotic sac.

**frequence_0.3** (111 tokens, arrêt : stop)

Amniotic band syndrome (ABS) is a condition that occurs when bands of the amniotic sac, which surrounds and protects the fetus, become entangled around the fetus's limbs or other body parts. The bands can cause severe limb deformities, such as clubfoot or missing fingers and toes. In some cases, the bands can also cause malformations of the face, heart, and other organs. ABS is usually diagnosed during pregnancy by ultrasound. Treatment depends on the severity of the condition and may include surgery to correct limb deformities.

**frequence_0.5** (127 tokens, arrêt : stop)

Amniotic band syndrome (ABS) is a condition that occurs when bands of the amniotic sac, which surrounds and protects the fetus, become entangled around the fetus's limbs or other body parts. The bands can cause severe limb deformities, such as clubfoot or missing fingers and toes. In some cases, ABS can also affect the face, head, or internal organs. The severity of ABS varies depending on which parts of the body are affected.  ABS is usually diagnosed during pregnancy by ultrasound imaging. Treatment depends on the severity of the condition and may include surgery to remove the bands and correct limb deformities.

**frequence_0.7** (79 tokens, arrêt : stop)

Amniotic band syndrome (ABS) is a condition that occurs when bands of the amniotic sac, which surrounds and protects the fetus, become entangled around the fetus's limbs or other body parts. The bands can cause severe limb deformities and other birth defects. ABS is usually diagnosed during pregnancy by ultrasound. Treatment may include surgery to remove the bands and correct limb deformities.

## Exemple 8 (en)

**Instruction**

How many people are affected by neonatal onset multisystem inflammatory disease ?

**Réponse attendue**

NOMID is a very rare disorder; approximately 100 affected individuals have been reported worldwide.

**frequence_0.3** (20 tokens, arrêt : stop)

Neonatal onset multisystem inflammatory disease is a rare condition; its exact prevalence is unknown.

**frequence_0.5** (20 tokens, arrêt : stop)

Neonatal onset multisystem inflammatory disease is a rare condition; its exact prevalence is unknown.

**frequence_0.7** (20 tokens, arrêt : stop)

Neonatal onset multisystem inflammatory disease is a rare condition; its exact prevalence is unknown.

## Exemple 9 (en)

**Instruction**

What is the outlook for Arteriovenous Malformation ?

**Réponse attendue**

The greatest potential danger posed by AVMs is hemorrhage. Most episodes of bleeding remain undetected at the time they occur because they are not severe enough to cause significant neurological damage. But massive, even fatal, bleeding episodes do occur. Whenever an AVM is detected, the individual should be carefully and consistently monitored for any signs of instability that may indicate an increased risk of hemorrhage. Individuals who are treated require brain imaging afterwards to evaluate if the AVM has been completely removed or destroyed. The risk of hemorrhage remains if some of the AVM persists despite treatment.

**frequence_0.3** (59 tokens, arrêt : stop)

The prognosis for patients with an arteriovenous malformation depends on the size and location of the malformation. Small malformations may not cause any symptoms and may be discovered incidentally during a physical exam or imaging study. Larger malformations may cause symptoms and may require treatment.

**frequence_0.5** (57 tokens, arrêt : stop)

The prognosis for patients with an arteriovenous malformation depends on the size and location of the malformation. Small, asymptomatic malformations may not require treatment. Larger or symptomatic malformations may be treated with surgery, embolization, or radiosurgery.

**frequence_0.7** (57 tokens, arrêt : stop)

The prognosis for patients with an arteriovenous malformation depends on the size and location of the malformation. Small, asymptomatic malformations may not require treatment. Larger or symptomatic malformations may be treated with surgery, embolization, or radiosurgery.

## Exemple 10 (en)

**Instruction**

What is (are) Gum (Periodontal) Disease ?

**Réponse attendue**

Gum disease is an infection of the tissues that hold your teeth in place. In its early stages, it is usually painless, and many people are not aware that they have it. But in more advanced stages, gum disease can lead to sore or bleeding gums, painful chewing problems, and even tooth loss.

**frequence_0.3** (248 tokens, arrêt : stop)

Gum disease is a common disease that affects the gums and the bone that supports your teeth. It is caused by plaque, a sticky film of bacteria that constantly forms on teeth. If plaque is not removed, it hardens into tartar, which can only be removed by a dental professional. Plaque irritates the gums and causes them to become red, swollen, and tender. If left untreated, gum disease can lead to tooth loss.    There are two types of gum disease: gingivitis and periodontitis. Gingivitis is the milder form of gum disease. It causes red, swollen gums that bleed easily when brushing or flossing. Gingivitis can be reversed with good oral hygiene and regular dental cleanings. Periodontitis is the more serious form of gum disease. It causes gums to pull away from the teeth and expose the roots, which can lead to tooth loss. Periodontitis cannot be reversed but can be treated with deep cleaning procedures called scaling and root planing.    The best way to prevent gum disease is to maintain good oral hygiene by brushing twice a day with fluoride toothpaste and flossing daily. Regular dental checkups are also important for early detection of gum disease.

**frequence_0.5** (350 tokens, arrêt : stop)

Gum disease is a common condition that affects the gums and the bone that supports your teeth. It is caused by plaque, a sticky film of bacteria that constantly forms on teeth. If not removed by brushing and flossing, plaque hardens into tartar (calculus), which can only be removed by a dental professional. Plaque and tartar irritate the gums, causing them to become red, swollen, and prone to bleeding. If left untreated, gum disease can lead to tooth loss.    There are two types of gum disease: gingivitis and periodontitis. Gingivitis is the milder form of gum disease; it causes red, swollen gums that bleed easily. If you have gingivitis, your dentist or hygienist can usually treat it with improved brushing and flossing techniques or with professional dental cleanings to remove plaque and tartar from your teeth.    Periodontitis is the more serious form of gum disease; it causes bone loss around the teeth that leads to loose teeth and eventually tooth loss. It may also cause receding gums (gums that pull away from your teeth). Periodontitis cannot be treated by brushing or flossing alone; it requires deep cleaning under local anesthesia performed by a dentist or periodontist (a dentist who specializes in treating gum disease).    The good news is that you can prevent both gingivitis and periodontitis if you brush twice daily with fluoride toothpaste, floss daily, use an antimicrobial mouth rinse as recommended by your dentist or hygienist, eat a healthy diet low in sugar, avoid smoking or using tobacco products, visit your dentist regularly for professional cleanings every six months, and maintain good oral hygiene at home.

**frequence_0.7** (395 tokens, arrêt : stop)

Gum disease is a common condition that affects the gums and bone that support your teeth. It is caused by plaque, a sticky film of bacteria that constantly forms on teeth. If not removed by brushing and flossing, plaque hardens into tartar (calculus), which can only be removed by a dental professional. Plaque and tartar irritate the gums, causing them to become red, swollen, and prone to bleeding. If left untreated, gum disease can lead to tooth loss.
                
The two main types of gum disease are gingivitis and periodontitis.
                
Gingivitis
                
Gingivitis is the milder form of gum disease. It causes redness, swelling, or bleeding in the gums when you brush or floss your teeth. Gingivitis usually does not cause pain or affect your ability to chew or speak normally.
                
Periodontitis
                
Periodontitis is more serious than gingivitis. It causes inflammation in the tissues that hold teeth in place (the gums and bone). As periodontitis progresses, it can destroy these tissues and lead to loose teeth or tooth loss.
                
Causes
                
Plaque buildup is the main cause of both gingivitis and periodontal disease.
                
Other factors that may increase your risk for gum disease include:
                
Poor oral hygiene
                
Tobacco use
                
Diabetes
                
Hormonal changes (such as those during pregnancy)
                
Certain medications (such as some blood pressure medicines)
                
Genetics
                

                
Treatment Options for Gum Disease
                
Treatment depends on how severe the condition is:
                
                
- Gingivitis: Brushing twice daily with fluoride toothpaste; flossing daily; using an antimicrobial mouth rinse; eating a healthy diet; quitting smoking if you smoke; seeing your dentist regularly for professional cleanings  - Moderate periodontal disease: Scaling and root planing  - Severe periodontal disease: Scaling and root planing plus antibiotics
