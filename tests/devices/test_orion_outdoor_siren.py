from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.siren import SirenEntityFeature
from homeassistant.const import PERCENTAGE

from ..const import ORION_SIREN_PAYLOAD
from ..helpers import assert_device_properties_set
from ..mixins.binary_sensor import MultiBinarySensorTests
from ..mixins.sensor import BasicSensorTests
from .base_device_tests import TuyaDeviceTestCase

TONE_DP = "1"
VOLUME_DP = "5"
CHARGING_DP = "6"
DURATION_DP = "7"
BATTERY_DP = "15"
TAMPER_DP = "20"


class TestOrionSiren(MultiBinarySensorTests, BasicSensorTests, TuyaDeviceTestCase):
    __test__ = True

    def setUp(self):
        self.setUpForConfig("orion_outdoor_siren.yaml", ORION_SIREN_PAYLOAD)
        self.subject = self.entities.get("siren")
        self.setUpMultiBinarySensors(
            [
                {
                    "dps": CHARGING_DP,
                    "name": "binary_sensor_charging",
                    "device_class": BinarySensorDeviceClass.BATTERY_CHARGING,
                },
                {
                    "dps": TAMPER_DP,
                    "name": "binary_sensor_tamper_detect",
                    "device_class": BinarySensorDeviceClass.TAMPER,
                },
            ]
        )
        self.setUpBasicSensor(
            BATTERY_DP,
            self.entities.get("sensor_battery"),
            unit=PERCENTAGE,
            device_class=SensorDeviceClass.BATTERY,
        )
        self.mark_secondary(
            ["sensor_battery", "binary_sensor_charging", "binary_sensor_tamper_detect"]
        )

    def test_supported_features(self):
        """Test the supported features of the siren"""
        self.assertEqual(
            self.subject.supported_features,
            SirenEntityFeature.TURN_ON
            | SirenEntityFeature.TONES
            | SirenEntityFeature.DURATION
            | SirenEntityFeature.VOLUME_SET,
        )

    def test_available_tones(self):
        """Test the available tones from the siren"""
        self.assertCountEqual(
            self.subject.available_tones,
            [
                "sound",
                "light",
                "sound+light",
                "normal",
            ],
        )

    async def test_set_to_sound(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {TONE_DP: "alarm_sound"}
        ):
            await self.subject.async_turn_on(tone="sound")

    async def test_set_to_light(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {TONE_DP: "alarm_light"}
        ):
            await self.subject.async_turn_on(tone="light")

    async def test_set_to_sound_light(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {TONE_DP: "alarm_sound_light"}
        ):
            await self.subject.async_turn_on(tone="sound+light")

    async def test_set_to_normal(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {TONE_DP: "normal"}
        ):
            await self.subject.async_turn_on(tone="normal")

    async def test_set_volume_low(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {VOLUME_DP: "low"}
        ):
            await self.subject.async_turn_on(volume=0.3)

    async def test_set_volume_mid(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {VOLUME_DP: "middle"}
        ):
            await self.subject.async_turn_on(volume=0.7)

    async def test_set_volume_high(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {VOLUME_DP: "high"}
        ):
            await self.subject.async_turn_on(volume=1.0)

    async def test_set_volume_mute(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device, {VOLUME_DP: "mute"}
        ):
            await self.subject.async_turn_on(volume=0.0)

    async def test_set_duration(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(self.subject._device, {DURATION_DP: 5}):
            await self.subject.async_turn_on(duration=5)

    async def test_set_multi(self):
        """Test turning on the siren with various parameters"""
        async with assert_device_properties_set(
            self.subject._device,
            {TONE_DP: "alarm_sound", DURATION_DP: 4, VOLUME_DP: "high"},
        ):
            await self.subject.async_turn_on(tone="sound", duration=4, volume=0.9)

    def test_extra_attributes(self):
        """Test reading the extra attributes from the siren"""
        self.dps[TONE_DP] = "alarm_light"
        self.dps[VOLUME_DP] = "middle"
        self.dps[DURATION_DP] = 3
        self.assertDictEqual(
            self.subject.extra_state_attributes,
            {
                "tone": "light",
                "volume_level": 0.67,
                "duration": 3,
            },
        )
