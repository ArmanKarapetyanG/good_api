from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
from lxml import etree
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from urllib.parse import urlparse
from string import whitespace
import validators


def universal_parser(soup, tagsz):
    charset = '0123456789,.'
    for i in tagsz:
        price = soup.find_all(i)
        if i == 'meta':
            for j in price:
                try:
                    all_atrs = list(j.attrs.keys())
                    attribute_keyval = []
                    for z in all_atrs:
                        if type(j[z]) == list:
                            attribute_keyval.append({
                                z: ','.join(j[z]),
                                'values_': float(j['content'])
                            })
                        else:
                            attribute_keyval.append({
                                z: j[z],
                                'values_': float(j['content'])
                            })
                    print(attribute_keyval)
                    for key in attribute_keyval:
                        if key['itemprop'].lower() == 'price':
                            return key['values_']
                except:
                    pass
        else:                
            for j in price:
                try:
                    all_atrs = list(j.attrs.keys())
                    attribute_keyval = []
                    for z in all_atrs:
                        if type(j[z]) == list:
                            attribute_keyval.append({
                                z: ','.join(j[z]),
                                'values_': float(''.join([m for m in j.text if m in charset]).replace(',', '.'))
                            })
                        else:
                            attribute_keyval.append({
                                z: j[z],
                                'values_': float(''.join([m for m in j.text if m in charset]).replace(',', '.'))
                            })
                    print(attribute_keyval)
                    for key in attribute_keyval:
                        for jkval in key.values():
                            if 'price' in jkval.lower():
                                return key['values_']
                except:
                    pass
    return 0




app = Flask(__name__)
api = Api(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def parse_it(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result



class ParseLink(Resource):
    def get(self):
        data = pd.read_csv('cleanest_max.csv')  # read CSV
        data = {'allowed hosts': list(data['host'])}
        return {'data': data}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url', required=True)
        args = parser.parse_args()
        url_to_parse = args['url']
        if validators.url(url_to_parse):
            try:
                html_page = requests.get(url_to_parse, headers=Headers(headers=True).generate(), timeout=10, verify=False).text
                soup = BeautifulSoup(html_page, 'lxml')
                price = universal_parser(soup, 'meta,span,p,a,i,b,brs,div,strong,h2,h1'.split(','))
                return {'price': price}, 200
            except:
                return {'error': 'Bad Getaway'}, 500
        else:
            return {'error': 'Bad URL'}, 400

    pass


api.add_resource(ParseLink, '/api/v1/parser')

if __name__ == '__main__':
    app.run(debug=True)
