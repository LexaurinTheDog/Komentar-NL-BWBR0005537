# Bronnen en controlebewijs

Gecontroleerd op 19 oktober 2026. Zie het [verificatieregister](sources/verification.json) voor de afzonderlijke toegangstijden, HTTP-statussen en hashes.

- [Officiële actuele Wettenbank-ingang](https://wetten.overheid.nl/BWBR0005537), [lokale respons](sources/landing.html): verwijzing naar de versie van 15 augustus 2026 en expliciete geldigheidsverklaring op de raadpleegdatum.
- [Officiële versie-informatie](https://wetten.overheid.nl/BWBR0005537/2026-08-15/0/informatie), [lokale respons](sources/version-information.html).
- [Officiële XML](https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/2026-08-15_0/xml/BWBR0005537_2026-08-15_0.xml), [lokale XML](sources/intake-official.xml), [mechanisch afgeleid tekstbestand](sources/canonical.txt).
- [Oorspronkelijke intake](sources/original-intake.md), [wijzigingenkaart](sources/change-map.json), [brondekking](coverage-evidence.json), [redactionele notities](sources/editorial-notes.json).
- [ABRvS 4 mei 2021, ECLI:NL:RVS:2021:953](case-cards/ECLI-NL-RVS-2021-953.md): toegang na omgevingsrechtelijke inspraak; grenzen van de toepassing en historische context staan op de kaart.
- [ABRvS 2 februari 2022, ECLI:NL:RVS:2022:285](case-cards/ECLI-NL-RVS-2022-285.md): evenredigheid bij discretionaire bevoegdheden, individuele beleidstoepassing en gevolgen van gebrekkige belangenafweging.

Het [zoeklog](sources/case-search-log.json) onderscheidt opgehaalde bronnen van werkelijk in commentaar gebruikte uitspraken. ECLI:NL:CBB:2024:31 is opgehaald en in het lokale corpus aangetroffen, maar nog niet inhoudelijk verwerkt of als dragende autoriteit gebruikt. Aan het ophalen alleen wordt geen inhoudelijke verificatieclaim verbonden. Het [corpuslog](sources/cases/local-corpus-check.json) bewaart de locaties en hashes van de aangetroffen nationale corpusbestanden.

De directe peildatum-URL gaf HTTP 404 en het metadata-XML-verzoek een lege HTTP 204-respons. Beide zijn als onbruikbare verzoekresultaten geregistreerd, niet als canonieke wetstekst. Het officiële XML-bestand is op root-element en BWB-identificatie gecontroleerd.
