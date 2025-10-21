# ⚽ Football Data Multi (Home Assistant Integratie)

Bekijk **standen**, **live wedstrijden** en **geplande wedstrijden** van meerdere competities via [Football-Data.org](https://www.football-data.org/).

## ✨ Functies
- Ondersteunt meerdere competities tegelijk (bijv. Eredivisie, Premier League, Bundesliga)
- Sensors voor:
  - Stand (`_stand`)
  - Volgende wedstrijd (`_next`)
  - Live wedstrijden (`_live`)
- Werkt met de gratis Football-Data API
- Volledig compatibel met Home Assistant en HACS

---

## 🧩 Installatie (HACS)

1. Open HACS → *Integraties*  
2. Klik rechtsboven op **⋮ → Aangepaste repository toevoegen**
3. Vul in:
   - **Repository URL**: `https://github.com/rikkie80/football-data-multi`
   - **Categorie**: *Integratie*
4. Klik **Toevoegen** → vervolgens **Downloaden**
5. Herstart Home Assistant
6. Ga naar **Instellingen → Apparaten & Diensten → Integratie toevoegen**
7. Zoek op: `Football Data Multi`
8. Voer je [Football-Data.org API token](https://www.football-data.org/client/register) in  
   en selecteer de competities (bijv. `DED`, `PL`, `BL1`)

---

## 🧠 Voorbeeld sensoren

```yaml
sensor.eredivisie_stand
sensor.eredivisie_next
sensor.eredivisie_live

sensor.premier_league_stand
sensor.bundesliga_live
