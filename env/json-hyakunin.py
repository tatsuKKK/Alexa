# coding:utf-8

from __future__ import print_function #ビルドイン関数

import os.path, random
import json

savename = "hyakunin.json"

# JSONファイルを解析
data = json.load(open(savename, "r", encoding="utf-8"))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        # ここのtextがAlexaによって音声に変換されてEchoに届きます
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        # Alexaアプリを使用した場合に画面に返ってくる「Card」の内容が入ります
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        # response.outputSpeechを出力した後、一定時間何も話さなかった場合に
        # このreprompt.outputSpeech.textが音声変換されてEchoに届きます。
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "ようこそ"
    speech_output = "これは百人一首の上の句をランダムに読み上げるスキルです "
    reprompt_text = "上の句読んでと言ってください "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "スキルを終了します"
    speech_output = "ありがとう"
    # セッションが終了する必要がある場合にはここがtrueになります。
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def set_card_in_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    res = random.choice(data)
    kaminoku = res['kami']
    shimonoku = res['simo']
    speech_output = kaminoku
    reprompt_text = shimonoku

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # この部分でIntentで設定した名前で処理を分岐することができる
    if intent_name == "setCard":
        return set_card_in_session(intent, session)
    # ヘルプ（デフォルト）への返答
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    # キャンセル（デフォルト）への返答
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    # Lambdaに渡されるJSONメッセージは全て event に格納されています。
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    # // アプリ起動時の返答
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    # IntentRequestへの返答
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])