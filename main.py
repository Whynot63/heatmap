import vk
import time
import re
import numpy as np
from PIL import Image

from settings import *
from tools import print_progress, sigmoid


session = vk.AuthSession(
    access_token = TOKEN,
)
vkapi = vk.API(session)

count_of_messages = vkapi.messages.getHistory(count=1, user_id=USER_ID)[0]
messages = []

print('Total count of messages: ', count_of_messages)

for i in range(0, count_of_messages, 200):
    print_progress(i, count_of_messages)
    messages += vkapi.messages.getHistory(offset=i, count=200, user_id=USER_ID)[1:]
    time.sleep(0.4)
print('')

m = [0] * count_of_messages
heatmap = np.zeros(count_of_messages)

for i, msg in enumerate(messages[::-1]):
    if 'attachment' in msg.keys():
        if 'sticker' in msg['attachment'].keys():
            m[i] = 5
    else:
        m[i] = len(re.findall(r'[\U0001f600-\U0001f650]', msg['body']))

m = [0] * SENSIBILITY + m + [0] * SENSIBILITY

for i in range(count_of_messages):
    for j in range(-SENSIBILITY, SENSIBILITY + 1):
        heatmap[i] += m[i + j] * (SENSIBILITY - abs(j)) // SENSIBILITY

heatmap *= np.pi / np.max(heatmap)

color = lambda value: [np.sin(value) * 255, 0, (1 - np.sin(value)) * 255]

heatmap = np.tile(list(map(color, heatmap)), (300, 1, 1)).astype(np.uint8)

img = Image.fromarray(heatmap).resize((600, 200), Image.BOX)
img.show()

img.save(USER_ID, '.png')
