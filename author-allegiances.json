/**
 * Data structure mapping author IDs to their philosophical/religious allegiances
 * This will be used to update the original JSON data
 */
const authorAllegiances = {
  // Jewish Religious Texts
  "heb0001": "Jewish",  // Hebrew Bible
  "tlg0527": "Jewish",  // Old Testament
  
  // Christian Religious Texts and Authors
  "tlg0031": "Christian",  // New Testament
  "tlg0555": "Christian",  // Clement of Alexandria
  "tlg0645": "Christian",  // Justin Martyr
  "tlg1271": "Christian",  // Clement of Rome
  "tlg1311": "Christian",  // Didache
  "tlg1419": "Christian",  // Hermas
  "tlg1443": "Christian",  // Ignatius of Antioch
  "tlg1447": "Christian",  // Irenaeus
  "tlg1622": "Christian",  // Polycarp
  "tlg1725": "Christian",  // Theophilus
  "tlg1766": "Christian",  // Tatianus
  "tlg2016": "Christian",  // Martyrium Perpetuae et Felcitatis
  "tlg2018": "Christian",  // Eusebius of Caesarea
  "tlg2021": "Christian",  // Epiphanius
  "tlg2022": "Christian",  // Gregory of Nazianzus
  "tlg2035": "Christian",  // Athanasius
  "tlg2040": "Christian",  // Basil of Caesarea
  "tlg2042": "Christian",  // Origen
  "tlg2048": "Christian",  // Sozomenus
  "tlg2057": "Christian",  // Socrates Scholasticus
  "tlg2058": "Christian",  // Philostorgius
  "tlg2115": "Christian",  // Hippolytus
  "tlg2733": "Christian",  // Evagrius Scholasticus
  "tlg2768": "Christian",  // Gelasius
  "tlg2806": "Christian",  // Marcus Diaconus
  "tlg2934": "Christian",  // John of Damascus
  "tlg2959": "Christian",  // Methodius
  "tlg3129": "Christian",  // Theophylactus
  "tlg4089": "Christian",  // Theodoretus
  "tlg4090": "Christian",  // Cyril of Alexandria
  
  // Jewish Authors
  "tlg0018": "Jewish",  // Philo Judaeus
  "tlg0526": "Jewish/Historian",  // Flavius Josephus
  "tlg1390": "Jewish/Historian",  // Hecataeus of Abderita
  "tlg1750": "Jewish",  // Vitae Prophetarum
  
  // Epic Poets
  "tlg0001": "Poet",  // Apollonius Rhodius
  "tlg0012": "Poet",  // Homer
  "tlg0013": "Poet",  // Homeric Hymns
  "tlg0020": "Poet",  // Hesiod
  "tlg0341": "Poet",  // Lycophron
  "tlg0579": "Poet",  // Orphica
  "tlg0653": "Poet",  // Aratus Solensis
  "tlg2045": "Poet",  // Nonnus of Panopolis
  "tlg2046": "Poet",  // Quintus Smyrnaeus
  "tlg2691": "Poet",  // Musaeus, Eleusinius
  "tlg4081": "Poet",  // Colluthus of Lycopolis
  "tlg0647": "Poet",  // Tryphiodorus
  
  // Lyric/Pastoral/Other Poets
  "tlg0005": "Poet",  // Theocritus
  "tlg0033": "Poet",  // Pindar
  "tlg0035": "Poet",  // Moschus
  "tlg0036": "Poet",  // Bion of Phlossa
  "tlg0199": "Poet",  // Bacchylides
  "tlg0233": "Poet",  // Hipponax
  "tlg0533": "Poet",  // Callimachus
  
  // Playwrights
  "tlg0006": "Poet/Playwright",  // Euripides
  "tlg0011": "Poet/Playwright",  // Sophocles
  "tlg0019": "Poet/Playwright",  // Aristophanes
  "tlg0085": "Poet/Playwright",  // Aeschylus
  "tlg0521": "Poet/Playwright",  // Epicharmus
  "tlg0541": "Poet/Playwright",  // Menander
  
  // Historians
  "tlg0003": "Historian",  // Thucydides
  "tlg0016": "Historian",  // Herodotus
  "tlg0060": "Historian",  // Diodorus Siculus
  "tlg0074": "Historian/Stoic",  // Arrian
  "tlg0081": "Historian",  // Dionysius of Halicarnassus
  "tlg0099": "Historian/Geographer",  // Strabo
  "tlg0385": "Historian",  // Cassius Dio Cocceianus
  "tlg0525": "Historian/Geographer",  // Pausanias
  "tlg0543": "Historian",  // Polybius
  "tlg0551": "Historian",  // Appianus of Alexandria
  "tlg4029": "Historian",  // Procopius
  "tlg4084": "Historian",  // Zosimus
  
  // Platonists
  "tlg0007": "Middle Platonist/Biographer",  // Plutarch
  "tlg0059": "Platonist",  // Plato
  "tlg0613": "Platonist",  // Demetrius of Phaleron
  "tlg0634": "Platonist",  // Xenocrates of Chalcedon
  "tlg0693": "Middle Platonist",  // Albinus
  "tlg1188": "Platonist",  // Aristocles of Messene
  "tlg1287": "Platonist",  // Crantor
  "tlg1542": "Middle Platonist",  // Numenius of Apamea
  "tlg1692": "Platonist",  // Speusippus
  
  // Neoplatonists
  "tlg2000": "Neoplatonist",  // Plotinus
  "tlg2023": "Neoplatonist",  // Iamblichus
  "tlg2034": "Neoplatonist",  // Porphyrius
  "tlg2049": "Neoplatonist",  // Sallustius
  "tlg4013": "Neoplatonist",  // Simplicius
  "tlg4016": "Neoplatonist",  // Ammonius
  "tlg4017": "Neoplatonist",  // Syrianus
  "tlg4018": "Neoplatonist",  // Asclepius
  "tlg4019": "Neoplatonist",  // Olympiodorus
  "tlg4020": "Neoplatonist",  // Elias Neoplatonicus
  "tlg4021": "Neoplatonist",  // David the Invincible
  "tlg4036": "Neoplatonist",  // Proclus
  "tlg4075": "Neoplatonist",  // Marinus
  
  // Aristotelians/Peripatetics
  "tlg0086": "Peripatetic",  // Aristotle
  "tlg0093": "Peripatetic",  // Theophrastus
  "tlg0615": "Peripatetic",  // Aspasius
  "tlg0732": "Peripatetic",  // Alexander of Aphrodisias
  
  // Stoics
  "tlg0557": "Stoic",  // Epictetus
  "tlg0562": "Stoic",  // Marcus Aurelius
  "tlg0628": "Stoic",  // Musonius Rufus
  "tlg1146": "Stoic",  // Antipater Tarsensis
  "tlg1193": "Stoic",  // Ariston of Chios
  "tlg1264": "Stoic",  // Chrysippus
  "tlg1269": "Stoic",  // Cleanthes
  
  // Cynics
  "tlg0591": "Cynic",  // Antisthenes
  "tlg0623": "Cynic",  // Cratetis Epistulae
  "tlg1325": "Cynic",  // Diogenes Sinopensis Epistulae
  
  // Epicureans
  "tlg0537": "Epicurean",  // Epicurus
  "tlg1595": "Epicurean",  // Philodemus
  
  // Pre-Socratics
  "tlg0626": "Pre-Socratic",  // Heraclitus of Ephesus
  "tlg0629": "Pre-Socratic",  // Periander
  "tlg0632": "Pythagorean",  // Pythagoras
  "tlg0637": "Socratic",  // Socraticorum Epistulae
  "tlg1304": "Pre-Socratic",  // Democritus
  "tlg1319": "Pre-Socratic",  // Diogenes of Apollonia
  "tlg1414": "Pre-Socratic",  // Heraclitus
  "tlg1562": "Pre-Socratic",  // Parmenides
  "tlg1596": "Pythagorean",  // Philolaus of Croton
  "tlg1705": "Pre-Socratic",  // Thales
  "tlg0620": "Pythagorean",  // Archytas of Tarentum
  
  // Skeptics
  "tlg0544": "Skeptic",  // Sextus Empiricus
  
  // Rhetoricians and Sophists
  "tlg0010": "Rhetorician",  // Isocrates
  "tlg0014": "Rhetorician",  // Demosthenes
  "tlg0026": "Rhetorician",  // Aeschines
  "tlg0027": "Rhetorician",  // Andocides
  "tlg0028": "Rhetorician",  // Antiphon
  "tlg0029": "Rhetorician",  // Dinarchus
  "tlg0030": "Rhetorician",  // Hyperides
  "tlg0034": "Rhetorician",  // Lycurgus
  "tlg0535": "Rhetorician",  // Demades
  "tlg0540": "Rhetorician",  // Lysias
  "tlg0592": "Rhetorician",  // Hermogenes
  "tlg0593": "Sophist",  // Gorgias of Leontini
  "tlg0594": "Rhetorician",  // Alexander Numenius
  "tlg0607": "Rhetorician",  // Aelius Theon
  "tlg0610": "Sophist",  // Alcidamas
  "tlg0612": "Rhetorician",  // Dio Chrysostom
  "tlg0649": "Rhetorician",  // Lesbonax (Rhetorician)
  "tlg1434": "Sophist",  // Hippias of Elis
  "tlg1634": "Sophist",  // Prodicus
  "tlg2027": "Rhetorician",  // Valerius Apsines
  "tlg2200": "Rhetorician",  // Libanius
  "tlg2586": "Rhetorician",  // Menander Rhetor
  "tlg2601": "Rhetorician",  // Tiberius Rhetor
  
  // Medical Writers
  "tlg0057": "Medical",  // Galen
  "tlg0530": "Medical",  // Pseudo-Galen
  "tlg0564": "Medical",  // Rufus of Ephesus
  "tlg0565": "Medical",  // Soranus
  "tlg0627": "Medical",  // Hippocrates
  "tlg0643": "Medical",  // Anonymus Londinensis
  "tlg0656": "Medical",  // Dioscurides Pedianus
  "tlg0671": "Medical",  // Philumenus
  "tlg0719": "Medical",  // Aretaeus of Cappadocia
  "tlg0733": "Medical",  // Cassius Iatrosophista
  "tlg0751": "Medical",  // Pseudo-Hippocrates
  "tlg1118": "Medical",  // Pseudo-Dioscorides
  
  // Grammarians
  "tlg0082": "Grammarian",  // Apollonius Dyscolus
  "tlg0087": "Grammarian",  // Aelius Herodianus
  "tlg0542": "Grammarian",  // Julius Pollux
  "tlg0609": "Grammarian",  // Tryphon I Grammaticus
  "tlg0644": "Grammarian",  // Aristophanes of Byzantium
  "tlg0708": "Grammarian",  // Ammonius Grammaticus
  "tlg1194": "Grammarian",  // Aristonicus of Alexandria
  "tlg1389": "Grammarian",  // Harpocration
  "tlg1402": "Grammarian",  // Hephaestion
  "tlg1602": "Grammarian",  // Philoxenus of Alexandria
  "tlg1763": "Grammarian",  // Tryphon II Grammaticus
  
  // Biographers
  "tlg0004": "Biographer",  // Diogenes Laertius
  "tlg0638": "Biographer",  // Philostratus the Athenian
  "tlg0652": "Biographer",  // Philostratus Minor
  "tlg2050": "Biographer",  // Eunapius
  
  // Geographers
  "tlg0064": "Geographer",  // Hanno
  "tlg0065": "Geographer",  // Scylax of Caryanda
  "tlg0066": "Geographer",  // Heraclides, Criticus
  "tlg0067": "Geographer",  // Agatharchides
  "tlg0068": "Geographer",  // Pseudo-Scymnus
  "tlg0069": "Geographer",  // Dionysius, Calliphontis
  "tlg0070": "Geographer",  // Isidore, of Charax
  "tlg0071": "Geographer",  // Pseudo-Arrianus
  "tlg0075": "Geographer",  // Pseudo-Arrianus
  "tlg0077": "Geographer",  // Stadiasmus Magni Maris
  "tlg0083": "Geographer",  // Dionysius of Byzantium
  "tlg0084": "Geographer",  // Dionysius Periegetes
  "tlg0090": "Geographer",  // Agathemerus
  "tlg0092": "Geographer",  // Anonymi Geographiae Expositio Compendiaria
  "tlg0363": "Astronomer/Geographer",  // Claudius Ptolemaeus
  "tlg2029": "Geographer",  // Anonymi summaria ratio geographiae in sphaera intelligendae
  "tlg4003": "Geographer",  // Marcianus, of Heraclea
  
  // Mathematicians
  "tlg0358": "Mathematician",  // Nicomachus of Gerasa
  "tlg0361": "Mathematician",  // Cleonides
  "tlg0550": "Mathematician",  // Apollonius of Perga
  "tlg0552": "Mathematician",  // Archimedes
  "tlg0559": "Mathematician/Engineer",  // Hero of Alexandria
  "tlg1210": "Mathematician",  // Autolycus
  "tlg1383": "Astronomer",  // Geminus
  "tlg1431": "Astronomer",  // Hipparchus
  "tlg1719": "Mathematician",  // Theodosius of Bithynia
  "tlg1724": "Mathematician",  // Theon Smyrnaeus
  "tlg1799": "Mathematician",  // Euclid
  "tlg2032": "Mathematician",  // Pappus Alexandrinus
  "tlg2039": "Mathematician",  // Diophantus Alexandrinus
  "tlg4072": "Mathematician",  // Eutocius
  
  // Novelists/Fiction Writers
  "tlg0532": "Novelist",  // Achilles Tatius
  "tlg0561": "Novelist",  // Longus
  "tlg0614": "Fabulist",  // Babrius
  "tlg0638": "Biographer/Novelist",  // Philostratus the Athenian
  "tlg0641": "Novelist",  // Xenophon of Ephesus
  "tlg0658": "Novelist",  // Heliodorus of Emesa
  "tlg1441": "Novelist",  // Iamblichus (Scr. Erot.)
  "tlg3118": "Fabulist",  // Syntipas
  
  // Military Writers
  "tlg0058": "Military Writer",  // Aeneas Tacticus
  "tlg0556": "Military Writer",  // Asclepiodotus
  "tlg0616": "Military Writer",  // Polyaenus Macedo
  "tlg0648": "Military Writer",  // Onasander
  
  // Natural/Physical Science
  "tlg0553": "Dream Interpreter",  // Artemidorus
  "tlg1337": "Astrologer",  // Dorotheus of Sidon
  "tlg1487": "Astrologer",  // Maximus, Astrologus
  "tlg1669": "Astrologer",  // Serapion Astrologus
  "tlg1764": "Astrologer",  // Vettius Valens
  "tlg2583": "Astrologer",  // Manetho Astrologus
  
  // Other/Specific Authors
  "tlg0032": "Historian/Socratic",  // Xenophon
  "tlg0094": "Middle Platonist",  // Pseudo-Plutarch
  "tlg0096": "Fabulist",  // Aesop
  "tlg0572": "Jurist",  // Gaius Romanus
  "tlg1116": "Independent",  // Anonymi de Barbarismo et Soloecismo
  "tlg1247": "Socratic",  // Cebes
  "tlg1286": "Hermeticist",  // Hermetica
  "tlg1309": "Sophist",  // Dialexeis
  "tlg1320": "Stoic",  // Diogenes Babylonius
  "tlg1413": "Independent",  // Heraclitus Paradoxographus
  "tlg1416": "Independent",  // Philo of Byblos
  "tlg1553": "Independent",  // Palaiphatos
  "tlg3156": "Scholar",  // Anonymi Exegesis in Hesiodi Theogoniam
  "tlg9010": "Lexicographer"  // Suda
};

// For all the remaining authors who aren't explicitly categorized:
// - Scholiasts - These are authors of commentaries (scholia) on classical texts
// - Epistolographers - Authors of letters
// - Aristotelian commentators
// - Later Christian authors
// - Byzantine authors (later centuries CE)
// - Independent/Unknown for truly unclear cases
