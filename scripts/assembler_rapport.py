"""Assembler rapport/rapport_final.md à partir des sections, puis le convertir en .docx et .pdf.

Aucun calcul statistique : le script concatène les fichiers de rapport/, numérote les figures et les tableaux,
applique la typographie française (espaces insécables), génère la table des matières (avec numéros de page
dans le PDF si pypdf est installé) et convertit avec pandoc (docx, html) et Edge ou Chrome sans interface (pdf).

Marqueurs reconnus dans les sections :
    [[FIG:id|chemin|Titre|Interprétation]]   figure numérotée avec légende
    [[TAB:id|Titre|Interprétation]]          titre numéroté placé avant un tableau
    @fig:id  /  @tab:id                      renvoi (« figure 3 », « tableau 7 »)
    [[INCLURE:chemin]]                       insère le contenu d'un fichier texte dans un bloc de code
    [[INSERER:chemin]]                       insère un fichier Markdown tel quel, en citation
    [[INSERER_LIGNES:chemin]]                insère un texte en citation, une ligne du fichier par paragraphe
    [[TABLE_CSV:chemin]]                     rend un fichier CSV en tableau
"""
from pathlib import Path
import csv
import re
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
RAPPORT = ROOT / 'rapport'
TITRE = 'WattIf — Consommation électrique quotidienne en France : prévision à 7 jours, contrefactuels COVID et sobriété'
SOUS_TITRE = 'Mini-projet de séries temporelles — Tek-Up, 3e année Data Science et IA — 12 octobre 2026'

CORPS = [
    '00_introduction.md', '01_donnees.md', '02_eda.md', '03_1_arima_sarima.md', '03_2_var_vecm.md', '03_3_garch.md',
    '03_4_replication_r.md', '04_1_lstm_gru.md', '04_2_hybride.md', '04_3_prophet.md', '05_llm.md',
    '06_prevision_evaluation.md', '07_extensions.md', '08_discussion_critique.md', '09_conclusion.md']
ANNEXES = ['annexe_A_tableaux.md', 'annexe_B_llm.md']

NBSP, NNBSP = '\u00a0', '\u202f'


def charger(nom):
    return (RAPPORT / nom).read_text(encoding='utf-8')


def numeroter(texte, compteurs, labels):
    """Remplace les marqueurs FIG/TAB/INCLURE ; les numéros suivent l'ordre du document."""
    sortie = []
    for ligne in texte.splitlines():
        m = re.match(r'\[\[FIG:([^|]+)\|([^|]+)\|([^|]+)\|(.+)\]\]\s*$', ligne)
        if m:
            ident, chemin, titre, interp = (x.strip() for x in m.groups())
            compteurs['fig'] += 1
            n = compteurs['fig']
            labels[('fig', ident)] = n
            sortie += [f'![Figure {n} — {titre}]({chemin})', '', f'*Figure {n} — {titre}.* {interp}', '']
            continue
        m = re.match(r'\[\[TAB:([^|]+)\|([^|]+)\|(.+)\]\]\s*$', ligne)
        if m:
            ident, titre, interp = (x.strip() for x in m.groups())
            compteurs['tab'] += 1
            n = compteurs['tab']
            labels[('tab', ident)] = n
            sortie += [f'**Tableau {n} — {titre}.** {interp}', '']
            continue
        m = re.match(r'\[\[INCLURE:([^\]]+)\]\]\s*$', ligne)
        if m:
            contenu = (ROOT / m.group(1).strip()).read_text(encoding='utf-8').rstrip()
            sortie += ['````text', contenu, '````']
            continue
        m = re.match(r'\[\[INSERER:([^\]]+)\]\]\s*$', ligne)
        if m:  # fichier Markdown inséré tel quel, en citation (réponse intégrale d'un LLM)
            contenu = (ROOT / m.group(1).strip()).read_text(encoding='utf-8').rstrip()
            sortie += ['> ' + l if l.strip() else '>' for l in contenu.splitlines()]
            continue
        m = re.match(r'\[\[INSERER_LIGNES:([^\]]+)\]\]\s*$', ligne)
        if m:  # texte sans mise en forme Markdown : chaque ligne reste un paragraphe, un titre « # » passe en gras
            contenu = [l.strip() for l in (ROOT / m.group(1).strip()).read_text(encoding='utf-8').splitlines() if l.strip()]
            contenu = [re.sub(r'^#+ +(.+)$', r'**\1**', l) for l in contenu]
            sortie += '\n>\n'.join('> ' + l for l in contenu).split('\n')
            continue
        m = re.match(r'\[\[TABLE_CSV:([^\]]+)\]\]\s*$', ligne)
        if m:  # fichier CSV rendu en tableau
            with open(ROOT / m.group(1).strip(), encoding='utf-8', newline='') as f:
                lignes_csv = list(csv.reader(f))
            sortie.append('| ' + ' | '.join(lignes_csv[0]) + ' |')
            sortie.append('|' + '---|' * len(lignes_csv[0]))
            sortie += ['| ' + ' | '.join(c.replace('|', '/') for c in l) + ' |' for l in lignes_csv[1:]]
            continue
        sortie.append(ligne)
    return '\n'.join(sortie)


