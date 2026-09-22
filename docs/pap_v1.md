# Pre-Analysis-Plan v1 — "Der Preis eines Designparameters"
**Projekt:** Digitaler Euro, Ereignisstudie über die Gesetzgebungsphase 2023–2026
**Datum:** 17.09.2026 · **Status:** Entwurf, noch nicht eingefroren
**Ziel:** Bundesbank-Call "Financial Stability in the Era of AI and Digital Finance", Einreichung 02.11.2026

## 0. Abgrenzung zur bestehenden Arbeit (Volltext gelesen)

**Burlon, Montes-Galdón, Muñoz, Smets**, EZB WP 2689 (2022), publiziert als Burlon, Muñoz, Smets, *AEJ: Macroeconomics* 16(4), 2024, 172–217.

Was sie machen:
- 134 Banken, Iboxx-Daten, 01.01.2007 bis 31.05.2021.
- Fama-French-Dreifaktormodell mit Ereignis-Dummies nach Sefcik und Thompson (1986); danach Querschnittsregression der abnormalen Renditen auf die Einlagenquote, mit Ereignis- und Bank-Fixed-Effects.
- **Ereignisse ausschließlich 2020 und 2021, ausschließlich Äußerungen von EZB-Direktoriumsmitgliedern**: Pressemitteilungen, Interviews, Reden, Blogeinträge, eine VoxEU-Kolumne.
- Befund: Eine Standardabweichung der Einlagenquote (18 Prozentpunkte) entspricht über einem Prozentpunkt Unterschied in der abnormalen Rendite je Ereignis.
- Kreditwirkung über AnaCredit: 0,1 bis 0,4 % des Vorvolumens je Prozentpunkt zusätzlicher Rendite.
- Die Rede von Panetta am 10.02.2021, in der eine mögliche Haltegrenze von 3.000 Euro genannt wurde, kehrt den Trend um. Das ist bei ihnen eine **Einzelbeobachtung**, kein Design.

Was daraus folgt für uns, vier belegbare Lücken:
1. **Kein einziges Gesetzgebungsereignis.** Ihr Fenster endet im Mai 2021; der Kommissionsvorschlag kam im Juni 2023. Die gesamte Phase, in der über das Design entschieden wurde, liegt außerhalb.
2. **Keine Dosis.** Ereignisse sind nicht nach Designinhalt kodiert. Die Umkehr nach dem 10.02.2021 legt nahe, dass der Inhalt zählt, wird aber nicht systematisch genutzt.
3. **Nur Banken.** Der Souveränitätsteil der Politikbegründung zielt auf außereuropäische Kartennetzwerke; deren Bewertung wird nicht untersucht.
4. **Kein Marktmacht-Test.** Sie zitieren Andolfatto und Chiu et al. dafür, dass CBDC bei unvollkommenem Wettbewerb die Einlagen sogar ausweiten kann, testen es aber nicht.

**Unsere Frage `[OUR CLAIM]`:** Was kostet ein einzelner Designparameter des digitalen Euro, und wem wird Rente entzogen?

## 1. Hypothesen

| # | Hypothese | Rolle |
|---|---|---|
| H1 | Ereignisse, die die Menge digitaler Euro **begrenzen** (niedrigere Haltegrenze, Offline-First, Verbot von Unternehmensbeständen), erhöhen Bankbewertungen; Ereignisse, die sie **ausweiten**, senken sie. Die Wirkung skaliert mit der Einlagenexposition | **primär** |
| H2 | Die implizite Bewertung je 1.000 Euro Haltegrenze lässt sich aus der Dosis-Wirkungs-Beziehung ableiten | primär, quantitativ |
| H3 | Zahlungsdienstleister und Kartennetzwerke mit hoher Euro-Abhängigkeit verlieren, wenn das Projekt vorankommt | sekundär |
| H4 | Bei hoher Einlagenmarktmacht ist die Reaktion schwächer negativ oder positiv (Chiu et al.) | sekundär, Theorietest |
| H5 | Kein Effekt bei rein prozeduralen Ereignissen ohne Designinhalt | Falsifikation |

## 2. Reihenfolge, die eingehalten wird

1. Ereignisliste an Primärquellen verifizieren.
2. **Ereignisse nach Designinhalt kodieren, bevor Kursdaten angesehen werden.** Die Kodierung wird per Hash eingefroren. Das ist die direkte Übertragung des Blindheitsprinzips aus dem Verlust-Paper.
3. Expositionsmaße aus Vorperiodendaten bilden (Stand vor Juni 2023).
4. Power-Rechnung.
5. Erst dann Kursdaten einlesen und schätzen.

## 3. Ereigniskodierung (vor Kursdaten)

Jedes Ereignis erhält:
- **Richtung** der Designänderung aus Banksicht: begrenzend (+1), ausweitend (−1), neutral (0).
- **Dosis**, wo quantifizierbar: genannte Haltegrenze in Euro; sonst fehlend.
- **Überraschungsgrad**: erwartet, teils erwartet, unerwartet, kodiert aus Vorberichterstattung und, bei Abstimmungen, aus dem Verhältnis von Ergebnis zu erwarteter Mehrheit.
- **Prozedural ja/nein** für den Falsifikationstest.

