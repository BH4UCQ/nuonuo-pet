#!/usr/bin/env python3
"""nuonuo-pet 固件状态机自检（宿主机版）。

用于验证 firmware/esp32/include/state_machine.h 与 PetApp 的核心转移：
- Booting -> Connecting
- Connecting -> Binding / Ready
- Binding -> Ready
- Ready -> LowPower -> Sleeping
- mood/energy/hunger 的基础更新
"""
from __future__ import annotations

from dataclasses import dataclass


class DeviceState:
    Booting = "Booting"
    Connecting = "Connecting"
    Binding = "Binding"
    Ready = "Ready"
    Sleeping = "Sleeping"
    LowPower = "LowPower"
    Error = "Error"


class PetMood:
    Neutral = "Neutral"
    Happy = "Happy"
    Curious = "Curious"
    Sleepy = "Sleepy"
    Hungry = "Hungry"
    Lonely = "Lonely"
    Sad = "Sad"
    Angry = "Angry"


class PetActivity:
    Idle = "Idle"
    Listening = "Listening"
    Talking = "Talking"
    Playing = "Playing"
    Eating = "Eating"
    Sleeping = "Sleeping"
    Recovering = "Recovering"


@dataclass
class PetState:
    device_state: str = DeviceState.Booting
    mood: str = PetMood.Neutral
    activity: str = PetActivity.Idle
    network_ready: bool = False
    is_bound: bool = False
    bind_retry_count: int = 0
    energy: int = 100
    happiness: int = 50
    hunger: int = 20
    last_tick_ms: int = 0


class PetApp:
    def __init__(self) -> None:
        self.state_ = PetState()

    def begin(self) -> None:
        self.state_.device_state = DeviceState.Connecting
        self.state_.last_tick_ms = 0

    def update(self, now_ms: int) -> None:
        if now_ms - self.state_.last_tick_ms >= 1000:
            if self.state_.energy > 0:
                self.state_.energy -= 1
            self.state_.hunger = min(100, self.state_.hunger + 1)

        if self.state_.hunger > 70:
            self.state_.mood = PetMood.Hungry
        elif self.state_.energy < 20:
            self.state_.mood = PetMood.Sleepy
        elif self.state_.is_bound:
            self.state_.mood = PetMood.Happy
        else:
            self.state_.mood = PetMood.Curious

        if self.state_.device_state == DeviceState.Connecting and self.state_.network_ready:
            self.state_.device_state = DeviceState.Ready if self.state_.is_bound else DeviceState.Binding

        if self.state_.device_state == DeviceState.Binding and self.state_.is_bound:
            self.state_.device_state = DeviceState.Ready

        if self.state_.device_state == DeviceState.Ready and self.state_.energy < 10:
            self.state_.device_state = DeviceState.LowPower
            self.state_.activity = PetActivity.Sleeping

        if self.state_.energy == 0:
            self.state_.device_state = DeviceState.Sleeping
            self.state_.activity = PetActivity.Sleeping

        self.state_.last_tick_ms = now_ms

    def set_bound(self, bound: bool) -> None:
        self.state_.is_bound = bound
        if bound and self.state_.device_state == DeviceState.Binding:
            self.state_.device_state = DeviceState.Ready

    def set_network_ready(self, ready: bool) -> None:
        self.state_.network_ready = ready
        if ready and self.state_.device_state == DeviceState.Connecting:
            self.state_.device_state = DeviceState.Ready if self.state_.is_bound else DeviceState.Binding


def assert_eq(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    app = PetApp()
    app.begin()
    assert_eq(app.state_.device_state, DeviceState.Connecting, "boot->connecting")

    app.set_network_ready(True)
    assert_eq(app.state_.device_state, DeviceState.Binding, "network ready -> binding")

    app.set_bound(True)
    assert_eq(app.state_.device_state, DeviceState.Ready, "bound -> ready")

    app.state_.energy = 9
    app.update(1000)
    assert_eq(app.state_.device_state, DeviceState.LowPower, "low energy -> lowpower")

    app.state_.energy = 0
    app.update(2000)
    assert_eq(app.state_.device_state, DeviceState.Sleeping, "zero energy -> sleeping")
    assert_eq(app.state_.activity, PetActivity.Sleeping, "sleeping activity")

    print("OK: firmware state machine self-test passed")


if __name__ == "__main__":
    main()
