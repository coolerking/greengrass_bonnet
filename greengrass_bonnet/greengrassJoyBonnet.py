# -*- coding: utf-8 -*-
"""
AWS Greengrass 経由で AWS IoT Coreへ操作情報を
Publishする。
"""
import logging
import platform
import sys
from threading import Timer

import greengrasssdk

# 標準出力にログを書き出す
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Greengrass Core SDK クライアントを生成
client = greengrasssdk.client("iot-data")

# Greengrass Coreから送信プラットフォーム情報を取得する
my_platform = platform.platform()

# pigpio オブジェクトを取得する
try:
    import pigpio
except ImportError:
    exit('This code need to import pigpio library.')
pgio = pigpio.pi()

# JoyBonnet インスタンスを生成する
from parts.adafruit import JoyBonnet
joy_bonnet = JoyBonnet(pgio=pgio, debug=True)

"""
Greengrass Core にデプロイされると、このコードは長寿命のLambda関数として
すぐに実行されます。
コードは、以下の無限whileループに入ります。
Lambdaコンソールで「テスト」を実行する場合、3秒の実行タイムアウトに達すると、
このテストは失敗します。 この関数は結果を返さないため、これは予期されています。
"""

# トピック名
TOPIC = 'real/agent/loader/joystick/json'
# キューポリシ
QUEUE_FULL_POLICY = 'AllOrException'
# タイマー間隔 (Sec)
SLEEP_TIME = 1

def greengrass_joy_bonnet_run():
    """
    JoyBonnetの操作情報を更新し、JSONデータとしてPublishする。
    その後SLEEP_TIMEに指定された間隔をあけ、
    再度自分自身を非同期実行する（無限ループ）。
    本モジュールがロードされると実行される。
    引数：
        なし
    戻り値：
        なし
    """
    try:
        joy_bonnet.update_values()
        client.publish(
            topic = TOPIC,
            queueFullPolicy = QUEUE_FULL_POLICY,
            payload = joy_bonnet.get_payload(),
        )
    except Exception as e:
        logger.error("Failed to publish message: " + repr(e))

    # 1秒後に再び実行されるように非同期でスケジュールする
    Timer(SLEEP_TIME, greengrass_joy_bonnet_run).start()


# モジュールがロードされた時点で実行する
greengrass_joy_bonnet_run()

def function_handler(event, context):
    """
    ダミーハンドラ。呼び出されることはない。
    引数：
        event       イベント
        context     コンテクスト
    戻り値：
        なし
    """
    return
