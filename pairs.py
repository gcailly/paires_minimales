pairs = [

    ["p_b",
        ["pain", "bain"],
        ["palais", "balai"],
        ["pelle", "belle"],
        ["peur", "beurre"],
        ["poire", "boire"],
        ["pou", "boue"],
        ["pull", "bulle"],
        ["poule", "boule"],
        ["pompon", "bonbon"],
        ["percer", "bercer"],
        ["peigner", "baigner"],
        ["pois", "bois"]
     ],

    ["t_d",
        ["touche", "douche"],
        ["tord", "dort"],
        ["tôt", "dos"],
        ["temps", "dent"],
        ["toux", "doux"],
        ["thé", "dé"],
        ["tire", "dire"],
        ["tard", "dard"],
        ["râteau", "radeau"]
     ],

    ["k_g",
        ["bac", "bague"],
        ["camp", "gant"],
        ["car", "gare"],
        ["carré", "garé"],
        ["cou", "goût"],
        ["classe", "glace"],
        ["oncle", "ongle"],
        ["crotte", "grotte"],
        ["crier", "griller"]
     ],

    ["f_v",
        ["faim", "vingt"],
        ["fâche", "vache"],
        ["fils", "vis"],
        ["faux", "veau"],
        ["faon", "vent"],
        ["folle", "vole"],
        ["fée", "v"],
        ["baffe", "bave"],
        ["foot", "voûte"],
        ["fond", "vont"],
        ["fer", "verre"],
        ["fil", "ville"]
     ],

    ["s_z",
        ["coussin", "cousin"],
        ["poisson", "poison"],
        ["douce", "douze"],
        ["tresse", "treize"],
        ["seau", "zoo"],
        ["casse", "case"],
        ["dessert", "désert"],
        ["visser", "viser"],
        ["les soeurs", "les heures"]
     ],

    ["ch_j",
        ["champ", "gens"],
        ["chou", "joue"],
        ["lécher", "léger"],
        ["manche", "mange"],
        ["bêche", "beige"],
        ["boucher", "bouger"],
        ["je l'achète", "je la jette"],
        ["cache", "cage"],
        ["hache", "âge"],
        ["chaîne", "gêne"]

     ],

    ["j_z",
        ["jaune", "zone"],
        ["rage", "rase"],
        ["bouse", "bouge"],
        ["des oeufs", "des jeux"],
        ["case", "cage"]
     ],

    ["s_ch",
        ["sous", "chou"],
        ["seau", "chaud"],
        ["sang", "champ"],
        ["bus", "bûche"],
        ["cassé", "caché"],
        ["mousse", "mouche"],
        ["douce", "douche"],
        ["tasse", "tache"],
        ["percer", "perché"],
        ["brosse", "broche"]
     ],

    ["t_k",
        ["pâté", "paquet"],
        ["pâtes", "pâques"],
        ["caché", "taché"],
        ["tarte", "carte"],
        ["tube", "cube"],
        ["toux", "cou"],
        ["tasse", "casse"],
        ["tas", "k"],
        ["tour", "court"],
        ["tôle", "colle"],
        ["temps", "camp"],
        ["tape", "cape"]
     ],

    ["tr_kr",
        ["trier", "crier"],
        ["trois", "croix"],
        ["trop", "croc"],
        ["trait", "craie"],
        ["entre", "encre"]
     ],

    ["r_l",
        ["barre", "balle"],
        ["roue", "loup"],
        ["poire", "poêle"],
        ["rat", "la"],
        ["mare", "malle"],
        ["reine", "laine"],
        ["fort", "folle"],
        ["père", "pelle"],
        ["robe", "lobe"],
        ["rang", "lent"],
        ["riz", "lit"]
     ],

    ["a_an",
        ["chat", "chant"],
        ["bas", "banc"],
        ["rat", "rang"],
        ["tas", "temps"],
        ["K", "camp"],
        ["fa", "faon"],
        ["va", "vent"],
        ["la", "lent"],
        ["plat", "plan"]
     ],

    ["an_on",
        ["blanc", "blond"],
        ["banc", "bond"],
        ["rang", "rond"],
        ["temps", "tond"],
        ["paon", "pont"],
        ["dent", "don"],
        ["lent", "long"],
        ["faon", "fond"],
        ["vent", "vont"],
        ["ranger", "ronger"]
     ],

]







fin_s = [
    ["pain", "pince"],
    ["mou", "mousse"],
    ["tas", "tasse"],
    ["scie", "six"]
]


fin_t = [
    ["roue", "route"],
    ["champ", "chante"],
    ["pas", "pâtes"],
    ["bois", "boîte"]

]

fin_l = [
    ["mât", "malle"],
    ["pue", "pull"],
    ["pou", "poule"],
    ["boue", "boule"],

]

fin_r = [
    ["bas", "barre"],
    ["lit", "lire"],
    ["cou", "court"],
    ["chat", "char"],
    ["bois", "boire"]

]

fin_m = [
    ["rat", "rame"],
    ["pot", "pomme"],
]

fin_p = [
    ["poule", "poulpe"]
]

fins = [
    ["boue", "bouche"],
    ["doux", "douze"],
    ["k", "canne"],
    ["cou", "coude"],
    ["rang", "range"],
    ["bas", "bague"],
    ["loup", "louche"],
    ["ment", "mange"],
]


# Fonction pour compter les paires
def count_pairs(pairs):
    count = 0
    for cat in pairs:
        count += len(cat) - 1
    return count


if __name__ == "__main__":
    # Compter le nombre de paires et l'afficher
    total_pairs = count_pairs(pairs)
    print(f"Nombre total de paires de mots: {total_pairs}")
