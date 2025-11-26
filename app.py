from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_price', methods=['POST'])
def get_price():
    data = request.get_json()
    # Support both single 'fsn' and multiple 'fsns' keys for flexibility
    fsns_input = data.get('fsns') or data.get('fsn')

    if not fsns_input:
        return jsonify({'error': 'No FSN provided.'}), 400

    # Split by comma and clean up
    fsn_list = [f.strip() for f in fsns_input.split(',') if f.strip()]
    
    if not fsn_list:
        return jsonify({'error': 'No valid FSNs found.'}), 400

    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    for fsn in fsn_list:
        if len(fsn) != 16:
            results.append({'fsn': fsn, 'error': 'Invalid length (must be 16)'})
            continue

        url = f"https://www.flipkart.com/product/p/itm?pid={fsn}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                 results.append({'fsn': fsn, 'error': 'Product not found'})
                 continue
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.select_one('.Nx9bqj.CxhGGd')
            
            if price_element:
                price = price_element.text.strip()
                results.append({'fsn': fsn, 'price': price})
            else:
                results.append({'fsn': fsn, 'error': 'Price not found'})

        except requests.RequestException as e:
            results.append({'fsn': fsn, 'error': 'Network error'})

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
