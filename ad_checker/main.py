import cv2 as cv
import requests


def find_channel(text, key):
    lines = text.split('\n')

    for line in lines:
        if key in line.lower():
            return line.strip()

    raise Exception(f'Unable to find {key}')


def find_m3u(url):
    response = requests.get(url)

    if response.status_code == 200:
        lines = response.text.split('\n')

        for line in lines:
            if 'm3u' in line:
                return line.strip()

        raise Exception(f'Unable to find m3u in response text:\n{response.text}')

    else:
        raise Exception(f'Request failed with code {response.status_code}') 


def find_ts(url):
    response = requests.get(url)

    if response.status_code == 200:
        lines = response.text.split('\n')

        ts_lines = filter(lambda x: 'ts' in x, lines)

        if not ts_lines:
            raise Exception(f'Unable to find m3u in response text:\n{response.text}')

        most_recent_ts = sorted(ts_lines)[-1]

        return most_recent_ts.strip()

    else:
        raise Exception(f'Request failed with code {response.status_code}') 


# vc = cv2.VideoCapture('https://iptv-org.github.io/iptv/index.m3u')

response = requests.get('https://iptv-org.github.io/iptv/index.m3u')


if response.status_code == 200:
    url = find_channel(response.text, 'fox_sports_1')
    base_url = '/'.join(url.split('/')[:-1])
    print(url)

    m3u = find_m3u(url)
    m3u_url = base_url + '/' + m3u
    print(m3u)

    ts = find_ts(m3u_url)
    ts_url = base_url + '/' + ts
    print(ts_url)

    # raw = requests.get(ts_url).text
    vc = cv.VideoCapture(ts_url)

    ret, frame = vc.read()

    cv.imshow('frame', frame)
    cv.waitKey()


else:
    print(response)

