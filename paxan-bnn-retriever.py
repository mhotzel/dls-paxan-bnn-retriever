from ftplib import FTP
from os.path import join
from datetime import date, datetime
import sys
from configparser import ConfigParser
from pathlib import Path
import logging

LOGGING_FORMAT = '%(asctime)s - %(filename)s - %(levelname)s - %(funcName)s: %(message)s'
LOGGING_DATEFORMAT = '%Y-%m-%d-%H.%M.%S'
LOGGING_LEVEL = logging.INFO
CSV_HEADER = 'Kennung;Version;Zeichensatz;Versenderadresse;Umfang;Inhalt;Preiswährung;DatumAb;DatumBis;Abgabedatum;Abgabezeit;Dateizähler;ArtikelNr;Änderungskennung;ÄnderungsDatum;ÄnderungsZeit;EANladen;EANbestell;Bezeichnung;Bezeichnung2;Bezeichnung3;Handelsklasse;Hersteller/Inverkehrbringer;Hersteller;Herkunft;Qualität;Kontrollstelle;MHD-Restlaufzeit;WG-BNN;WG-IfH;WG-GH;ErsatzArtikelNr;MinBestellMenge;Bestelleinheit;Bestelleinheits-Menge;Ladeneinheit;Mengenfaktor;Gewichtsartikel;PfandNrLadeneinheit;PfandNrBestelleinheit;GewichtLadeneinheit;GewichtBestelleinheit;Breite;Höhe;Tiefe;MwstKennung;VkFestpreis;EmpfVk;EmpfVkGH;Preis;rabattfähig;skontierfähig;StaffelMenge1;StaffelPreis1;rabattfähig1;skontierfähig1;StaffelMenge2;StaffelPreis2;rabattfähig2;skontierfähig2;StaffelMenge3;StaffelPreis3;rabattfähig3;skontierfähig3;StaffelMenge4;StaffelPreis4;rabattfähig4;skontierfähig4;StaffelMenge5;StaffelPreis5;rabattfähig5;skontierfähig5;Artikelart;Aktionspreis;AktionspreisGültigAb;AktionspreisGültigBis;empfVk-Aktion;Grundpreis-Einheit;Grundpreis-Faktor;LieferbarAb;LieferbarBis'

logger = logging.getLogger(__name__)

def setup_logging(protocol_file: str):
    '''Konfiguriert das Logging, also Pfade, Formate, Loglevel usw.'''
    logging.basicConfig(
        format=LOGGING_FORMAT,
        datefmt=LOGGING_DATEFORMAT,
        level=LOGGING_LEVEL,
        encoding='utf-8',
        filename=protocol_file
    )


def list_writer(liste: list, row: str) -> None:
    liste.append(row)


def retreive_header(first_row: str) -> dict:
    '''Liest die erste Zeile der Datei aus um die Datei-Metainformationen zu ermitteln'''
    rlist = first_row.split(";")

    datum_abgabe: date = None
    try:
        datum_abgabe = datetime.strptime(rlist[9], '%Y%m%d').date()
    except ValueError as ve:
        datum_abgabe = datetime.now().date()
        logger.warning(f"Abgabedatum konnte nicht korrekt ermittelt werden")

    uhrzeit_abgabe: date = None
    try:
        uhrzeit_abgabe = datetime.strptime(rlist[10], '%H%M').time()
    except ValueError as ve:
        uhrzeit_abgabe = datetime.now().time()
        logger.warning(f"Abgabeuhrzeit konnte nicht korrekt ermittelt werden")

    metaData = {
        'kennung': rlist[0],
        'version': rlist[1],
        'zeichensatz': rlist[2],
        'versender': rlist[3],
        'umfang': rlist[4],
        'inhalt': rlist[5],
        'waehrung': rlist[6],
        'gueltig_ab': rlist[7],
        'gueltig_bis': rlist[8],
        'datum_abgabe': datum_abgabe,
        'uhrzeit_abgabe': uhrzeit_abgabe,
        'datei_zaehler': rlist[11]
    }

    return metaData


def read_config() -> ConfigParser:
    app_dir = Path(__file__).parent
    cfg_parser = ConfigParser()
    with open(join(app_dir, "config.ini")) as file:
        cfg_parser.read_file(file)
    return cfg_parser


def main() -> None:
    cfg = read_config()
    host = cfg.get('paxan', 'host')
    user = cfg.get('paxan', 'user')
    password = cfg.get('paxan', 'password')
    encoding = cfg.get('paxan', 'encoding')
    filename_on_server = cfg.get('paxan', 'source_filename')
    target_filename = cfg.get('paxan', 'target_filename')
    target_dir = cfg.get('paxan', 'target_dir')
    protocol_file = cfg.get('paxan', 'protocol_file')
    setup_logging(protocol_file)

    try:
        logger.info(f"{str(datetime.now())} - Start Abholung Paxan-Artikeldatei")
        client = FTP(host=host, user=user, passwd=password, encoding=encoding)
        result_list = []
        client.retrlines(f'RETR {filename_on_server}',
                        lambda row: list_writer(result_list, row))
        client.close()
        kopfsatz = retreive_header(result_list[0])

        now = datetime.now().strftime('%Y%m%d%H%M%S')
        erstellung = kopfsatz['datum_abgabe'].strftime(
            '%Y%m%d') + kopfsatz['uhrzeit_abgabe'].strftime('%H%M00')

        filename = target_filename.replace('{retrievets}', f"{now}")
        filename = filename.replace('{validts}', f"{erstellung}")

        first_line = result_list[0]
        result_list = result_list[1:-1]

        with open(join(target_dir, filename), 'w', encoding='UTF-8') as file:
            file.write(CSV_HEADER + '\n')
            for line_nr, line in enumerate(result_list):
                file.write(first_line + ";" + line + '\n')

        logger.info(f"{str(datetime.now())} - Fertig")
    except Exception as e:
        logger.error(f'Fehler bei der Ausführung', exc_info=True)
        raise e

if __name__ == '__main__':
    main()
