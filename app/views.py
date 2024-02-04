from flask import request, Blueprint, redirect, jsonify
from .models import URL
from .utils import generate_short_url
from datetime import datetime, timedelta


# Create a blueprint
shortener = Blueprint('shortener', __name__)

    
@shortener.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data['url']
    custom_short_url = data.get('custom_short_url')
    
    # Set defaults if not provided
    expiration_days = data.get('expiration_days', 30)  # Default to 30 days
    max_uses = data.get('max_uses', 1000)             # Default to 1000 uses

    # Calculate the expiration date
    expiration_date = datetime.now() + timedelta(days=expiration_days)

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

    # Insert the URL with the default or provided expiration date and max uses
    URL.insert_short_url(original_url, short_url, expiration_date, max_uses)
    return jsonify({'short_url': short_url})


@shortener.route('/<short_url>')
def redirect_to_original(short_url):
    if URL.is_expired_or_maxed_out(short_url):
        return "This URL has expired or reached its maximum number of uses", 410

    original_url = URL.get_original_url(short_url)
    if original_url:
        URL.increment_visit_count(short_url)
        return redirect(original_url)
    else:
        return "URL not found", 404

@shortener.route('/visits/<short_url>', methods=['GET'])
def get_visit_count(short_url):
    visit_count = URL.get_visit_count(short_url)
    if visit_count is not None:
        return jsonify({'short_url': short_url, 'visit_count': visit_count})
    else:
        return jsonify({'error': 'Short URL not found'}), 404
    

@shortener.route('/update/url', methods=['POST'])
def update_short_url():
    data = request.json
    original_short_url = data.get('original_short_url')
    new_short_url = data.get('new_short_url')

    # Validate input
    if not original_short_url or not new_short_url:
        return jsonify({'error': 'Missing original or new short URL'}), 400

    # Check if the new short URL is already taken
    if URL.get_original_url(new_short_url):
        return jsonify({'error': 'Please provide a unique short URL'}), 409

    # Proceed with the update if the new short URL is unique
    success = URL.update_short_url(original_short_url, new_short_url)
    if success:
        return jsonify({'message': 'Short URL updated successfully'})
    else:
        return jsonify({'error': 'Original short URL not found'}), 404

@shortener.route('/update/settings', methods=['POST'])
def update_url_settings():
    data = request.json
    short_url = data.get('short_url')
    expiration_days = data.get('expiration_days')
    max_uses = data.get('max_uses')

    if not short_url:
        return jsonify({'error': 'Short URL is required'}), 400

    # Convert expiration_days to an actual date, if provided
    expiration_date = None
    if expiration_days is not None:
        try:
            expiration_days = int(expiration_days)
            expiration_date = (datetime.now() + timedelta(days=expiration_days)).isoformat()
        except ValueError:
            return jsonify({'error': 'Invalid expiration days format'}), 400

    # Assuming update_url_details can handle None values to keep existing settings
    success = URL.update_url_details(short_url, expiration_date, max_uses)
    if success:
        return jsonify({'message': 'URL settings updated successfully'})
    else:
        return jsonify({'error': 'Failed to update URL settings or URL not found'}), 404

@shortener.route('/details/<short_url>', methods=['GET'])
def get_url_details(short_url):
    details = URL.get_url_details(short_url)
    if details:
        return jsonify(details)
    else:
        return jsonify({'error': 'Short URL not found'}), 404