Zwei Kodierer wären ideal. Falls nur einer, wird das wie im Vorgängerpaper offengelegt.

## 4. Schätzgleichung

Erste Stufe (Burlon-kompatibel, damit die Ergebnisse vergleichbar sind):
R(b,t) = α_b + β_m R_m(t) + β_HML R_HML(t) + β_SMB R_SMB(t) + Σ_e γ(b,e) D(e,t) + ε(b,t)

Zweite Stufe, unser Beitrag:
γ̂(b,e) = θ · Exposition(b) × Richtung(e) + λ · Exposition(b) × Dosis(e) + δ_e + μ_b + X(b,e)'ψ + u(b,e)

Ereignis-Fixed-Effects δ_e nehmen alles heraus, was am Ereignistag alle Banken gleich trifft. Identifikation kommt aus dem Querschnitt.

**Inferenz:** Cluster auf Bankebene; zusätzlich Wild-Cluster-Bootstrap und Permutation der Expositionswerte über Banken. Size-Simulation vor der Schätzung, wie im Verlust-Paper.

## 5. Daten

| Block | Inhalt | Quelle | Status |
|---|---|---|---|
| Kurse | Tagesrenditen von etwa 40 börsennotierten Euro-Banken, Kartennetzwerken, Zahlungsdienstleistern, Nicht-Euro-Kontrollbanken | Yahoo Finance oder Stooq | **Philip lädt herunter** |
| Faktoren | Fama-French-Faktoren Europa | Kenneth-French-Datenbibliothek | **Philip lädt herunter** |
| Exposition | Einlagen des privaten Nichtfinanzsektors an den Hauptverbindlichkeiten, Stand vor Juni 2023 | EBA Transparency Exercise | öffentlich |
| Marktmacht | Konzentration des Bankensektors je Land | EZB-Strukturstatistik | öffentlich |
| Ereignisse | Daten, Dokumente, Abstimmungsergebnisse | EUR-Lex, Legislative Observatory, Rat, EZB | in Arbeit |
| Netzwerke | Euro-Umsatzanteile | Segmentberichte | öffentlich |

## 6. Vorab festgelegte Falsifikationstests
- F1: Prozedurale Ereignisse ohne Designinhalt zeigen keinen Effekt.
- F2: Nicht-Euro-Banken mit ähnlicher Einlagenstruktur zeigen keinen Effekt.
- F3: Vorzeichenumkehr zwischen begrenzenden und ausweitenden Ereignissen.
- F4: Placebo-Tage in derselben Woche.
- F5: Pre-Trends im Schätzfenster der ersten Stufe.

## 7. Die zwei Angriffe, die das Paper töten
1. **"Das ist Burlon et al. mit neuen Ereignissen."** Gegenmittel: Dosis und Vorzeichenmuster sind der Beitrag. Das muss im Abstract im ersten Satz stehen, nicht im Beitragsabsatz.
2. **"Gesetzgebungsschritte sind vollständig antizipiert."** Gegenmittel: Überraschungskodierung vorab, Abstimmungsergebnisse gegen erwartete Mehrheiten, Fenster von einem Tag statt mehreren.

## 8. Offene Entscheidungen für Philip
1. Kursdaten: Kommst du an Yahoo Finance oder Stooq?
2. Zweiter Kodierer für die Ereignisse?
3. Ziel: Extended Abstract bis 02.11.2026, oder vollständiges Paper?

---

## Nachtrag v1.1 (18.09.2026): Ereignisse verifiziert, Lobbydaten gefunden

### A. 17 von 21 Ereignissen an der Primärquelle geprüft
Quelle: Legislative Observatory, Verfahren 2023/0212(COD), abgerufen am 18.09.2026. Die Ereignisliste liegt jetzt in `data/hand/events_v1.csv`.

Korrekturen gegenüber v0:
- Die Ausschussabstimmung war am **23.06.2026**, der Bericht wurde am **26.06.2026** eingereicht, die Ankündigung im Plenum erfolgte am **06.07.2026**, die Bestätigung am **09.07.2026**. Das sind vier getrennte Ereignisse, nicht zwei.
- Änderungsanträge wurden in zwei Wellen eingereicht: zwei Sätze am **21.02.2024** (Berger-Phase), vier Sätze am **19.12.2025** (Navarrete-Phase).
- Neu aufgenommen: **13.11.2024**, Wiederaufnahme des Dossiers nach der Wahlperiode. Ein rein prozedurales Ereignis und damit ein guter Kandidat für den Falsifikationstest.
- Der Berichterstatterwechsel am **16.12.2024** ist bestätigt: Berger (EPP, ernannt 19.07.2023) wurde durch Navarrete Rojas (EPP) ersetzt.
- Noch offen: ECOFIN 08.07.2025, Eurogruppe 19.09.2025, EZB-Pilotaufruf 05.03.2026 sowie das genaue Trilogdatum.

### B. Unerwarteter Fund: das Verfahren hat ein öffentliches Lobbyregister

