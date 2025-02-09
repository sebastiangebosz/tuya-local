"""
Platform to control Tuya sirens.
"""
from homeassistant.components.siren import (
    SirenEntity,
    SirenEntityDescription,
    SirenEntityFeature,
)

from ..device import TuyaLocalDevice
from ..helpers.device_config import TuyaEntityConfig
from ..helpers.mixin import TuyaLocalEntity


class TuyaLocalSiren(TuyaLocalEntity, SirenEntity):
    """Representation of a Tuya siren"""

    def __init__(self, device: TuyaLocalDevice, config: TuyaEntityConfig):
        """
        Initialize the siren.
        Args:
           device (TuyaLocalDevice): The device API instance.
           config (TuyaEntityConfig): The config for this entity.
        """
        dps_map = self._init_begin(device, config)
        self._tone_dp = dps_map.get("tone", None)
        self._volume_dp = dps_map.get("volume_level", None)
        self._duration_dp = dps_map.get("duration", None)
        self._init_end(dps_map)
        # All control of features is through the turn_on service, so we need to
        # support that, even if the siren does not support direct control
        support = SirenEntityFeature.TURN_ON
        if self._tone_dp:
            support |= SirenEntityFeature.TONES
            self.entity_description = SirenEntityDescription
            self.entity_description.available_tones = self._tone_dp.values(device)

        if self._volume_dp:
            support |= SirenEntityFeature.VOLUME_SET
        if self._duration_dp:
            support |= SirenEntityFeature.DURATION
        self._attr_supported_features = support

    async def async_turn_on(self, **kwargs) -> None:
        tone = kwargs.get("tone", None)
        duration = kwargs.get("duration", None)
        volume = kwargs.get("volume", None)
        set_dps = {}

        if tone is not None and self._tone_dp:
            set_dps = {
                **set_dps,
                **self._tone_dp.get_values_to_set(self._device, tone),
            }
        if duration is not None and self._duration_dp:
            set_dps = {
                **set_dps,
                **self._duration_dp.get_values_to_set(self._device, duration),
            }

        if volume is not None and self._volume_dp:
            # Volume is a float, range 0.0-1.0 in Home Assistant
            # In tuya it is likely an integer or a fixed list of values.
            # For integer, expect scale and step to do the conversion,
            # for fixed values, we need to snap to closest value.
            if self._volume_dp.values(self._device) is not None:
                volume = min(
                    self._volume_dp.values(self._device), key=lambda x: abs(x - volume)
                )

            set_dps = {
                **set_dps,
                **self._volume_dp.get_values_to_set(self._device, volume),
            }

        await self._device.async_set_properties(set_dps)
