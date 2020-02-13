import json
import requests
from flask_babelex import _
from flask import current_app

# def translate(text, source_language, dest_language):
#     if 'MS_TRANSLATOR_KEY' not in current_app.config or not current_app.config['MS_TRANSLATOR_KEY']:
#         return _('Error: the translation service is not configured.')
#     auth = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY']}
#     print('https://api.microsofttranslator.com/v2/Ajax.svc/Translate?text={}&from={}'.format(text, source_language, dest_language))
#     r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc/Translate?text={}&from={}'.format(
#                      text, source_language, dest_language),headers=auth)
#     if r.status_code != 200:
#         return _('Error: the translation service failed.')
#     return json.loads(r.content.decode('utf-8-sig'))

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    # auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
    r = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&lang={}-{}&text={}'.format(
        current_app.config['MS_TRANSLATOR_KEY'], source_language, dest_language, text))
    if r.status_code != 200:
        # return r.status_code
        return _('Error: the translation service failed.')
    resp = json.loads(r.content.decode('utf-8-sig'))
    return resp.get('text')[0]