Die Verfahrensakte führt die **Treffen mit Interessenvertretern**, mit Datum, Abgeordnetem, Rolle und Name der Organisation. Bereits in der ersten Ansicht sichtbar: Fédération bancaire française, Banco Santander (fünf Treffen), CECA, Apple, EPI, Bizum, European Payment Institutions Federation, EuroCommerce, Inditex, Ons Geld. Erste 20 Einträge liegen in `data/hand/lobby_meetings_v0.csv`; die Liste ist länger und wird vollständig gezogen.

Das ist aus drei Gründen wertvoll:
1. **Mechanismus statt Spekulation.** Wir können zeigen, welche Interessen vor welchen Verfahrensschritten aktiv waren, statt es zu vermuten.
2. **Der Querschnitt ist im Kurssample.** Santander und Apple sind börsennotiert und Teil unserer Stichprobe. Bank gegen Bigtech gegen Zahlungssystem ist genau die Inzidenzfrage des Papers.
3. **Überraschungsmaß.** Lobbyintensität in den Wochen vor einem Ereignis ist ein vorab beobachtbarer Indikator dafür, wie umkämpft und damit wie wenig vorhersehbar ein Schritt war.

**Wichtige Einschränkung:** Das Register erfasst nur Treffen von Berichterstattern, Schattenberichterstattern und Ausschussvorsitzenden verpflichtend. Es ist kein vollständiges Bild der Einflussnahme.

### C. Konsequenz für das Design
Das Paper bekommt einen dritten Baustein neben Bewertung und Inzidenz: **wer verhandelt hat**. Damit rückt es näher an die politische Ökonomie und weiter weg von einer reinen Wiederholung von Burlon et al.

Nächster Schritt: vollständige Lobbyliste ziehen, Ratsereignisse verifizieren, dann die Designkodierung der Ereignisse festlegen und einfrieren.

---

## Nachtrag v1.2 (18.09.2026): Vollständiges Lobbyregister und Designinhalt des Ausschussberichts

### A. 309 dokumentierte Treffen, Juli 2023 bis Juli 2026
`data/hand/lobby_meetings_v1.csv`, vollständig aus der Verfahrensakte übertragen. Pro Jahr: 48 (2023), 20 (2024), 161 (2025), 80 (2026 bis Juli).

Häufigste Organisationen: Deutsche Bank (12), Fédération bancaire française (10), Amazon (8), BEUC (8), Banco Santander (7), EuroCommerce (7), EDPIA (6), Mercadona (6), Finance Watch (6).

Drei Beobachtungen:
1. **Der Einbruch 2024 ist informativ.** Nach dem Ende der Wahlperiode und vor der Ernennung des neuen Berichterstatters ruht das Dossier fast vollständig. Das stützt die Kodierung des 13.11.2024 als rein prozedurales Ereignis.
2. **Die Gegenseite ist organisiert.** Neben Banken treten Handel (EuroCommerce, Mercadona, Inditex), Verbraucherschutz (BEUC, Positive Money, Finance Watch), Kartennetzwerke (Mastercard, Visa, American Express), Bigtech (Amazon, Apple, Meta) und Krypto (Circle, Ripple) auf. Die Inzidenzfrage des Papers ist damit nicht konstruiert, sondern in den Verhandlungsdaten sichtbar.
3. **Viele der Organisationen sind börsennotiert** und damit direkt im Kurssample: Deutsche Bank, BNP Paribas, Société Générale, Santander, BBVA, CaixaBank, Intesa Sanpaolo, UniCredit, ING, Rabobank, Crédit Agricole, Erste Group, BPCE, Mastercard, Visa, American Express, Amazon, Apple, Meta, Nexi, Inditex, Ryanair, TotalEnergies.

**Einschränkung:** Verpflichtend veröffentlicht werden nur Treffen von Berichterstattern, Schattenberichterstattern und Ausschussvorsitzenden. Die zweite Liste ("Other Members") ist freiwillig und daher unvollständig.

### B. Der Ausschussbericht liefert den Designinhalt
`data/hand/committee_report_content.md`. Der am 26.06.2026 eingereichte Bericht legt unter anderem fest: Gesamtobergrenze für Haltegrenzen, festgelegt durch die Kommission auf EZB-Empfehlung und alle zwei Jahre überprüft; **keine Bestände juristischer Personen**, außer für 24 Stunden zur Bündelung; Einführungsphase von **mindestens 24 Monaten**; **Deckelung der Händler- und Interbankenentgelte**, Offline-Zahlungen gebührenfrei.

**Wichtige Konsequenz für das Design:** Dieses Ereignis ist nicht eindimensional. Die Mengenbegrenzungen sind für Banken günstig, die Gebührendeckel sind für Händler günstig und für Zahlungsdienstleister ungünstig. Die Kodierung muss die Richtung **getrennt für Banken und für Zahlungsdienstleister** festhalten. Genau diese Trennung ist der Beitrag gegenüber Burlon et al., die nur einen Querschnitt haben.

---

## Nachtrag v1.3 (18.09.2026): Ereigniskodierung begonnen, Lobbyintensität berechnet

