# TkTactics

**TkTactics** is a single-player, turn-based strategy board game. You command the blue army, battling against ever-growing waves of red enemy forces controlled by the computer. With each wave, the enemy grows stronger and more aggressive - can you hold the line and lead your troops to victory?

## Requirements

    OS: Linux or Windows
    Python: Version 3.12 or higher

## How to Play

    git clone https://github.com/Yang-Wei-Ting/TkTactics.git
    cd TkTactics/
    python sources/play.py

## Game Overview

### Units

Each unit has a health bar. When a unit’s health reaches zero, it is destroyed.

#### Soldier Units

There are four types of soldier units, each with its own strengths and weaknesses:

##### Infantries

![](images/soldiers/blue_infantry.gif)
![](images/soldiers/red_infantry.gif)

High defense  
Moderate attack range  
Strong against: Cavalries  
Weak against: Archers, Heroes

##### Archers

![](images/soldiers/blue_archer.gif)
![](images/soldiers/red_archer.gif)

High attack range  
Weak attack  
Strong against: Infantries  
Weak against: Cavalries, Heroes

##### Cavalries

![](images/soldiers/blue_cavalry.gif)
![](images/soldiers/red_cavalry.gif)

High mobility  
Strong against: Archers  
Weak against: Infantries, Heroes

##### Heroes

![](images/soldiers/blue_hero.gif)
![](images/soldiers/red_hero.gif)

High attack, health, and mobility  
Strong against: All other soldier unit types

#### Controlling Your Soldier Units

##### Selecting

Press a unit to select it.  
Light blue squares: Available movements  
Red diamond-shaped marker: Attack range

##### Moving and Attacking

Move: Drag the unit onto a light blue square and release.  
Rock and tree tiles require a unit's full mobility for the turn.  
All other tile types cost one mobility point.  
Attack: Drag the unit onto an enemy within attack range and release.

After moving and attacking, a unit turns gray - indicating it can no longer perform any actions until the next turn.

##### Healing

Units automatically heal between enemy waves.

#### Inspecting Enemy Soldier Units

Press an enemy unit to view its attack range and mobility.

#### Leveling Up Soldier Units

Units gain experience by attacking enemies.  
When enough experience is earned, a unit automatically levels up and becomes stronger.

The unit’s level is shown in the upper-left corner of its icon.  

#### Building Units

Currently, there is one type of building units:

##### Barracks

![](images/buildings/barrack.gif)

Used to recruit new soldier units.

#### Recruiting Soldier Units

Earn coins by surviving each enemy wave.  
Spend coins at building units to recruit new soldier units.

How to recruit:  
Click a building unit to open the production panel on the right.  
Click a soldier unit to recruit - blue means you can afford it; gray means you can’t.  
Click one of the highlighted light blue squares to deploy the unit.  
The new unit will become active on your next turn.

## Attributions

| Title                                         | Author     | Source                                                                                          | License                                                       |
|-----------------------------------------------|------------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| Overworld - Grass Biome                       | Beast      | [opengameart.org](https://opengameart.org/content/overworld-grass-biome)                        | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Camping Tent Icon                             | Delapouite | [game-icons.net](https://game-icons.net/1x1/delapouite/camping-tent.html)                       | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)     |
| Horse Face Silhouette Right Side View Variant | SVG Repo   | [svgrepo.com](https://www.svgrepo.com/svg/152103/horse-face-silhouette-right-side-view-variant) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
