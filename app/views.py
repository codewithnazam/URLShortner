from flask import request, Blueprint, redirect, jsonify
from .models import URL
from .utils import generate_short_url


# Create a blueprint
shortener = Blueprint('shortener', __name__)

    
@shortener.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data['url']
    custom_short_url = data.get('custom_short_url')

    # Check if the original URL already exists in the database
    existing_short_url = URL.find_by_original_url(original_url)
    if existing_short_url:
        if custom_short_url and existing_short_url != custom_short_url:
            return jsonify({'message': 'We found your custom URL with this original URL', 'short_url': existing_short_url})
        return jsonify({'short_url': existing_short_url})

    if custom_short_url:
        # Check if the custom short URL is unique
        if URL.get_original_url(custom_short_url):
            return jsonify({'error': 'Custom short URL already exists'}), 409
        short_url = custom_short_url
    else:
        # Generate a unique random short URL
        short_url = generate_short_url()
        while URL.get_original_url(short_url):
            short_url = generate_short_url()

    URL.insert_short_url(original_url, short_url)
    return jsonify({'short_url': short_url})


@shortener.route('/<short_url>')
def redirect_to_original(short_url):
    original_url = URL.get_original_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return "URL not found", 404
