from datetime import datetime


def error_log(e=None, r=None):
    now = datetime.now()
    error_time = now.strftime('%Y-%m-%d %H:%M:%S')

    if e is not None:
        msg = f'{error_time} -> {e.__class__.__name__}: {str(e)}\n'
        print(msg)
        with open('./error.log', 'a') as f:
            f.write(msg)

    if r is not None:
        msg = f'{error_time} -> {r.status_code}: {r.text}\n'
        print(msg)
        with open('./error.log', 'a') as f:
            f.write(msg)
