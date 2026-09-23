# Test des paramètres de décodage vLLM, passage 3

Modèle : `runs/final`. Greedy (temperature=0), max_tokens=512.
Questions libres écrites à la main, sans réponse attendue : on juge la forme, pas la justesse médicale.

## Configurations

- `frequence_0.5` : {'frequency_penalty': 0.5}
- `frequence_0.5_repetition_1.1` : {'frequency_penalty': 0.5, 'repetition_penalty': 1.1}
- `frequence_0.5_presence_0.5` : {'frequency_penalty': 0.5, 'presence_penalty': 0.5}

## Exemple 1 (fr)

**Instruction**

J'ai 35 ans avec des douleur en bas du dos, douleur a l'épaule et au genoux. Quel diagnostic peut être envisagé au vu des signes cliniques et biologiques ?

**frequence_0.5** (41 tokens, arrêt : stop)

- Syndrome de l'os intervertébral 
- Syndrome de la rotule 
- Syndrome de l'os intertrochanterique 
- Syndrome de la fémoroacetabulaire

**frequence_0.5_repetition_1.1** (26 tokens, arrêt : stop)

- Syndrome de la colonne vertébrale 
 - syndrome d'entropion
 - tendinite ou entorse

**frequence_0.5_presence_0.5** (30 tokens, arrêt : stop)

- Syndrome de l'os intervertébral 
- Syndrome de la rotule 
- Syndrome de l'os intertrochanterique

## Exemple 2 (fr)

**Instruction**

Homme de 35 ans avec des douleur en bas du dos, douleur a l'épaule et au genoux. Quel diagnostic peut être envisagé au vu des signes cliniques et biologiques ?

**frequence_0.5** (42 tokens, arrêt : stop)

- Syndrome de l'os intervertébral 
- Syndrome de l'os intervertebral avec syndrome de la jambe
- Syndrome de l'os intervertebral avec syndrome du genou

**frequence_0.5_repetition_1.1** (15 tokens, arrêt : stop)

- Syndrome d'entropion 
 - syndrome de la rotule

**frequence_0.5_presence_0.5** (30 tokens, arrêt : stop)

- Syndrome de l'os intervertébral 
- Syndrome de la rotule 
- Syndrome de l'os intertrochanterique

## Exemple 3 (fr)

**Instruction**

J'ai 58 ans, je fume, et j'ai une douleur dans la poitrine qui serre et qui descend dans le bras gauche depuis 30 minutes. Qu'est-ce que j'ai ?

**frequence_0.5** (43 tokens, arrêt : stop)

Il s'agit d'un signe de crise aiguë de myocardique. Il faut immédiatement aller au plus proche cabinet de cardiologie ou au plus proche hôpital.

**frequence_0.5_repetition_1.1** (81 tokens, arrêt : stop)

Il s'agit d'un signe de crise aiguë de myocardique (CMA) ou syndrome coronarien aigu.
Lorsqu'il n'y a pas d'anomalies métaboliques ni des troubles du rythme cardiaque, il faut envisager un arrêt ventriculaire droit à gauche par rupture artérielle coronaire droite.

**frequence_0.5_presence_0.5** (43 tokens, arrêt : stop)

Il s'agit d'un signe de crise aiguë de myocardique. Il faut immédiatement aller au plus proche cabinet de cardiologie ou au plus proche hôpital.

## Exemple 4 (fr)

**Instruction**

Homme de 58 ans, fumeur, douleur thoracique constrictive irradiant dans le bras gauche depuis 30 minutes. Quel diagnostic évoquer ?

**frequence_0.5** (7 tokens, arrêt : stop)

Pneumothorax

**frequence_0.5_repetition_1.1** (7 tokens, arrêt : stop)

Pneumothorax

**frequence_0.5_presence_0.5** (7 tokens, arrêt : stop)

Pneumothorax

## Exemple 5 (fr)

**Instruction**

J'ai 45 ans et d'un coup j'ai eu un mal de tête très violent, le pire de ma vie, avec envie de vomir. Qu'est-ce que ça peut être ?

**frequence_0.5** (69 tokens, arrêt : stop)

C'est probablement un mal de crâne, qui peut être dû à une tension artérielle élevée, à un stress, à une intoxication par des substances toxiques (alcool, drogues), à une infection (influenza, sinusite), à un traumatisme cranio-cérébral.

**frequence_0.5_repetition_1.1** (41 tokens, arrêt : stop)

Cela pourrait être une crise cardiaque (ou arrêt du cœur). Il faut aller immédiatement chez votre médecin traitant ou au plus vite à l'hôpital.

**frequence_0.5_presence_0.5** (34 tokens, arrêt : stop)

C'est probablement un mal de crâne, qui peut être dû à une tension artérielle élevée, à un stress ou à une infection.

## Exemple 6 (fr)

**Instruction**

Femme de 45 ans, céphalée brutale en coup de tonnerre, d'intensité maximale d'emblée, avec nausées. Quel diagnostic évoquer ?

