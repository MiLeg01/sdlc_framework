# Agent Commons Unternehmenspräsentation — vollständiger Sprechertext

**Gesamtdauer:** 27 Minuten 30 Sekunden

## 1. Mit der Arbeit beginnen, nicht mit der Einrichtung

**Präsentationskapitel: Agent Commons Library / Start with the work. Not the setup.**

**Zeit:** 00:00–01:20

### Sprechertext

„Guten Morgen und herzlich willkommen zu meinem Vortrag über Agent Commons – wiederverwendbare technische Methoden für AI-unterstützte Projekte.

Ich werde immer wieder gefragt: Wie setzt man eigentlich ein AI-Projekt sauber auf?

Um darauf eine ehrliche Antwort zu finden, habe ich meine bisherigen Projekte nebeneinandergelegt und untersucht, was ich am Anfang tatsächlich jedes Mal mache.

Das Muster war eindeutig. Zuerst erstelle ich eine `AGENTS.md`. Darin halte ich den Scope fest: Ziel, Grenzen, schreibgeschützte Bereiche, erwartete Ergebnisse und Regeln für den Agent. Danach wähle oder erstelle ich die benötigten Skills. Ich definiere Nachweise, Tests, Validierung und bei Bedarf ein Dashboard.

Die Projekte selbst waren sehr unterschiedlich. Es ging um Modernisierung, Entwicklung, Recherche oder Architektur. Der technische Start war aber erstaunlich ähnlich.

Dabei habe ich erkannt: Ich richte nicht nur einzelne Projekte ein. Ich baue immer wieder dieselbe technische Methodik neu auf.

Aus dieser Beobachtung ist Agent Commons entstanden. Die wiederverwendbare Methode wird einmal gepflegt. Der konkrete Projektkontext bleibt lokal. So kann das nächste Projekt früher mit der eigentlichen Arbeit beginnen.“

## 2. Jedes Projekt baut dasselbe Fundament neu

**Präsentationskapitel: The repetition problem**

**Zeit:** 01:20–02:40

### Sprechertext

„Als ich diese Projekte nebeneinandergelegt habe, wurde das Muster sichtbar: Die Aufgaben unterscheiden sich. Das Fundament darunter wiederholt sich.

Eine Analyse eines Altsystems braucht anderes Fachwissen als eine Neuentwicklung oder eine Recherche. Trotzdem beginnen wir immer wieder mit ähnlichen Grundlagen: erst inventarisieren, dann interpretieren; Aussagen mit Quellen belegen; Akzeptanzkriterien festhalten; Tests und Validierung definieren; Ergebnisse dokumentieren und sauber übergeben.

Bleibt diese Methodik in einem einzelnen Projekt, wird sie kopiert, angepasst, vergessen und später erneut erfunden. Das Unternehmen hat für die Erfahrung bereits bezahlt. Das nächste Team kann trotzdem nicht verlässlich damit starten.

Dabei entstehen auch Qualitätsunterschiede. Ein Team dokumentiert Nachweise sauber, ein anderes arbeitet nur mit Zusammenfassungen. Ein Team verwendet Tests als Beleg, ein anderes ergänzt sie erst nach der Umsetzung. Gemeinsame Methoden schaffen eine verlässlichere Ausgangsbasis, ohne alle Projekte in denselben starren Prozess zu zwingen.“

## 3. Projektdaten bleiben lokal. Die Methode wird geteilt.

**Präsentationskapitel: The central idea**

**Zeit:** 02:40–03:55

### Sprechertext

„Die zentrale Idee passt in einen Satz: Die Fakten bleiben im Projekt. Die wiederverwendbare Arbeitsweise wird geteilt.

Links sehen Sie alles, was zum konkreten Vorhaben gehört: Quellcode, Geschäftsregeln, Anforderungen, Zugangsdaten, Entscheidungen, Sprache und Marke. Das bleibt lokal und unter der Kontrolle des Projekts.

