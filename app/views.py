from flask import request, Blueprint, redirect, jsonify
from .models import URL
from .utils import generate_short_url


# Create a blueprint
shortener = Blueprint('shortener', __name__)

    
@shortener.route('/shorten', methods=['POST'])
def shorten_url():
    
    # Extract the original URL from the request body
    original_url = request.json['url']
    # Check if the URL already exists in the database
    existing_short_url = URL.find_by_original_url(original_url)
    if existing_short_url:
        return jsonify({'short_url': existing_short_url})
    
    # If not, generate a new short URL
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
