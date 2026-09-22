# Anleitung für die zweite Kodierung (ca. 60 Minuten)

Ziel: unabhängige Prüfung der Ereigniskodierung. Bitte **nicht** das Paper oder die Datei `event_coding_v1.csv` ansehen.

Für jedes Ereignis in `second_coder_sheet.csv` die Spalten ausfüllen, nur auf Grundlage des beschriebenen Inhalts und dessen, was **am Tag des Ereignisses** öffentlich bekannt war. Späteres Wissen (etwa, dass ein Entwurf nie abgestimmt wurde) darf nicht einfließen.

- **procedural_0_1:** 1, wenn der Akt keinerlei Bestimmung zu einem Designparameter enthält.
- **banks / payment_providers / device_gatekeepers:** +1, wenn der Akt die Rente dieser Gruppe gegenüber dem vorherigen Stand erhöht; −1, wenn er sie senkt; 0, wenn neutral oder gemischt; leer, wenn keine Bestimmung diese Gruppe betrifft.
  - Banken verlieren, wenn mehr digitaler Euro gehalten werden kann (höhere Haltegrenze, Unternehmen dürfen halten, Projekt wird wahrscheinlicher). Sie gewinnen bei Mengenbegrenzungen.
  - Zahlungsdienstleister verlieren bei Gebührendeckeln und wenn das Projekt ihre Zahlungsschienen ersetzt.
  - Gerätehersteller verlieren bei erzwungenem Zugang zu Hardware und Software.
- **surprise:** Wie überraschend war der Inhalt angesichts der vorherigen öffentlichen Berichterstattung?

Nach dem Ausfüllen die Datei zurückschicken. Die Übereinstimmung (Cohen's κ je Dimension) wird im Paper berichtet, unabhängig vom Ergebnis.