Rechts steht die Methode: wie wir analysieren, testen, Diagramme erzeugen, Dashboards aufbauen und Ergebnisse prüfen. Diese Arbeitsweise kann bewertet, verallgemeinert und vom nächsten Team wiederverwendet werden.

Agent Commons ist daher keine zentrale Ablage für Projektdaten. Es ist eine gemeinsame Bibliothek erprobter Vorgehensweisen.

Einfach gesagt: Wir bewegen das Arbeitsrezept, nicht die Projektdaten.“

## 4. Bausteine und Capability-Navigator

**Präsentationskapitel: What is what?**

**Zeit:** 03:55–06:20

### Sprechertext

„Damit wir im weiteren Verlauf dieselben Begriffe verwenden, erkläre ich die wichtigsten Bausteine kurz.

Ein Skill ist ein wiederverwendbares Arbeitsrezept. Er beschreibt, wie eine bestimmte Aufgabe erledigt werden soll.

Ein Agent ist eher mit einer spezialisierten Kollegin oder einem spezialisierten Kollegen vergleichbar. Er erhält eine eigenständige Verantwortung, wenn eine getrennte fachliche Beurteilung die Qualität verbessert.

Ein Tool arbeitet deterministisch. Es zählt, inventarisiert, rendert, prüft oder transformiert. Wo ein exaktes Ergebnis erforderlich ist, darf nicht geraten werden.

Ein Archetype ist ein Projektrezept für die Initialisierung. Er wählt und priorisiert passende Capabilities. Danach bleibt er als Konfiguration und Herkunftsnachweis im Projekt. Zur Laufzeit wird ein Skill aufgerufen, nicht der Archetype selbst.

Ein Overlay ergänzt eine querschnittliche Anforderung, zum Beispiel Nachverfolgbarkeit, ein Dashboard, Branding oder Lokalisierung. Ein Adapter verbindet dieselbe Methode mit verschiedenen Runtimes. Ein Eval prüft automatisiert, ob eine Capability weiterhin das versprochene Verhalten zeigt. Und ein Template gibt einem Ergebnis Struktur, ersetzt aber keine technische Beurteilung.

Diese Begriffe reichen für den Einstieg. Im Navigator können wir später nach einem konkreten Problem suchen, eine Capability auswählen und ihren Zweck, ihre Grenzen und ihre Beziehungen prüfen.“

„Der Navigator ist die praktische Oberfläche für eine spätere Vertiefung. Sie suchen nach einem Problem, wählen eine Capability, lesen ihren Zweck und ihre Grenzen, sehen eine sichere Quellvorschau und erkennen, wo sie verwendet wird.

Entscheidend ist nicht die Anzahl. Entscheidend ist, dass die Präsentation aus demselben kanonischen Katalog erzeugt wird und keine getrennte Werbeinventarliste pflegt.“

„Vom einzelnen Baustein wechseln wir jetzt zur Gesamtstruktur der Bibliothek.“

## 5. Das Capability-Netzwerk

**Präsentationskapitel: Capability network**

**Zeit:** 06:20–07:00

### Sprechertext

„Dieses Netzwerk ist ein kurzer Nachweis dafür, dass die Bibliothek nicht nur gesammelt, sondern bewusst zusammengesetzt ist. Skills sind über erzeugte Beziehungen mit Archetypes, Tools, Agents, Adaptern und Evals verbunden.

Ich kann `analyze-legacy-system` auswählen und sehe sofort die Capabilities, die dieses Vorgehen unterstützen. Das Netzwerk dient der Erkundung. Wir müssen hier nicht jeden Knoten einzeln besprechen.“

## 6. Eine Methode, an jedes Werkzeug angepasst

**Präsentationskapitel: How it works**

**Zeit:** 07:00–09:10

### Sprechertext

„Bevor wir ein Projekt initialisieren, lesen wir die Architektur von links nach rechts.