### A. Kodierstand
`data/hand/event_coding_v1.csv`. Von 21 Ereignissen sind **12 kodiert**, 4 warten auf die Lektüre der Dokumententexte, 5 auf die Verifikation an Primärquellen. Die Kodierung enthält für jedes Ereignis: prozedural ja/nein, Richtung für **Banken**, Richtung für **Zahlungsdienstleister**, Dosis in Euro, Überraschungsgrad und eine schriftliche Begründung.

**Drei Ereignisse tragen bereits ein Vorzeichenmuster**, bei dem Banken und Zahlungsdienstleister gegenläufig betroffen sind: die EZB-Stellungnahme vom 31.10.2023 sowie die Ausschussposition vom 23.06.2026 und ihre Bestätigung im Plenum am 09.07.2026. Das ist die Variation, die ein reiner Nachrichtenintensitätseffekt nicht erzeugen kann.

Zwei Ereignisse sind als **Falsifikationsereignisse** markiert: die Wiederaufnahme nach der Wahlperiode (13.11.2024) und die Ankündigung nach Regel 72 im Plenum (06.07.2026). Beide sind rein prozedural.

### B. Lobbyintensität als vorab beobachtbares Überraschungsmaß
`data/derived/lobby_intensity_by_event.csv`. Für jedes Ereignis die Zahl dokumentierter Treffen in den 30 Tagen davor, aufgeteilt nach Bankenseite, Zahlungsdienstleistern sowie Handel und Zivilgesellschaft.

Das Bild ist scharf:
- **Höchste Intensität vor der Eurogruppen-Einigung zur Haltegrenze (19.09.2025): 22 Treffen, davon 14 von der Bankenseite.** Das ist der stärkste Ausschlag im gesamten Datensatz und stützt die Vermutung, dass dies das zentrale Dosisereignis ist.
- **Zweithöchste vor dem EZB-Pilotaufruf (05.03.2026): 19 Treffen, davon 13 von der Bankenseite.**
- **Niedrigste vor den Falsifikationsereignissen:** ein Treffen vor dem 13.11.2024. Die Kodierung als prozedural wird also unabhängig durch das Verhalten der Lobbyisten bestätigt.

Die Kategorisierung liegt in `data/derived/lobby_categorised.csv`: 119 Treffen der Bankenseite, 40 Zahlungsdienstleister, 23 Handel, 25 Zivilgesellschaft, 13 Bigtech, 89 sonstige (überwiegend Zentralbanken, Finanzministerien und Ständige Vertretungen).

### C. Was das für die Kodierung bedeutet
Die Lobbyintensität wird **nicht** zur Bestimmung der Richtung verwendet, sondern nur als Überraschungsmaß. Die Richtung kommt ausschließlich aus dem dokumentierten Inhalt. Diese Trennung wird vor dem Einfrieren festgeschrieben.

### D. Offene Arbeit vor dem Einfrieren
1. Vier Ausschussdokumente lesen und kodieren: PE758.954, PE759.657/666, PE778.136, PE781.235/499/500/501.
2. Fünf Ereignisse an Primärquellen verifizieren, vorrangig die Eurogruppe vom 19.09.2025.
3. Erst dann Hash und Kursdaten.

---

## Nachtrag v1.4 (18.09.2026): Der Berichtsentwurf ist der Kern, und es kommt ein dritter Querschnitt dazu

### A. Der Entwurf vom 03.11.2025 ist das stärkste Ereignis im Datensatz
Der Berichtsentwurf des Berichterstatters (PE778.136) trennt Offline- und Online-Euro scharf:
- Der **Offline-Euro** wird sofort eingeführt, als tokenisiertes Gerät-zu-Gerät-Instrument mit Bargeldeigenschaften.
- Der **Online-Euro**, also die einlagensubstituierende Variante, wird **nur dann** eingeführt, wenn die **Kommission** nach einer Untersuchungsphase feststellt, dass keine geeignete paneuropäische souveräne Zahlungslösung existiert.
- Die Haltegrenzen werden präskriptiver gefasst.

Das ist die weitreichendste mengenbegrenzende Festlegung des gesamten Verfahrens: Sie macht den bankenschädlichen Teil des Projekts bedingt und übergibt die Feststellung der Kommission statt der EZB. Kodierung: **für Banken +1, für private europäische Zahlungssysteme +1**, Überraschungsgrad hoch.

### B. Neues Ereignis: Ratsposition vom 17.12.2025
Der Rat legte am **17.12.2025** seine Verhandlungsposition fest: Haltegrenzen von der EZB innerhalb einer vom Rat definierten Obergrenze, kostenlose Basisdienste, regulierte Entgelte für Zusatzdienste, **garantierter fairer Zugang zu Mobilgeräten für Zahlungsdienstleister**, gedeckelte Entgelte in einer Übergangszeit und danach kostenbasierte Preise.

### C. Daraus folgt ein dritter Querschnitt: Gerätehersteller
Der Zugang zu NFC-Schnittstellen auf Mobilgeräten trifft **Apple** unmittelbar und nur Apple. Das Register zeigt zwei Treffen von Apple mit dem Berichterstatter beziehungsweise einem Schattenberichterstatter, im November 2025 und im Juni 2026.

