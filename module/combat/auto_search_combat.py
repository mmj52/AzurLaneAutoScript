from module.combat.assets import *
from module.combat.combat import Combat
from module.exception import CampaignEnd
from module.logger import logger
from module.map.assets import *


class AutoSearchCombat(Combat):
    fleets_reversed: bool  # Define in MapOperation

    def get_fleet_current_index(self):
        """
        Returns:
            int: 1 or 2

        Pages:
            in: map
        """
        if self.appear(FLEET_NUM_1, offset=(20, 20)):
            return 1
        elif self.appear(FLEET_NUM_2, offset=(20, 20)):
            return 2
        else:
            logger.warning('Unknown fleet current index, use 1 by default')
            return 1

    def auto_search_moving(self, skip_first_screenshot=True):
        """
        Pages:
            in: map
            out: is_combat_loading()
        """
        logger.info('Auto search moving')
        self.device.stuck_record_clear()
        fleet_log = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.is_auto_search_running():
                index = self.get_fleet_current_index()
                fleet_current_index = 3 - index if self.fleets_reversed else index
                if not fleet_log:
                    logger.info(f'Fleet: {index}, fleet_current_index: {fleet_current_index}')
                    fleet_log = True
                elif fleet_current_index != self.fleet_current_index:
                    logger.info(f'Fleet: {index}, fleet_current_index: {fleet_current_index}')
                self.fleet_current_index = fleet_current_index
            if self.handle_retirement():
                continue
            if self.handle_auto_search_map_option():
                continue
            if self.handle_combat_low_emotion():
                continue

            # End
            if self.is_combat_loading():
                break
            if self.is_in_auto_search_menu():
                raise CampaignEnd
            if self.is_in_stage():
                # Sometimes game is bugged, and auto search menu is not shown
                raise CampaignEnd

    def auto_search_combat_execute(self, emotion_reduce, fleet_index):
        """
        Args:
            emotion_reduce (bool):
            fleet_index (int):

        Pages:
            in: is_combat_loading()
            out: combat status
        """
        logger.info('Auto Search combat execute')
        self.device.screenshot_interval_set(self.config.COMBAT_SCREENSHOT_INTERVAL)
        if emotion_reduce:
            self.emotion.reduce(fleet_index)

        while 1:
            self.device.screenshot()

            # End
            if self.appear(BATTLE_STATUS_S) or self.appear(BATTLE_STATUS_A) or self.appear(BATTLE_STATUS_B) \
                    or self.appear(EXP_INFO_S) or self.appear(EXP_INFO_A) or self.appear(EXP_INFO_B) \
                    or self.is_auto_search_running():
                self.device.screenshot_interval_set(0)
                break

    def auto_search_combat_status(self, skip_first_screenshot=True):
        """
        Pages:
            in: any
            out: is_auto_search_running()
        """
        logger.info('Auto Search combat status')
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.is_auto_search_running():
                break
            if self.is_in_auto_search_menu():
                raise CampaignEnd
            if self.is_in_stage():
                # Sometimes game is bugged, and auto search menu is not shown
                raise CampaignEnd

    def auto_search_combat(self, emotion_reduce=None, fleet_index=1):
        """
        Execute a combat.

        Note that fleet index == 1 is mob fleet, 2 is boss fleet.
        It's not the fleet index in fleet preparation or auto search setting.
        """
        emotion_reduce = emotion_reduce if emotion_reduce is not None else self.config.ENABLE_EMOTION_REDUCE

        self.device.stuck_record_clear()
        self.auto_search_combat_execute(emotion_reduce=emotion_reduce, fleet_index=fleet_index)
        self.auto_search_combat_status()

        logger.info('Combat end.')
