import os
from urllib import urlencode

from flask import Flask, redirect, render_template, request
from rauth.service import OAuth2Service

app = Flask(__name__)
app.debug = True

service = OAuth2Service(name='mendeley',
                        authorize_url='https://mix.mendeley.com/oauth/authorize',
                        access_token_url='https://mix.mendeley.com/oauth/token',
                        client_id=os.environ['MENDELEY_CLIENT_ID'],
                        client_secret=os.environ['MENDELEY_CLIENT_SECRET'])

REDIRECT_URI = 'http://localhost:5000/oauth'


@app.route('/')
def home():
    login_url = service.get_authorize_url(
        redirect_uri=REDIRECT_URI,
        scope='all',
        response_type='code')

    return render_template('home.html', login_url=login_url)


@app.route('/oauth')
def auth_return():
    if 'error_description' in request.args:
        return render_template('error.html', error_text=request.args.get('error_description'))

    code = request.args.get('code')

    data = dict(code=code,
                redirect_uri=REDIRECT_URI,
                grant_type='authorization_code')

    auth_rsp = service.get_raw_access_token('POST', data=data)

    if auth_rsp.ok:
        access_token = auth_rsp.json()['access_token']
        return redirect("/listDocuments?access_token=%s" % access_token)
    else:
        try:
            error_text = auth_rsp.json()['error_description']
        except ValueError:
            error_text = "Error getting access token (status %s, text %s)" % (auth_rsp.status_code, auth_rsp.text)

        return render_template('error.html', error_text=error_text)


@app.route('/listDocuments')
def list_documents():
    access_token = request.args.get('access_token')
    session = service.get_session(token=access_token)

    docs_response = session.get('https://mix.mendeley.com/documents')

    if not docs_response.ok:
        return render_template('error.html', error_text='Error getting documents')

    profile_response = session.get(
        'https://mix.mendeley.com/profiles/me')

    if not profile_response.ok:
        return render_template('error.html', error_text='Error getting profile')

    name = profile_response.json()['display_name']

    return render_template('library.html', name=name, docs=docs_response.json(), access_token=access_token)


@app.route('/document')
def get_document():
    access_token = request.args.get('access_token')
    document_id = request.args.get('document_id')
    session = service.get_session(token=access_token)

    doc_response = session.get('https://mix.mendeley.com/documents/%s' % document_id)

    if not doc_response.ok:
        return render_template('error.html', error_text='Error getting document')

    return render_template('metadata.html', doc=doc_response.json())


@app.route('/metadataLookup')
def metadata_lookup():
    access_token = request.args.get('access_token')
    doi = request.args.get('doi')
    session = service.get_session(token=access_token)

    metadata_response = session.get('https://mix.mendeley.com/metadata?%s' % urlencode({'doi': doi}))

    if metadata_response.ok:
        catalog_id = metadata_response.json()['catalog_id']
        response = session.get('https://mix.mendeley.com/catalog/%s?view=all' % catalog_id)

        return render_template('metadata.html', doc=response.json())
    else:
        return render_template('error.html', error_text="Could not find metadata for DOI %s" % doi)


@app.route('/annotations')
def annotations():
    access_token = request.args.get('access_token')
    document_id = request.args.get('document_id')
    session = service.get_session(token=access_token)

    annotations_response = session.get('https://mix.mendeley.com/annotations?document_id=%s' % document_id)

    if annotations_response.ok:
        annotation_texts = []
        for annotation in annotations_response.json():
            if annotation.has_key('text'):
                annotation_texts.append(annotation['text'])

        return render_template('annotations.html', annotation_texts=annotation_texts)
    else:
        return render_template('error.html', error_text='Error getting annotations')


if __name__ == '__main__':
    app.run()