Erstens enthält Agent Commons jeweils eine geprüfte Fassung eines Arbeitsrezepts. Zweitens übersetzt ein kleiner Adapter dieses Rezept in die Form, die das jeweilige KI-Werkzeug versteht. Drittens verwendet das Werkzeug die Methode innerhalb des Projekts. Dort bleiben Quellbestand, Erkenntnisse und Entscheidungen.

Das ist die obere Reihe: eine gemeinsame Methode, angepasst an verschiedene Werkzeuge, ohne getrennte Fassungen pflegen zu müssen.

Die untere Reihe zeigt den Projektablauf genauer. Bei der Initialisierung wählen wir einen passenden Archetype oder eine bewusste Kombination. Daraus werden die kanonischen Capabilities als stabile IDs aufgelöst. Zur Laufzeit ruft ein Mensch einen konkreten Skill auf. Dieser arbeitet mit dem lokalen Projektzustand. Tests und Reviews sichern das Ergebnis ab.

Mehr müssen Sie sich aus dieser Architektur nicht merken: Commons liefert die Methode. Das KI-Werkzeug wendet sie an. Das Projekt bleibt die maßgebliche Quelle für die Fakten.

Mit diesem Modell im Kopf starten wir jetzt ein konkretes Projekt.“

## 7. Das Projekt initialisieren und die Demo durchführen

**Präsentationskapitel: How do I start tomorrow?**

**Zeit:** 09:10–19:50

### Sprechertext

„Jetzt wird es praktisch. Ich beginne nicht mit einer langen Liste einzelner Skills, sondern mit dem tatsächlichen Projektziel und dem Skill `initialize-project`.

Die Installation wird durch das Repository verwaltet. Codex ist die standardmäßig verwendete Runtime. Dieselben kanonischen Methoden werden auch für Claude Code, Cline und OpenCode angepasst, soweit die jeweilige Runtime sie unterstützt.

Für diese Demo verwende ich ein offen lizenziertes IBM-Beispiel zu z/OS Connect. Es enthält COBOL, PL/I, Java, OpenAPI, CICS und IMS. Der gesamte Quellbestand ist schreibgeschützt.

Ich beginne beim frischen Projektstand. Dort liegt im Wesentlichen nur `client_input`. Das Ziel lautet: den Quellbestand analysieren, Anforderungen ableiten, die Modernisierung schätzen, OpenSpec vorbereiten und ein Dashboard erzeugen.

Die Grafik hat zwei Leserichtungen. Links folgen wir den Schritten nach unten: menschliche Eingabe, Initialisierung, bei Bedarf ein menschlicher Prüfpunkt, deterministische Tools und das Ergebnis.

Innerhalb der Initialisierung lesen wir von links nach rechts: Ziel und Arbeitsbereich prüfen, passende Archetypes auswählen, stabile Capability-IDs ohne Doppelungen auflösen und die Konfiguration schreiben.

Ein Mensch wird nur bei echten Lücken gefragt. Exakte Aufgaben wie Inventarisierung und Konfigurationsprüfung erledigen Tools.

Das Ergebnis sind Projektanweisungen, `.agent-commons.yaml`, die aufgelösten Capabilities und genau eine nächste Aktion. Der Archetype bleibt Konfiguration. Zur Laufzeit wird ein Skill aufgerufen.

Jetzt starte ich die Initialisierung. Der Vorgang dauert normalerweise einige Minuten. Wir lassen ihn im Hintergrund weiterlaufen und wechseln anschließend durch die vorbereiteten Projektstände bis zum analysierten Dashboard.“

**JETZT `initialize-project` STARTEN**

Im vorbereiteten Codex-Task `$initialize-project` aufrufen. Die echte Ausgabe 20 bis 40 Sekunden sichtbar lassen. Danach den vorbereiteten initialisierten Stand öffnen, die Analyse starten und über die vorbereiteten Zwischenstände zum Dashboard weitergehen. Anschließend zu `#compose` wechseln.

„Das ist der fertig initialisierte Stand desselben Quellbestands.

