from __future__ import annotations

from app.data.database.components import ComponentType
from app.data.database.database import DB
from app.data.database.item_components import ItemComponent, ItemTags
from app.engine import (action, banner, combat_calcs, engine, equations,
                        image_mods, item_funcs, item_system, skill_system)
from app.engine.game_state import game
from app.engine.objects.unit import UnitObject
from app.utilities import utils, static_random


class DoNothing(ItemComponent):
    nid = 'do_nothing'
    desc = 'does nothing'
    tag = ItemTags.CUSTOM

    expose = ComponentType.Int
    value = 1

class ManaCostPerUse(ItemComponent):
    nid = 'mana_cost_per_use'
    desc = "Item subtracts the specified amount of Mana per use. MANA must be defined in the equations editor. If unit does not have enough mana the item will not be usable."
    tag = ItemTags.USES

    expose = ComponentType.Int
    value = 1

    def available(self, unit, item) -> bool:
        return unit.get_mana() >= self.value

    def is_broken(self, unit, item) -> bool:
        return unit.get_mana() < self.value

    def on_broken(self, unit, item) -> bool:
        if unit.equipped_weapon is item:
            action.do(action.UnequipItem(unit, item))
        return False

    def on_hit(self, actions, playback, unit, item, target, item2, target_pos, mode, attack_info):
        action.do(action.ChangeMana(unit, -self.value))

    def on_miss(self, actions, playback, unit, item, target, item2, target_pos, mode, attack_info):
        action.do(action.ChangeMana(unit, -self.value))

    def reverse_use(self, unit, item):
        action.do(action.ChangeMana(unit, self.value))