from flask import Flask
from os import urandom
from ffield import FField


ffield = FField(11953696440786470837)
app = Flask(__name__)


@app.route('/')
def index():
    id = int(urandom(4).encode('hex'), 16)
    secret = ffield.randomElement()
    print 'INFO: id=%d, secret=%s' % (id, secret)
    shares = create_shares(secret)
    return repr([id, shares])


def create_shares(secret):
    # Simplified Blakley's secret sharing (https://en.wikipedia.org/wiki/Secret_sharing#Blakley's_scheme)
    point = [
        secret,
        secret.ffield.randomElement(),
        secret.ffield.randomElement()
    ]

    shares = []
    set_a = set()
    while len(shares) < 3:
        a = secret.ffield.randomElement()
        if not a.value in set_a:
            set_a.add(a.value)

            b = ((point[2] * a + point[1]) * a + point[0]) * a
            shares.append([a, b])

    return shares


if __name__ == '__main__':
    app.run(port=3000)