Wichtig sind vor allem die Projektanweisungen und die Datei `.agent-commons.yaml`. Das Manifest dokumentiert die gewählten Archetypes, die Runtime, die schreibgeschützte Quellgrenze, die erwarteten Ergebnisse, die Regeln für OpenSpec und TDD, die Dashboard-Konfiguration und den Zustand der Capabilities.

Das Dashboard ist bereits als gültige Hülle vorhanden. Es zeigt aber ehrlich, was noch nicht analysiert wurde. Auch der nächste Schritt ist eindeutig: `analyze-legacy-system` ausführen.

Ein initialisiertes Projekt ist noch kein analysiertes Projekt. Das Gerüst zeigt, was ausgewählt wurde, was noch unbekannt ist und welche Capability als Nächstes arbeiten soll. Das Team erhält damit einen nachvollziehbaren und wiederaufnehmbaren Zustand statt einer verfrühten Erfolgsmeldung.“

„Vom initialisierten Projektstand starte ich jetzt `analyze-legacy-system`.

Zu Beginn sollten Sie das Inventar, die Aufteilung in klar begrenzte Analysepakete, die Zuständigkeiten und die Abdeckungsprüfung sehen. Diese Analyse geht bewusst in die Tiefe und dauert länger, als wir auf einer Bühne warten sollten. Wir lassen sie weiterlaufen und springen zu einem bereits abgeschlossenen Stand.“

„Diese Zwischenstandsordner sind keine getrennten Demos.

Sie enthalten dieselben 77 Quelldateien mit derselben portablen Prüfsumme. Der erste Stand enthält nur den Quellbestand. Der zweite ist initialisiert. Im dritten sind Analyse, Anforderungen, Schätzung und Dashboard abgeschlossen. Der vierte ergänzt das geprüfte OpenSpec-Planungspaket.

Ein Validator prüft beide Richtungen: Dateien, die in einer Stufe vorhanden sein müssen, und Dateien späterer Stufen, die dort noch nicht vorhanden sein dürfen. Dadurch kann ich nicht versehentlich den falschen Ordner als Ergebnis zeigen.

Es sind eingefrorene Lebenszyklusstände desselben Projekts. So können wir in der Zeit vorspringen, ohne vorzutäuschen, die Arbeit sei sofort erledigt.“

„Das ist der zentrale Nutzen der Demo.

Zuerst die Managementübersicht: Alle 76 relevanten Artefakte sind erfasst. Die acht vorgesehenen Analysepakete wurden vollständig geprüft. Das Dashboard nennt aber auch die Grenze: Wir sehen hier ein öffentliches IBM-Lernbeispiel. Das ist keine belastbare Grundlage für die Aufwandsschätzung eines großen Produktivsystems.

Als Nächstes sehen wir Zusammensetzung und Komplexität. Der Quellbestand umfasst COBOL, PL/I, Java, OpenAPI, CICS, IMS und generierte Zuordnungsartefakte. Die Zeilenzahl ist groß. Ein wesentlicher Anteil ist jedoch dupliziert oder generiert. Die schwierigere Aufgabe liegt an den Integrationsgrenzen und im Fehlerverhalten.

Danach kommen Architektur und Schnittstellen. Wir sehen die aufrufenden Host-Systeme, die Grenze von z/OS Connect, den Java-Dienst, die API-Operationen und eine mögliche Zielstruktur.

Im Quellbestand gibt es weder eine ausführbare Testsuite noch eine CI-Konfiguration. Eine statische Analyse kann daher keine Laufzeitgleichheit beweisen. Charakterisierungstests sind eine Eintrittsbedingung für die Modernisierung und keine spätere Zusatzarbeit.

Nun zu einem konkreten Befund. Der Java-Endpunkt übernimmt den Autorfilter als Zeichenkette. Anschließend wird diese Zeichenkette in einer Map gesucht, deren Schlüssel `Author`-Objekte sind. Deshalb liefert ein nicht leerer Autorfilter den Status 404, statt den Wert des Autors korrekt zu vergleichen. Die Analyse dokumentiert diesen Fehler als `JAVA-DEF-01` und verknüpft ihn mit den genauen Stellen im Quellcode.