def renvois(texte, labels):
    def rep(m):
        genre, ident = m.group(1), m.group(2)
        if (genre, ident) not in labels:
            raise KeyError(f'Renvoi inconnu : @{genre}:{ident}')
        return f"{'figure' if genre == 'fig' else 'tableau'}{NBSP}{labels[(genre, ident)]}"
    # « tableau @tab:x » ou « figure @fig:x » : le mot est déjà écrit, on ne le répète pas.
    texte = re.sub(r'\b(?:tableau|figure)\s+@(tab|fig):', r'@\1:', texte)
    return re.sub(r'@(fig|tab):([A-Za-z0-9_\-]+)', rep, texte)


def typographie(texte):
    """Espaces insécables avant : ; ! ? % et dans les guillemets « », hors code, liens et adresses."""
    morceaux = re.split(r'(````.*?````|`[^`\n]*`|!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|https?://\S+)', texte, flags=re.S)
    for i in range(0, len(morceaux), 2):
        t = morceaux[i]
        t = re.sub(r'(?<=\d) (?=\d{3}(?!\d))', NNBSP, t)  # séparateur de milliers insécable
        t = re.sub(r'(?<=\d) ?%', NNBSP + '%', t)
        t = re.sub(r'(?<=[^\s|]) ?([;!?])(?=\s|$)', NNBSP + r'\1', t)
        t = re.sub(r'(?<=[^\s|:]) :(?=\s|$)', NBSP + ':', t)
        t = re.sub(r'«\s*', '«' + NBSP, t)
        t = re.sub(r'\s*»', NBSP + '»', t)
        morceaux[i] = t
    return ''.join(morceaux)


def ancre(titre):
    t = re.sub(r'[`*_]', '', titre.strip().lower())
    t = re.sub(r'[^\w\s-]', '', t, flags=re.UNICODE)
    return re.sub(r'\s', '-', t)


def titres(texte, niveaux=(1, 2)):
    en_code, res = False, []
    for ligne in texte.splitlines():
        if ligne.startswith('```'):
            en_code = not en_code
        m = None if en_code else re.match(r'(#{1,3}) (.+)', ligne)
        if m and len(m.group(1)) in niveaux:
            res.append((len(m.group(1)), m.group(2).strip()))
    return res


def assembler(noms, compteurs, labels):
    brut = '\n\n'.join(numeroter(charger(n), compteurs, labels).strip() + '\n' for n in noms)
    return brut


