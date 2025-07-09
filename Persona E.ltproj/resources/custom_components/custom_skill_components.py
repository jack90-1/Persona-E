from __future__ import annotations

from app.data.database.components import ComponentType
from app.data.database.database import DB
from app.data.database.skill_components import SkillComponent, SkillTags
from app.engine import (action, banner, combat_calcs, engine, equations,
                        image_mods, item_funcs, item_system, skill_system)
from app.engine.game_state import game
from app.engine.objects.unit import UnitObject
from app.utilities import utils, static_random


class DoNothing(SkillComponent):
    nid = 'do_nothing'
    desc = 'does nothing'
    tag = SkillTags.CUSTOM

    expose = ComponentType.Int
    value = 1

class OneMore(SkillComponent):
    nid = 'one_more'
    desc = "Refresh unit after hitting target."
    tag = SkillTags.MOVEMENT

    def end_combat(self, playback, unit, item, target, item2, mode):
        mark_playbacks = [p for p in playback if p.nid in ('mark_miss', 'mark_hit', 'mark_crit')]
        if target and \
            any(p.nid in ('mark_hit', 'mark_crit') and p.attacker is unit and (p.main_attacker is unit ) for p in mark_playbacks):
            action.do(action.Reset(unit))
            action.do(action.TriggerCharge(unit, self.skill))

class EventAfterCombatOnHitSkill(SkillComponent):
    nid = 'event_after_combat_on_hit_skill'
    desc = "The selected event plays at the end of combat so long as an attack in combat hit."
    tag = SkillTags.ADVANCED

    expose = ComponentType.Event

    _did_hit = False

    def on_hit(self, actions, playback, unit, item, target, item2, target_pos, mode, attack_info):
        self._did_hit = True
        self.target_pos = target_pos

    def end_combat(self, playback, unit, item, target, item2, mode):
        if self._did_hit and target:
            event_prefab = DB.events.get_from_nid(self.value)
            if event_prefab:
                local_args = {'target_pos': self.target_pos, 'item': item, 'item2': item2, 'mode': mode}
                game.events.trigger_specific_event(event_prefab.nid, unit, target, unit.position, local_args)
        self._did_hit = False

