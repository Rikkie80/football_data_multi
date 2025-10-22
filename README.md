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
```
---

## Lovelace Card

<img src="https://github.com/user-attachments/assets/b72bbd59-18f9-4e3d-b6ab-ccaaeb274f99" width="300">

```yaml
type: vertical-stack
cards:
  - type: conditional
    conditions:
      - condition: numeric_state
        entity: sensor.eredivisie_nederland_live_wedstrijden
        above: 0
    card:
      type: markdown
      content: >
        ## ⚽ Live Wedstrijden

        {% set matches =
        state_attr('sensor.eredivisie_nederland_live_wedstrijden', 'matches') |
        default([]) %}

        {% if matches | length > 0 %}
          {% for match in matches %}
        **{{ match.home_team }} - {{ match.away_team }}**  

        Score: {{ match.score_home | default('0') }} - {{ match.score_away |
        default('0') }}  

        Status: {{ match.status }} {% if match.minute %}({{ match.minute }}'){%
        endif %}

        ---
          {% endfor %}
        {% else %}

        *Geen live wedstrijden*

        {% endif %}
  - type: markdown
    content: >
      <div style="padding: 16px; text-align: center;">


      {% set next = states('sensor.eredivisie_nederland_volgende_wedstrijd') %}

      {% if next != 'Geen gepland' and next != 'unavailable' and next !=
      'unknown' %}


      <h2 style="margin: 0;">📅 Volgende Wedstrijd</h2>

      {% set home = state_attr('sensor.eredivisie_nederland_volgende_wedstrijd',
      'thuisteam') %}

      {% set away = state_attr('sensor.eredivisie_nederland_volgende_wedstrijd',
      'uitteam') %}

      {% set home_crest =
      state_attr('sensor.eredivisie_nederland_volgende_wedstrijd',
      'thuisteam_crest') %}

      {% set away_crest =
      state_attr('sensor.eredivisie_nederland_volgende_wedstrijd',
      'uitteam_crest') %}

      {% set datum =
      state_attr('sensor.eredivisie_nederland_volgende_wedstrijd', 'datum') %}


      <div style="display: flex; justify-content: space-around; align-items:
      center; margin: 20px 0;">
        <div>
          <b>{% if home_crest %}<img src="{{ home_crest }}" width="25" style="display: block; margin: 0 auto;">{% endif %}
          {{ home }} -
          {{ away }}
          {% if away_crest %}<img src="{{ away_crest }}" width="25" style="display: block; margin: 0 auto;">{% endif %}
          </b>
        </div>
      </div>

      <p style="color: var(--secondary-text-color);">

      {% set dag_eng = as_timestamp(datum) | timestamp_custom('%A', true) %}

      {% set maand_eng = as_timestamp(datum) | timestamp_custom('%B', true) %}


      {% set dagen = {'Monday': 'Maandag', 'Tuesday': 'Dinsdag', 'Wednesday':
      'Woensdag', 'Thursday': 'Donderdag', 'Friday': 'Vrijdag', 'Saturday':
      'Zaterdag', 'Sunday': 'Zondag'} %}

      {% set maanden = {'January': 'Januari', 'February': 'Februari', 'March':
      'Maart', 'April': 'April', 'May': 'Mei', 'June': 'Juni', 'July': 'Juli',
      'August': 'Augustus', 'September': 'September', 'October': 'Oktober',
      'November': 'November', 'December': 'December'} %}

      {% set dag_nl = dagen[dag_eng] | default(dag_eng) %}

      {% set maand_nl = maanden[maand_eng] | default(maand_eng) %}

      🕐 {{ dag_nl }} {{ as_timestamp(datum) | timestamp_custom('%d', true) }}
      {{ maand_nl }} {{ as_timestamp(datum) | timestamp_custom('%Y om %H:%M',
      true) }}

      📍 Ronde {{ state_attr('sensor.eredivisie_nederland_volgende_wedstrijd',
      'matchday') | default('?') }}

      </p>


      {% else %}

      <h2>📅 Volgende Wedstrijd</h2>

      <p style="color: var(--secondary-text-color);">Geen geplande wedstrijden
      gevonden</p>

      {% endif %}


      </div>
  - type: custom:flex-table-card
    title: 🏆 Eredivisie Stand
    entities:
      include: sensor.eredivisie_nederland_stand
    columns:
      - name: Pos
        data: standings
        modify: x.position
        align: center
      - name: Team
        data: standings
        modify: >-
          '<img src="' + x.team.crest + '" style="height: 24px; vertical-align:
          middle; margin-right: 8px;">' + x.team.name
        align: left
      - name: Matches
        data: standings
        modify: x.playedGames
        align: center
      - name: Points
        data: standings
        modify: x.points
        align: center
      - name: +/-
        data: standings
        modify: x.goalDifference
        align: center
      - name: Goals
        data: standings
        modify: x.goalsFor + ':' + x.goalsAgainst
        align: center
    card_mod:
      style: |
        ha-card {
          overflow-x: auto;
        }
        tbody tr:nth-child(-n+4) {
          border-left: 3px solid #4CAF50 !important;
        }
        tbody tr:nth-last-child(-n+2) {
          border-left: 3px solid #f44336 !important;
        }
        tbody tr:hover {
          background-color: var(--table-row-background-hover-color) !important;
        }
        th {
          background: var(--secondary-background-color) !important;
          color: var(--secondary-text-color) !important;
          position: sticky !important;
          top: 0 !important;
          z-index: 10 !important;
        }
        td:nth-child(4) {
          font-weight: bold !important;
          font-size: 16px !important;
        }
title: Eredivisie
```

<a href="https://www.buymeacoffee.com/rikkie80" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
```