Dieser Befund lässt sich überprüfen, betrifft ein sichtbares API-Verhalten und kann direkt eine Anforderung und einen testbaren Vertrag speisen.

Das Dashboard hält auch Unsicherheit sichtbar. Produktionsmengen, Wiederanlaufziele, Sicherheitsverantwortung und die vollständige Liste der Host-Aufrufer sind nicht belegt. Solche Punkte werden nicht erraten, sondern als Entscheidungstore in Planung und Schätzung aufgenommen.

Für die Führungsebene beantwortet das Dashboard: Was wissen wir? Was ist noch unsicher? Was ist die nächste verantwortbare Investition? Für Architektur und Entwicklung verbindet derselbe Nachweis Systeme, Schnittstellen, Anforderungen, Spezifikationen, Tests und offene Fragen.“

## 8. Vom Analyseaufruf bis zur geprüften Umsetzung

**Präsentationskapitel: How the analysis runs**

**Zeit:** 19:50–22:20

### Sprechertext

„Diese Folie zeigt zuerst, wie `analyze-legacy-system` tatsächlich abläuft.

Noch vor der Laufzeit hat der Archetype die üblichen Capabilities ausgewählt. `.agent-commons.yaml` hält ihre stabilen IDs und die Projektgrenzen fest. Der Archetype wird aber nicht ausgeführt. Der Mensch startet den Skill.

Die Runtime lädt Governance, Manifest, Zustand, Projektwissen und vorhandene Nachweise. Danach legt der Koordinator auf Basis des Inventars einen gemeinsamen Nenner für die Abdeckung fest. Er teilt die Arbeit in klar abgegrenzte, überschneidungsfreie Analysepakete.

Die spezialisierten Worker liefern ausschließlich geprüfte Nachweispakete zurück. Sie verändern nicht gemeinsam denselben Zustand. Der Koordinator führt die Ergebnisse zusammen, aktualisiert die vorgesehenen Artefakte und bleibt Eigentümer des Gesamtbilds.

Am Ende steht eine harte Prüfung: Ist der vereinbarte Umfang vollständig? Sind die Ergebnisse konsistent? Ist das Dashboard aktuell? Erst dann erhält der Mensch das Ergebnis und die nächste Aktion. Die Analyse beginnt keine Umsetzung.

Danach folgt die Nachweiskette. Aus `JAVA-DEF-01` entstehen `MOD-REQ-001` und `MOD-REQ-002`. Die OpenSpec für `redbook-api` übersetzt sie in beobachtbare Szenarien. Erst nach Prüfung und Freigabe beginnt TDD mit einem Test, der aus dem richtigen Grund fehlschlägt: RED. Dann folgen die kleinste Änderung, GREEN, REFACTOR und die breiteren Prüfungen.

Ein grüner Test allein genügt nicht. Spezifikation, Umsetzung, Tests und Nachweise müssen am Ende wieder zusammenpassen. Im aktuellen Projektstand ist die Umsetzung wegen offener fachlicher Entscheidungen zu Recht noch blockiert.“

## 9. `review-for-commons`: aus Erfahrung wird ein geprüfter Vorschlag

**Präsentationskapitel: Contribution: review-for-commons**

**Zeit:** 22:20–23:35

### Sprechertext

„In Projekten entstehen nützliche lokale Methoden. Wir kopieren sie nicht direkt in Agent Commons.

`review-for-commons` prüft zuerst: Ist das Verhalten auch außerhalb dieses Projekts nützlich? Deckt Commons dieselbe Verantwortung bereits ab? Lässt sich die Methode sicher verallgemeinern? Und welcher Capability-Typ wäre passend?