Das Paper misst damit die Inzidenz entlang der gesamten Zahlungswertschöpfungskette:
1. **Banken** als Einlagenhalter und Vertriebsstellen,
2. **Zahlungsdienstleister und Kartennetzwerke** als Betreiber der Zahlungsschienen,
3. **Gerätehersteller** als Torwächter des Zugangs.

Kein bestehendes Papier macht das. Burlon et al. haben nur den ersten Querschnitt.

### D. Stand der Kodierung
22 Ereignisse, davon 14 kodiert, 3 warten auf Dokumentenlektüre, 5 auf Verifikation. Sechs Ereignisse tragen ein Vorzeichenmuster, bei dem mindestens zwei Gruppen gegenläufig betroffen sind.

---

## Nachtrag v1.5 (18.09.2026): Eurogruppe verifiziert, eine Datumskollision gefunden

### A. Eurogruppe vom 19.09.2025 verifiziert
Belegt über die Sitzungsseite des Rates, den EZB-Abschlussbericht und ein Arbeitsdokument der Präsidentschaft (WK 14306/2025). Die Minister haben den **konzeptionellen Rahmen für die Festlegung und Änderung der Obergrenze** der Haltegrenzen gebilligt, **nicht die Zahlen selbst**.

Die Richtung ist dadurch echt gemischt: Das Ereignis treibt das Verfahren voran, was für Banken ungünstig ist, legt aber zugleich fest, dass es einen verbindlichen Obergrenzenmechanismus geben wird, was günstig ist. Ich kodiere es als 0 und dokumentiere die Mischung, statt eine Richtung zu erzwingen.

Bemerkenswert bleibt: Es ist das Ereignis mit der höchsten Lobbyintensität im gesamten Datensatz, 22 Treffen in 30 Tagen, davon 14 von der Bankenseite. Die Marktteilnehmer haben es also als wichtig behandelt, auch wenn die Richtung für Außenstehende nicht eindeutig ist.

### B. Datumskollision, die das Design betrifft
Die Ratsposition und die vier Sätze von Änderungsanträgen im ECON fallen beide auf den **19.12.2025**. Mit Tagesdaten sind sie nicht trennbar.

Drei Optionen, vorab zu entscheiden:
1. Beide gemeinsam als ein Ereignis behandeln, mit kombinierter Kodierung.
2. Den Tag ausschließen.
3. Intraday-Daten nutzen, falls die Uhrzeiten der Veröffentlichungen dokumentiert sind.

Zusätzlich nennen Sekundärquellen den 17.12.2025 für die Ratseinigung, die Pressemitteilung trägt den 19.12.2025. Das Datum muss vor dem Einfrieren an der Primärquelle geklärt werden.

### C. Neues Ereignis
**23.10.2025**, die Staats- und Regierungschefs fordern beschleunigten Fortschritt. Reine Beschleunigung ohne Designinhalt, also für alle Amtsinhaber ungünstig.

### D. Stand
23 Ereignisse: 15 kodiert, 1 mit Kollisionsvermerk, 3 warten auf Dokumentenlektüre, 4 auf Verifikation.

---

## Nachtrag v1.6 (18.09.2026): Ratsposition verifiziert, das Vorzeichenmuster steht

### A. Ratsposition vom 19.12.2025, Primärquelle
Pressemitteilung 1125/25 des Rates. Inhalt, für die Kodierung relevant:
- Haltegrenzen setzt die EZB, sie müssen aber eine **vom Rat vereinbarte Gesamtobergrenze** einhalten, die mindestens alle zwei Jahre überprüft wird. Politische statt technokratische Kontrolle über den Parameter.
- Zahlungsdienstleister dürfen für **Pflichtdienste keine Entgelte** verlangen: Eröffnung und Schließung von Konten, Zahlungen, Auf- und Abladen von Beträgen aus dem eigenen Einlagenkonto. Nur Zusatzdienste sind entgeltfähig.
- Es wird ein Rahmen geschaffen, der Anbietern von Digitaleuro-Diensten **Zugang zu Hardware und Software der Gerätehersteller** garantiert.
- Vergütung: In einer Übergangszeit von **mindestens fünf Jahren** werden Interbanken- und Händlerentgelte auf das Niveau vergleichbarer Zahlungsmittel gedeckelt, danach kostenbasiert.

Kodierung: Banken **gemischt** (politische Obergrenze günstig, entgeltfreie Pflichtdienste und gedeckelte Vergütung ungünstig), Zahlungsdienstleister **negativ**, Gerätehersteller **negativ**.

### B. Das Vorzeichenmuster über acht kodierte Ereignisse

| Ereignis | Datum | Banken | Zahlungs-DL | Geräte |
|---|---|---|---|---|
| Kommissionsvorschlag | 28.06.2023 | − | − | |
| EZB-Stellungnahme | 31.10.2023 | − | 0 | |
| Staats- und Regierungschefs | 23.10.2025 | − | − | 0 |
| EZB, nächste Phase | 30.10.2025 | − | − | |
| **Berichtsentwurf** | **03.11.2025** | **+** | **+** | 0 |
| **Ratsposition** | **19.12.2025** | **0** | **−** | **−** |
| **Ausschussposition** | **23.06.2026** | **+** | **−** | |
| Plenum bestätigt | 09.07.2026 | + | − | |

