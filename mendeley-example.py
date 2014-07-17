from urllib import urlencode

from flask import Flask, redirect, render_template, request, session
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
import yaml


with open('config.yml') as f:
    config = yaml.load(f)

REDIRECT_URI = 'http://localhost:5000/oauth'

AUTHORIZE_URL = 'https://api.mendeley.com/oauth/authorize'
TOKEN_URL = 'https://api.mendeley.com/oauth/token'

app = Flask(__name__)
app.debug = True
app.secret_key = config['clientSecret']


@app.route('/')
def home():
    if 'token' in session:
        return redirect('/listDocuments')

    oauth = OAuth2Session(client_id=config['clientId'], redirect_uri=REDIRECT_URI, scope=['all'])
    (login_url, state) = oauth.authorization_url(AUTHORIZE_URL)

    return render_template('home.html', login_url=login_url)


@app.route('/oauth')
def auth_return():
    if 'error_description' in request.args:
        return render_template('error.html', error_text=request.args.get('error_description'))

    code = request.args.get('code')
    oauth = OAuth2Session(client_id=config['clientId'], redirect_uri=REDIRECT_URI, scope=['all'])

    try:
        session['token'] = oauth.fetch_token(TOKEN_URL, code=code, client_secret=config['clientSecret'])
        return redirect('/listDocuments')
    except OAuth2Error as e:
        error_text = 'Error getting access token (status %s, text %s)' % (e.status_code, e.description)
        return render_template('error.html', error_text=error_text)
    except ValueError:
        error_text = 'Error parsing token response.  Are your client ID/secret correct?'
        return render_template('error.html', error_text=error_text)


@app.route('/listDocuments')
def list_documents():
    if 'token' not in session:
        return redirect('/')

    oauth = OAuth2Session(client_id=config['clientId'], token=session['token'])
    docs_response = oauth.get('https://api.mendeley.com/documents')

    if not docs_response.ok:
        return render_template('error.html', error_text='Error getting documents')

    profile_response = oauth.get('https://api.mendeley.com/profiles/me')

    if not profile_response.ok:
        return render_template('error.html', error_text='Error getting profile')

    name = profile_response.json()['display_name']

    return render_template('library.html', name=name, docs=docs_response.json())


@app.route('/document')
def get_document():
    if 'token' not in session:
        return redirect('/')

    document_id = request.args.get('document_id')

    oauth = OAuth2Session(client_id=config['clientId'], token=session['token'])
    doc_response = oauth.get('https://api.mendeley.com/documents/%s' % document_id)

    if not doc_response.ok:
        return render_template('error.html', error_text='Error getting document')

    return render_template('metadata.html', doc=doc_response.json())


@app.route('/metadataLookup')
def metadata_lookup():
    if 'token' not in session:
        return redirect('/')

    doi = request.args.get('doi')

    oauth = OAuth2Session(client_id=config['clientId'], token=session['token'])
    metadata_response = oauth.get('https://api.mendeley.com/metadata?%s' % urlencode({'doi': doi}))

    if metadata_response.ok:
        catalog_id = metadata_response.json()['catalog_id']
        response = oauth.get('https://api.mendeley.com/catalog/%s?view=all' % catalog_id)

        return render_template('metadata.html', doc=response.json())
    else:
        return render_template('error.html', error_text='Could not find metadata for DOI %s' % doi)


@app.route('/annotations')
def annotations():
    if 'token' not in session:
        return redirect('/')

    document_id = request.args.get('document_id')

    oauth = OAuth2Session(client_id=config['clientId'], token=session['token'])
    annotations_response = oauth.get('https://api.mendeley.com/annotations?document_id=%s' % document_id)

    if annotations_response.ok:
        annotation_texts = []
        for annotation in annotations_response.json():
            if 'text' in annotation:
                annotation_texts.append(annotation['text'])

        return render_template('annotations.html', annotation_texts=annotation_texts)
    else:
        return render_template('error.html', error_text='Error getting annotations')


@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()