Das Ergebnis bleibt als bereinigter Vorschlag im Projekt. Es wird nichts installiert, aktiviert oder automatisch in Commons übernommen. Ein Mensch wählt einen genau benannten Kandidaten aus oder entscheidet bewusst, dass die Capability im Projekt bleiben soll.

Diese Grenze schützt beide Seiten. Commons wird nicht mit beinahe gleichen Varianten überfüllt. Gleichzeitig gelangen keine Kundenannahmen, proprietären Nachweise oder internen Pfade versehentlich in die gemeinsame Bibliothek.“

## 10. `promote-to-commons`: verallgemeinern und erneut prüfen

**Präsentationskapitel: Contribution: promote-to-commons**

**Zeit:** 23:35–24:45

### Sprechertext

„`promote-to-commons` bindet genau den freigegebenen Kandidaten und stellt ihn noch einmal auf den Prüfstand.

Ist der Nachweis stark genug? Enthält der Vorschlag vertrauliche Details? Ist die Lizenz geklärt? Verdoppelt er eine bestehende Capability? Was ist die kleinste sinnvolle, Runtime-neutrale Abstraktion?

Erst danach ändern wir die kanonische Bibliothek. Wir ergänzen oder aktualisieren Evals, synchronisieren Kataloge und Adapter, erneuern erzeugte Daten und führen die Repository-Prüfungen aus.

Übernahme bedeutet nicht Kopieren. Sie bedeutet Verallgemeinerung unter klarer Governance.

Das Ergebnis kann eine neue Capability sein. Es kann aber auch eine Erweiterung, Zusammenführung, Aufteilung, Ablösung oder bewusst gar keine Änderung sein.“

## 11. Eine gemeinsame Basis, unabhängige Projekte

**Präsentationskapitel: Why this matters to the company**

**Zeit:** 24:45–26:10

### Sprechertext

„Das ist der Nutzen auf Unternehmensebene: eine gemeinsame geprüfte Basis und gleichzeitig unabhängige Projekte.

Eine aktuelle Commons-Version steht allen neuen Projekten zur Verfügung. Projekt A, B und C können damit parallel beginnen. Jedes behält seinen eigenen Umfang, Zustand, seine Nachweise und seine Ergebnisse. Die Projekte teilen also nicht ihre laufende Arbeit und sind nicht voneinander abhängig.

Trotzdem kann jedes Projekt eine wiederverwendbare Erkenntnis vorschlagen. Solche Vorschläge fließen an einer einzigen Governance-Stelle zusammen. Dort werden sie geprüft, verallgemeinert, validiert und nur bei ausreichender Qualität übernommen.

Erst eine neue geprüfte Commons-Version verändert den Ausgangspunkt künftiger Projekte. Es gibt keine direkte Abhängigkeit von Projekt zu Projekt und keine automatische Übernahme.

Das schafft Konsistenz ohne zentrale Projektsteuerung. Teams starten mit derselben technischen Grundqualität, arbeiten aber weiterhin selbstständig. Unternehmenswissen wächst kontrolliert, ohne lokale Projektgrenzen aufzuweichen.“

## 12. Jedes Projekt lehrt uns etwas

**Präsentationskapitel: The company-wide default**

**Zeit:** 26:10–27:30

### Sprechertext

„Jedes Projekt lehrt uns etwas. Die Frage ist, ob dieses Wissen in dem Projekt bleibt, in dem es entstanden ist, oder ob das nächste Team bereits damit beginnen kann.

Agent Commons bietet einen geregelten Weg von der Projekterfahrung über die Prüfung bis zur wiederverwendbaren Capability und von dort zurück in das nächste Projekt.

Wenn Sie in Ihrem Team ein reales Vorhaben haben, bei dem diese Arbeitsweise helfen könnte, laden Sie mich zu einer vertiefenden Durchsprache ein. Dann prüfen wir die Methode am tatsächlichen Anwendungsfall, an den tatsächlichen Grenzen und an den tatsächlich verfügbaren Nachweisen.

So wird aus jedem Projekt ein besserer Ausgangspunkt für das nächste.“