Das ist die Variation, auf der das Paper ruht. Gemeinsame Nachrichtenintensität kann nicht erzeugen, dass dieselbe Meldung Banken hebt und Zahlungsdienstleister senkt. Drei Ereignisse tragen ein solches gegenläufiges Muster, zwei davon mit hohem Überraschungsgrad.

### C. Was das für die Hypothesen heißt
H1 wird schärfer formulierbar: Nicht "Banken reagieren auf Nachrichten zum digitalen Euro", sondern **"dieselbe Nachricht bewegt drei Gruppen in unterschiedliche Richtungen, entsprechend der Rente, die ihnen der jeweilige Designparameter entzieht oder belässt"**. Das ist die Abgrenzung zu Burlon et al. in einem Satz.

### D. Rest
23 Ereignisse: 16 kodiert, 3 warten auf Dokumentenlektüre (Berger-Entwurf, Änderungsanträge 2024 und 2025), 4 auf Verifikation (ECOFIN 08.07.2025, EZB-Pilotaufruf 05.03.2026, Trilog 13.07.2026, Position des neuen Berichterstatters bei Amtsantritt).

---

## Nachtrag v1.7 (18.09.2026): Pilotverfahren verifiziert, ein Ereignis mit Innengruppenvergleich

### A. Verifiziert
- **05.03.2026:** EZB veröffentlicht den Aufruf zur Interessenbekundung, Frist 14.05.2026, 17:00 MESZ; zwölfmonatiger Pilot in der zweiten Jahreshälfte 2027. Für Banken projektfördernd und damit ungünstig; für Zahlungsdienstleister auf Indexebene mehrdeutig, weil dasselbe Ereignis Wettbewerb bringt und zugleich Teilnahme ermöglicht.
- **14.07.2026:** EZB wählt **36 Zahlungsdienstleister** aus mehr als 50 Bewerbern aus, Banken und Nichtbanken.

### B. Warum die Auswahl das methodisch wertvollste Ereignis ist
Alle übrigen Ereignisse vergleichen Gruppen. Die Auswahl erlaubt einen Vergleich **innerhalb** der Gruppe der Zahlungsdienstleister: ausgewählt gegen nicht ausgewählt, am selben Tag, unter denselben Marktbedingungen.

Das trägt eine Schwäche des Designs ab. Wenn ein Gutachter einwendet, Bankenindex und Zahlungsdienstleisterindex unterschieden sich in vielem, dann ist dieser Vergleich die Antwort: Hier werden Unternehmen desselben Sektors verglichen, deren einziger relevanter Unterschied die Teilnahme ist.

**Einschränkung, die ins Paper gehört:** Die Teilnahme ist selbstgewählt, denn die Unternehmen mussten sich bewerben. Die Auswahl misst also nicht den kausalen Effekt der Teilnahme, sondern die Überraschung über eine Auswahlentscheidung bei bereits bekundetem Interesse. Für ein Ereignisfenster von einem Tag ist das genau die richtige Interpretation.

### C. Zwei Kollisionsrisiken
1. **19.12.2025:** Ratsposition und vier Sätze Änderungsanträge am selben Tag. Entscheidung: gemeinsam als ein Ereignis behandeln.
2. **13. und 14.07.2026:** erster Trilog und Auswahl der Piloten an aufeinanderfolgenden Tagen. Bei einem zweitägigen Fenster überlappen sie. Entscheidung vorab: Für den Auswahl-Innengruppenvergleich wird ein Eintagesfenster verwendet.

### D. Stand
24 Ereignisse: 18 kodiert (davon eines mit Kollisionsvermerk), 3 warten auf Dokumentenlektüre, 3 auf Verifikation.

---

## Nachtrag v1.8 (18.09.2026): Pilotauswahl im Detail verifiziert
Pressemitteilung der EZB vom 14.07.2026: mehr als 50 Bewerbungen, **36 ausgewählte Zahlungsdienstleister**, Banken und Nichtbanken, breite geografische Streuung. Der Pilot läuft bei der EZB und 19 nationalen Zentralbanken.

Zwei Details, die den Innengruppenvergleich verbessern:
1. Die **Namen der 36** sind auf der EZB-Pilotseite veröffentlicht. Damit ist der Vergleich ausgewählt gegen nicht ausgewählt unter börsennotierten Anbietern tatsächlich umsetzbar. Die Liste wird als Nächstes übertragen.
2. Die Ausgewählten sind in **verteilende, akquirierende und doppelrollige** Anbieter unterteilt. Das liefert eine zweite Dimension innerhalb der Behandelten: Wer Händler anbindet, konkurriert direkter mit dem Kartengeschäft als wer nur Endkunden bedient.

---

## Nachtrag v1.9 (18.09.2026): Eine Datenlücke und ein neues Ereignis