def navigateur():
    return next((p for p in [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe'] if Path(p).exists()), None)


CSS = """
@page { size: A4; margin: 14mm 12mm 16mm 12mm; @bottom-center { content: counter(page) " / " counter(pages); font: 8.5pt Arial; color: #555; } }
body{font-family:Arial,sans-serif;font-size:9.5pt;line-height:1.26;max-width:none;margin:0;color:#111}
h1{font-size:15pt;margin:12px 0 5px;border-bottom:1px solid #1f3864;color:#1f3864}
h1.title{border:none}
h2{font-size:11.5pt;margin:9px 0 3px;color:#1f3864}h3{font-size:10pt;margin:7px 0 2px;color:#2f5496}
p{margin:3px 0;text-align:justify}li{margin:0}ul,ol{margin:3px 0;padding-left:20px}
table{border-collapse:collapse;font-size:7.5pt;margin:3px 0 7px;width:auto;max-width:100%}
th,td{border:1px solid #999;padding:1px 3px;vertical-align:top}th{background:#e8edf5}
tr{break-inside:avoid}img{display:block;margin:3px auto 0;max-width:100%;max-height:5.6cm;object-fit:contain}
pre,code{font-size:7.5pt;white-space:pre-wrap;word-break:break-word}
header#title-block-header{text-align:center;margin:60px 0 30px}
header#title-block-header h1.title{font-size:20pt}
nav#TOC{break-after:page}nav#TOC ul{list-style:none;padding-left:12px;margin:0}nav#TOC>ul{padding-left:0}nav#TOC li{font-size:8.5pt}
.saut{break-before:page}
"""


def vers_pdf(markdown, sortie_pdf, tmp, toc=True):
    nav, pandoc = navigateur(), shutil.which('pandoc')
    if not nav or not pandoc:
        return False
    src, css, html = Path(tmp) / 'src.md', Path(tmp) / 'style.css', Path(tmp) / 'rapport.html'
    src.write_text(markdown, encoding='utf-8')
    css.write_text(CSS, encoding='utf-8')
    cmd = [pandoc, str(src), '-f', 'gfm', '-s', '--embed-resources', '--metadata', f'title={TITRE}',
           '--metadata', f'subtitle={SOUS_TITRE}', '--metadata', 'lang=fr', '-c', str(css),
           '--resource-path', str(RAPPORT), '-o', str(html)]
    if toc:
        cmd += ['--toc', '--toc-depth=2']
    subprocess.run(cmd, check=True, cwd=RAPPORT)
    sortie_pdf.unlink(missing_ok=True)
    subprocess.run([nav, '--headless', '--disable-gpu', f'--user-data-dir={Path(tmp) / "profil"}',
                    f'--print-to-pdf={sortie_pdf}', '--no-pdf-header-footer', html.as_uri()], check=True, timeout=600)
    for _ in range(180):  # Edge peut rendre la main avant la fin de l'écriture du fichier
        if sortie_pdf.exists() and sortie_pdf.stat().st_size > 0:
            time.sleep(2)
            return True
        time.sleep(1)
    return False


def pages_des_titres(pdf, cibles):
    """Numéro de page de chaque titre, lu dans le texte du PDF (nécessite pypdf, facultatif)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return {}
    textes = [re.sub(r'\s+', ' ', (p.extract_text() or '')).replace(NBSP, ' ').replace(NNBSP, ' ')
              for p in PdfReader(str(pdf)).pages]
    # Le corps commence à la première page qui contient la première phrase de l'introduction (hors table des matières).
    debut = next((i for i, t in enumerate(textes) if 'Nous avons choisi la thématique' in t), 0)
    pages, courant = {}, debut
    for titre in cibles:
        cible = re.sub(r'\s+', ' ', re.sub(r'[`*]', '', titre)).replace(NBSP, ' ').replace(NNBSP, ' ')
        for i in range(courant, len(textes)):
            if cible in textes[i]:
                pages[titre] = i + 1
                courant = i
                break
    return pages


def main():
    compteurs, labels = {'fig': 0, 'tab': 0}, {}
    brut = assembler(CORPS + ANNEXES, compteurs, labels)
    saut = '<div class="saut"></div>' + chr(10) + chr(10)
    brut = brut.replace('# Annexe A', saut + '# Annexe A', 1).replace('# Annexe B', saut + '# Annexe B', 1)
    tout = typographie(renvois(brut, labels))
    idx = tout.find('# Annexe A')
    corps_seul = tout[:idx]
    liste = titres(tout)
    toc = '\n'.join(f"{'  ' * (n - 1)}- [{t}](#{ancre(t)})" for n, t in liste)
    md = f'# {TITRE}\n\n{SOUS_TITRE}\n\n## Table des matières\n\n{toc}\n\n---\n\n{tout}'
    (RAPPORT / 'rapport_final.md').write_text(md, encoding='utf-8', newline='\n')
    print(f"écrit rapport/rapport_final.md ; {compteurs['fig']} figures, {compteurs['tab']} tableaux")

    pandoc = shutil.which('pandoc')
    if not pandoc:
        print('pandoc introuvable : .docx et .pdf non générés')
        return
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        src = Path(tmp) / 'corps.md'
        src.write_text(tout, encoding='utf-8')
        subprocess.run([pandoc, str(src), '-f', 'gfm', '-o', str(RAPPORT / 'rapport_final.docx'), '--toc', '--toc-depth=2',
                        '--metadata', f'title={TITRE}', '--metadata', f'subtitle={SOUS_TITRE}', '--metadata', 'lang=fr',
                        '--resource-path', str(RAPPORT)], check=True, cwd=RAPPORT)
        print('écrit rapport/rapport_final.docx')

        pdf = RAPPORT / 'rapport_final.pdf'
        if not vers_pdf(tout, pdf, tmp):
            print('PDF non généré')
            return
        pages = pages_des_titres(pdf, [t for _, t in liste])
        for _ in range(3):  # la table des matières change la pagination : on itère jusqu'à stabilité
            if not pages:
                break
            lignes = [f"{'  ' * (n - 1)}- {t} — page {pages[t]}" for n, t in liste if t in pages]
            bloc = '## Table des matières' + chr(10) * 2 + chr(10).join(lignes) + chr(10) * 2 + '<div class="saut"></div>' + chr(10) * 2
            vers_pdf(bloc + tout, pdf, Path(tmp), toc=False)
            nouvelles = pages_des_titres(pdf, [t for _, t in liste])
            if nouvelles == pages:
                break
            pages = nouvelles
        print('écrit rapport/rapport_final.pdf', '(table des matières avec numéros de page)' if pages else '(pypdf absent : numéros de page seulement en pied de page)')

        # Longueur du corps : pages qui précèdent l'annexe A dans le PDF final (page de titre et table des matières comprises).
        annexe = next((p for t, p in pages.items() if t.startswith('Annexe A')), None)
        intro = pages.get('Introduction')
        if annexe:
            print(f'pages du corps, titre et table des matières compris : {annexe - 1} ; hors titre et table des matières : '
                  f'{annexe - intro if intro else "non compté"}')
        else:
            print('pypdf absent : nombre de pages du corps non compté ici')


if __name__ == '__main__':
    main()
