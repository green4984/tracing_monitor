from __future__ import unicode_literals
from flask import Flask, render_template
import redis
import simplejson as json
from datetime import datetime

app = Flask(__name__)
rd = redis.Redis.from_url('redis://localhost:6380/3')


@app.route('/')
def track_log_display():
    tracking_log = []
    for key in rd.keys():
        items = rd.lrange(key, 0, -1)
        tmp_queue = []
        total_time = 0
        percent = []
        prefix_width = 0
        for item in items:
            data = json.loads(item)
            microsec = data['bgn_timestamp']
            if data['seq'] == 0:
                total_time = data['took']
            else:
                status = 'warning' if data['exception_message'] else 'success'
                curr = int(data['took'] * 100.0 / total_time)
                percent.append([status, prefix_width, curr])
                prefix_width += curr
            data['bgn_timestamp'] = datetime.fromtimestamp(microsec/1000).strftime("%Y-%m-%d %H:%M:%S.") + str(microsec)[-3:]
            tmp_queue.append(data)
        if tmp_queue:
            tmp_queue[0]['took_percent_list'] = percent
        tracking_log.append(tmp_queue)
    return render_template('index.html', tracking_log=tracking_log)


if __name__ == '__main__':
    app.run(debug=True)