### A. Die Namen der 36 Anbieter sind nicht abrufbar
Die EZB-Pilotseite verweist für die Liste auf die Pressemitteilung, und diese nennt im Text nur die Zahl. Über die mir zugänglichen Seiten sind die Namen nicht zu bekommen.

**Konsequenz:** Der Innengruppenvergleich ausgewählt gegen nicht ausgewählt ist derzeit **nicht umsetzbar**. Ich trage ihn als offenen Punkt und nicht als vorhandenen Test. Zwei Wege bleiben: die Liste in einer PDF-Anlage oder einer nationalen Zentralbank-Meldung suchen, oder den Test streichen und das im Paper offenlegen.

Das ist die zweite Stelle in diesem Projekt, an der eine attraktive Idee an der Datenverfügbarkeit hängt. Beim letzten Paper war es die Reservenverzinsung. Der Unterschied ist, dass wir es diesmal vor der Schätzung merken.

### B. Neues Ereignis, drei Tage alt
**15.09.2026:** Die EZB ruft E-Commerce- und Mobile-Commerce-**Händler** auf, sich für den Piloten zu bewerben, Frist 27.10.2026. Das fügt der Wertschöpfungskette einen vierten Querschnitt hinzu, fällt aber nach dem geplanten Schätzfenster und wird für die Out-of-Sample-Erweiterung vorgemerkt.

### C. Stand
25 Ereignisse, 20 kodiert. Offen: drei Ausschussdokumente, zwei Verifikationen, die Anbieterliste.

---

## Nachtrag v1.10 (18.09.2026): Firmenuniversum und Schätzcode

### A. Firmenuniversum, 51 Unternehmen in fünf Gruppen
`data/hand/firm_universe_v0.csv`:
- **30 börsennotierte Euro-Banken** aus 11 Ländern, ausgewählt nach Einlagenfinanzierung und dokumentierter Beteiligung am Verfahren. Mediobanca ist bewusst als Bank mit niedriger Einlagenquote dabei, damit der Querschnitt Variation hat und nicht nur Niveau.
- **10 Zahlungsdienstleister und Kartennetzwerke**, getrennt in Netzwerke (Mastercard, Visa, American Express), Euro-Acquirer (Nexi, Worldline, Adyen) und übrige.
- **2 Gerätehersteller** (Apple, Alphabet) für den NFC-Zugangskanal.
- **2 Bigtech** auf der Akzeptanzseite (Amazon, Meta).
- **7 Nicht-Euro-Kontrollbanken** aus Schweden, Dänemark, Norwegen, Großbritannien und der Schweiz mit ähnlicher Einlagenstruktur. Sie tragen den Falsifikationstest F2.

Alle Tickersymbole sind als zu prüfen markiert. Ich habe sie nicht als gesichert eingetragen, weil ein falsches Symbol still die falsche Zeitreihe zieht.

### B. Schätzcode steht und ist getestet
`code/eventstudy.py`, drei Tests grün:
1. **Erste Stufe:** Abnormale Renditen aus einem Dreifaktormodell, geschätzt auf einem sauberen Fenster, das alle Ereignistage plus zehn Handelstage Abstand ausschließt.
2. **Zweite Stufe:** CAR auf Exposition mal kodierte Richtung, mit Firmen- und Ereignis-Fixed-Effects. Standardfehler geclustert auf Firmenebene plus Leave-one-out-Jackknife.
3. **Inferenz:** Permutation der Expositionswerte **innerhalb der Gruppe**, damit die Permutation nicht Banken gegen Kartennetzwerke vertauscht.

Getestet mit synthetischen Daten: Ein eingebauter Effekt von 0,05 wird mit Abweichung unter 0,02 und t über 3 wiedergefunden; ohne Effekt wird nicht abgelehnt.

### C. Was jetzt noch fehlt
Nur noch Daten: Kurse, Faktoren und die Einlagenquoten aus der EBA-Transparenzübung. Der gesamte Rechenweg von Rohkursen bis zur Ergebnistabelle ist vorhanden und geprüft.

---

## Nachtrag v1.11 (19.09.2026): Kodierung eingefroren, Kurse eingetroffen

Die Kursdaten wurden hochgeladen. **Vor jeder Berechnung aus diesen Daten** wurden die Ereigniskodierung und das Firmenuniversum per SHA-256 eingefroren (`docs/coding_freeze.sha256`). Die Datei `prices_daily.csv` wurde bis zu diesem Punkt nur auf Vollständigkeit geprüft (Zeilenzahl, Tickerzahl, Zeitraum), nicht auf Renditen.

**Vorab festgelegte Hauptspezifikation für den Fall fehlender EBA-Daten:** Da die Einlagenquoten noch nicht vorliegen, wird die Exposition zunächst als **Gruppenindikator** geführt (Bank, Anbieter, Gerätehersteller jeweils mit Exposition 1 in der eigenen Gruppe; Nicht-Euro-Kontrollbanken als Referenz mit Richtung 0). Das ist der binäre Spezialfall der registrierten Gleichung Exposition × Richtung. Die kontinuierliche Spezifikation mit Einlagenquoten folgt, sobald die EBA-Daten vorliegen, und ersetzt diese nicht nachträglich, sondern wird daneben berichtet.