**frequence_0.5** (10 tokens, arrêt : stop)

Trombophlébite aortique

**frequence_0.5_repetition_1.1** (10 tokens, arrêt : stop)

Trombophlébite aortique

**frequence_0.5_presence_0.5** (10 tokens, arrêt : stop)

Trombophlébite aortique

## Exemple 7 (fr)

**Instruction**

J'ai 25 ans, j'ai le nez qui coule, mal à la gorge et un peu de fièvre depuis 2 jours. Qu'est-ce que j'ai ?

**frequence_0.5** (54 tokens, arrêt : stop)

Si vous avez un nez qui coule, mal à la gorge et une fièvre, il est probable que vous souffrez d'une infection respiratoire aiguë. Il s'agit d'une infection bactérienne qui peut être grave.

**frequence_0.5_repetition_1.1** (83 tokens, arrêt : stop)

Si vous avez des symptômes d'une grippe ou d'un rhume (fièvre, toux, fatigue), il est important de prendre soin de votre hygiène respiratoire : port du masque en cas de contact avec une personne atteinte ; lavage régulier des mains par désinfection au savon et à l'eau pendant plus de 10 secondes.

**frequence_0.5_presence_0.5** (160 tokens, arrêt : stop)

Si vous avez un nez qui coule, mal à la gorge et une fièvre, il est probable que vous souffrez d'une infection respiratoire aiguë. La plupart des infections respiratoires aiguës sont bénignes et se guérissent sans traitement. Cependant, si votre fièvre persiste ou s'aggrave, ou si vous présentez d'autres symptômes graves comme des douleurs thoraciques, une toux persistante avec du sang ou de la muqueuse, un état général défavorable (perte de poids significative en raison d'une toux chronique) ou une dyspnée (difficulté à respirer), consultez immédiatement un médecin.

## Exemple 8 (fr)

**Instruction**

Homme de 25 ans, rhinorrhée, odynophagie et fébricule depuis 2 jours. Quel diagnostic évoquer ?

**frequence_0.5** (7 tokens, arrêt : stop)

Gingivostomatite

**frequence_0.5_repetition_1.1** (7 tokens, arrêt : stop)

Gingivostomatite

**frequence_0.5_presence_0.5** (7 tokens, arrêt : stop)

Gingivostomatite

## Exemple 9 (en)

**Instruction**

I'm 30 and I have a fever, a stiff neck and a bad headache, and light hurts my eyes. What do I have?

**frequence_0.5** (71 tokens, arrêt : stop)

You may have meningitis, a serious infection of the membranes that cover the brain and spinal cord. Meningitis can be caused by bacteria, viruses, fungi or parasites. Bacterial meningitis is the most serious type of meningitis and can be fatal if not treated promptly. Viral meningitis is less severe but can still cause serious complications.

**frequence_0.5_repetition_1.1** (105 tokens, arrêt : stop)

You may be suffering from meningitis, an infection of the membranes that cover your brain and spinal cord (meninges). Meningitis can cause severe headaches; nausea or vomiting; sensitivity to light; confusion; drowsiness; loss of balance or coordination; seizures; and/or a rash called petechiae - small red dots on the skin caused by bleeding under the surface. If you think you might have meningitis, call your doctor right away for advice about whether it's safe to go home with antibiotics alone.

**frequence_0.5_presence_0.5** (309 tokens, arrêt : stop)

You may have meningitis, a serious infection of the membranes that cover and protect the brain and spinal cord. Meningitis can be caused by bacteria, viruses or fungi. Bacterial meningitis is more common in children and young adults than in older people. Viral meningitis is more common in older people. Fungal meningitis is rare but can occur in people with weakened immune systems.    Signs of bacterial meningitis include         - A high fever    - A stiff neck    - A severe headache that doesn't go away    - Nausea and vomiting    - Confusion or drowsiness     - Slight sensitivity to light (photophobia)        Signs of viral meningitis include         - A high fever    - A stiff neck    - A severe headache that doesn't go away    - Nausea and vomiting     Viral meningitis usually clears up on its own within 7 to 10 days without treatment. However, you should see your doctor if you have any of these signs:         - High fever for more than 24 hours     - Severe headache     - Confusion or drowsiness       You should also see your doctor if you have any of these symptoms:         - Trouble walking or balance problems     - Seizures       Your doctor will do a physical exam, take a medical history and order tests to diagnose the cause of your symptoms. These tests may include blood tests, a lumbar puncture (spinal tap), an MRI scan or CT scan, and/or an X-ray.

## Exemple 10 (en)

**Instruction**

A 30-year-old woman presents with fever, neck stiffness, headache and photophobia. What diagnosis should be considered?

**frequence_0.5** (4 tokens, arrêt : stop)

Meningitis

**frequence_0.5_repetition_1.1** (4 tokens, arrêt : stop)

Meningitis

**frequence_0.5_presence_0.5** (4 tokens, arrêt : stop)

Meningitis
