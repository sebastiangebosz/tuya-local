from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)

from ..const import POOLEX_QLINE_HEATPUMP_PAYLOAD
from ..helpers import assert_device_properties_set
from ..mixins.binary_sensor import BasicBinarySensorTests
from ..mixins.climate import TargetTemperatureTests
from .base_device_tests import TuyaDeviceTestCase

HVACMODE_DPS = "1"
MODE_DPS = "2"
TEMPERATURE_DPS = "4"
CURRENTTEMP_DPS = "16"
ERROR_DPS = "15"


class TestPoolexSilverlineHeatpump(
    BasicBinarySensorTests,
    TargetTemperatureTests,
    TuyaDeviceTestCase,
):
    __test__ = True

    def setUp(self):
        self.setUpForConfig("poolex_qline_heatpump.yaml", POOLEX_QLINE_HEATPUMP_PAYLOAD)
        self.subject = self.entities.get("climate")
        self.setUpTargetTemperature(
            TEMPERATURE_DPS,
            self.subject,
            min=8,
            max=40,
        )
        self.setUpBasicBinarySensor(
            ERROR_DPS,
            self.entities.get("binary_sensor_water_flow"),
            device_class=BinarySensorDeviceClass.PROBLEM,
            testdata=(1, 0),
        )
        self.mark_secondary(["binary_sensor_water_flow"])

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            ClimateEntityFeature.TARGET_TEMPERATURE,
        )

    def test_icon(self):
        self.dps[HVACMODE_DPS] = True
        self.dps[MODE_DPS] = "heating"
        self.assertEqual(self.subject.icon, "mdi:hot-tub")
        self.dps[MODE_DPS] = "cold"
        self.assertEqual(self.subject.icon, "mdi:snowflake")
        self.dps[MODE_DPS] = "mute"
        self.assertEqual(self.subject.icon, "mdi:hot-tub")
        self.dps[ERROR_DPS] = 1
        self.assertEqual(self.subject.icon, "mdi:water-pump-off")
        self.dps[HVACMODE_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:hvac-off")

    def test_temperature_unit_returns_device_temperature_unit(self):
        self.assertEqual(
            self.subject.temperature_unit, self.subject._device.temperature_unit
        )

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DPS] = 25
        self.assertEqual(self.subject.current_temperature, 25)

    def test_hvac_mode(self):
        self.dps[HVACMODE_DPS] = True
        self.dps[MODE_DPS] = "heating"
        self.assertEqual(self.subject.hvac_mode, HVACMode.HEAT)

        self.dps[MODE_DPS] = "cold"
        self.assertEqual(self.subject.hvac_mode, HVACMode.COOL)

        self.dps[MODE_DPS] = "mute"
        self.assertEqual(self.subject.hvac_mode, HVACMode.FAN_ONLY)

        self.dps[HVACMODE_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVACMode.OFF)

    def test_hvac_modes(self):
        self.assertCountEqual(
            self.subject.hvac_modes,
            [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY],
        )

    async def test_hvac_mode_heat(self):
        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: True, MODE_DPS: "heating"}
        ):
            await self.subject.async_set_hvac_mode(HVACMode.HEAT)

    async def test_hvac_mode_cool(self):
        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: True, MODE_DPS: "cold"}
        ):
            await self.subject.async_set_hvac_mode(HVACMode.COOL)

    async def test_hvac_mode_mute(self):
        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: True, MODE_DPS: "mute"}
        ):
            await self.subject.async_set_hvac_mode(HVACMode.FAN_ONLY)

    async def test_turn_off(self):
        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: False}
        ):
            await self.subject.async_set_hvac_mode(HVACMode.OFF)

    def test_error_state(self):
        self.dps[ERROR_DPS] = 0
        self.assertEqual(self.subject.extra_state_attributes, {"error": "OK"})

        self.dps[ERROR_DPS] = 1
        self.assertEqual(
            self.subject.extra_state_attributes,
            {"error": "Water Flow Protection"},
        )
        self.dps[ERROR_DPS] = 2
        self.assertEqual(
            self.subject.extra_state_attributes,
            {"error": 2},
        )
