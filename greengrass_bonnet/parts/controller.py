# -*- coding: utf-8 -*-
from .adafruit import JoyBonnet

class JoyBonnetController:
    def __init__(self, throttle_dir,
                throttle_scale,
                steering_scale,
                auto_record_on_throttle,
                pgio=None, i2c_bus=1, i2c_address=0x48, debug=False):
        """
        JoyBonnetクラスを生成しインスタンス変数へ格納する。
        引数：
            throttle_dir            スロットル向き(反転させたい場合は-1.0を指定)
            throttle_scale          スロットル値の範囲
            steering_scale          ステアリング値の範囲
            auto_record_on_throttle スロットルオン時の自動記録（真：記録する、偽：記録しない）
            pgio                    pigpio.piオブジェクト
            i2c_bus                 JoyBonnetが接続されているI2Cバス
            i2c_addess              JoyBonnetが接続されているI2Cスレーブアドレス
            debug                   デバッグフラグ
        """
        self.throttle_dir = throttle_dir
        self.steering_scale = steering_scale
        self.auto_recording_on_throttle = auto_record_on_throttle
        self.joy = JoyBonnet(pgio, i2c_bus, i2c_address, debug)
        self.debug = debug
        self.drive_mode = ['user', 'local_angle', 'local']
        self.drive_mode_index = 0
        self.recording = False
        
    
    def update(self):
        """
        JoyBonnetの無限ループを開始する。
        引数：
            なし
        戻り値：
            なし
        """
        self.joy.update()



        # なにか変だ、全部向こうでやったほうがいいかも..
        # トグル系は、前回の変化がわからない？！
    
    def run_threaded(self):
        """
        最新のジョイスティック入力値を返却する。
        引数：
            なし
        戻り値：
            なし
        """
        if self.joy.dpad_up == 1:
            if self.joy.dpad_down == 0:
                throttle = 1.0
            else:
                throttle = 0.0
        else:
            if self.joy.dpad_down == 1:
                throttle = 0.0
            else:
                throttle = -1.0
        
        if self.joy.dpad_left == 1:
            if self.joy.dpad_right == 0:
                angle = 1.0
            else:
                throttle = 0.0
        else:
            if self.joy.dpad_right == 1:
                throttle = 0.0
            else:
                throttle = -1.0
        
        if self.joy.select == 1:
            mode = self.toggle_drive_mode()
        else:
            mode = self.get_drive_mode()
        
        if self.joy.start == 1:
            recording = self.toggle_recording()
        else:
            recording = self.get_recording()
        
        return angle, throttle, mode, recording

    def shutdown(self):
        self.joy.shutdown()

    def get_drive_mode(self):
        return self.drive_mode[self.drive_mode_index % len(self.drive_mode)]
    
    def toggle_drive_mode(self):
        self.drive_mode_index = (self.drive_mode_index + 1) % len(self.drive_mode)
        return self.get_drive_mode()
    
    def get_recording(self):
        return self.recording
    
    def toggle_recording(self):
        self.recording = not self.recording
        return self.get_recording()


def get_js_controller(cfg, pgio=None):
    try:
        from donkeycar.parts.controller import get_js_controller as get_controller
        return get_controller(cfg)
    except:
        if cfg.CONTROLLER_TYPE == "joybonnet":
            cont_class = JoyBonnetController
            ctr = cont_class(
                throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
                throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
                steering_scale=cfg.JOYSTICK_STEERING_SCALE,
                auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE)
            ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
            return ctr
        else:
            raisek