Ausgeschlossen vorab: Ereignisse mit Status `to_verify` (ECOFIN 08.07.2025, Trilog 13.07.2026) sowie das Ereignis nach Ende der Faktorreihe (15.09.2026).

---

## Nachtrag v1.12 (21.09.2026): Erste Ergebnisse der binären Spezifikation

Geschätzt nach dem Einfrieren (siehe v1.11), Eintagesfenster, Firmen- und Ereignis-Fixed-Effects, 49 Firmen, 22 Ereignisse, 1.042 Beobachtungen.

| Koeffizient (pp je Einheit kodierter Richtung) | Eintagesfenster | t (Jackknife) | Zweitagesfenster | t |
|---|---|---|---|---|
| Gepoolt | 0,055 | 0,37 | 0,023 | 0,12 |
| Banken | 0,101 | 0,62 | 0,183 | 0,86 |
| Zahlungsdienstleister | −0,147 | −0,36 | −0,510 | −1,81 |
| Gerätehersteller und Bigtech | 0,867 | 1,68 | 1,425 | 1,86 |

**Placebo-Daten (gültiger Falsifikationstest für die binäre Spezifikation):** Der Bankenkoeffizient von 0,118 pp liegt im Band der 500 Placebo-Ziehungen (95 %: −0,50 bis 0,54 pp), p = 0,62.

**Lesart:** Kein nachweisbarer Effekt in der registrierten binären Spezifikation. Der Bankenkoeffizient hat das vorhergesagte Vorzeichen, ist aber von Zufallstagen nicht zu unterscheiden. Der Gerätehersteller-Koeffizient beruht vollständig auf einem Ereignis (19.12.2025) mit vier Firmen; ohne dieses Ereignis ist er null. Bei den Zahlungsdienstleistern zeigt sich kein konsistentes Muster, im Zweitagesfenster sogar das Gegenvorzeichen.

**Explorativ, nicht registriert:** Die Differenz Euro-Banken minus Nicht-Euro-Banken hat bei 8 von 10 bankenrelevanten Ereignissen das vorhergesagte Vorzeichen (einseitiger Vorzeichentest p ≈ 0,055). Das ist eine nachträgliche Beobachtung und wird so gekennzeichnet.

**Methodischer Fehler gefunden und nicht berichtet:** Der zuerst gerechnete F2-Test (Kontrollbanken erhalten dieselbe Richtung wie Euro-Banken) ist in dieser Spezifikation mit den Ereignis-Fixed-Effects kollinear und daher nicht identifiziert. Er wurde verworfen und durch den Placebo-Daten-Test ersetzt.

**Noch ausstehend:** Die kontinuierliche Spezifikation mit Einlagenquoten ist die registrierte Hauptspezifikation und nutzt Variation innerhalb der Bankengruppe. Sie braucht die EBA-Daten.

---

## Nachtrag v1.13 (21.09.2026): Festlegung der kontinuierlichen Spezifikation, vor ihrer Schätzung

Die EBA-Daten liegen vor. Aus der Codeliste: Instrument 30 = Einlagen, 31 = davon Sichteinlagen und laufende Konten; Sektor 301 = nichtfinanzielle Unternehmen, 401 = private Haushalte. Festgelegt **vor** der ersten Schätzung mit kontinuierlicher Exposition:

1. **Primäres Maß (wie registriert, vergleichbar mit Burlon et al.):** Einlagen von Haushalten und nichtfinanziellen Unternehmen (Sektoren 401 und 301, Instrument 30) geteilt durch die gesamten Verbindlichkeiten (Position 2321214).
2. **Sekundäres Maß (aus Proposition 1 abgeleitet):** Sichteinlagen derselben Sektoren (Instrument 31) geteilt durch die gesamten Verbindlichkeiten. Sichteinlagen sind das, was eine Haltegrenze direkt erfasst.
3. **Stichtag:** 31.03.2023, der letzte Meldestichtag vor dem Kommissionsvorschlag vom 28.06.2023. Nie aktualisiert.
4. **Skalierung:** Standardisiert innerhalb der Euro-Banken, sodass der Koeffizient die Wirkung einer Standardabweichung der Exposition je Einheit kodierter Richtung misst.
5. **Spezifikation:** CAR = Firmen-FE + Ereignis-FE + θ · (Exposition × Richtung). Stichprobe: Euro-Banken und Kontrollbanken; Anbieter und Gerätehersteller gehen mit ihrer Gruppenrichtung und Exposition 1 ein, damit die Ereignis-FE auf derselben Stichprobe wie in v1.12 geschätzt werden.
6. **Inferenz:** Jackknife über Firmen; Permutation der Expositionswerte innerhalb der Euro-Banken (hier sinnvoll, weil die Exposition variiert); Placebo-Daten.
7. **Konsolidierungsproblem vorab benannt:** Für Crédit Agricole meldet die EBA den Gesamtkonzern, gehandelt wird Crédit Agricole SA. Die Bank bleibt im Hauptlauf; Robustheit ohne sie.
