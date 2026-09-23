import re

def buscar_i048(nom_fitxer):
    with open(nom_fitxer, "r", encoding="utf-8") as fitxer:
        contingut = fitxer.read()

    # Busca I048/ seguit de 3 caràcters alfanumèrics
    resultats = re.findall(r'I021/[A-Za-z0-9]{3}', contingut)

    # Eliminar duplicats mantenint l'ordre
    resultats_unics = list(dict.fromkeys(resultats))

    return resultats_unics


resultats = buscar_i048("ICAO 9871 Technic_merged.txt")

for resultat in resultats:
    print(resultat)