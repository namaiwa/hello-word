import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient

# https://m.weibo.cn/api/container/getIndex?refer_flag[]=1001030201_&refer_flag[]=1001030201_&is_hot[]=1&is_hot[]=1&jumpfrom=weibocom&type=uid&value=5066284361&containerid=1076035066284361
url = 'https://m.weibo.cn/api/container/getIndex'
headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}
client = MongoClient()
db = client['weibo']
collection = db['weibo1']
max_page = 10


def get_page(page):
    params = {
        'refer_flag[]': '1001030201_',
        'refer_flag[]': '1001030201_',
        'is_hot[]': '1',
        'is_hot[]': '1',
        'jumpfrom': 'weibocom',
        'type': 'uid',
        'value': '5066284361',
        'containerid': '1076035066284361',
        'page': page
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            yield weibo


def save_to_mongo(result):
    if collection.insert(result):
        print('Saved to Mongo')


if __name__ == '__main__':
    for page in range(1, max_page + 1):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            print(result)
            save_to_mongo(result)