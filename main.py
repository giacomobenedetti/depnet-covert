import requests
import hashlib
import random

def get_package_hash(package_name, version):
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
    
    package_data = response.json()
    
    tarball_url = None
    for dist in package_data['urls']:
        if dist['packagetype'] == 'sdist':
            tarball_url = dist['url']
            break
    
    if not tarball_url:
        return None
    
    tarball_response = requests.get(tarball_url)
    
    if tarball_response.status_code != 200:
        return None
    
    sha256_hash = hashlib.sha256(tarball_response.content).hexdigest()
    
    return sha256_hash

def get_random_package_names(num_packages):
    url = "https://pypi.org/simple/"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching package list: {response.status_code}")
    
    packages = [line.split('>')[1].split('<')[0] for line in response.text.split('\n') if line]
    
    return random.sample(packages, num_packages)

def search_pypi_for_matching_packages(required_bytes, x, y):
    matches = []
    
    while len(matches) < 1:
        package_names = get_random_package_names(10)
        
        for package_name in package_names:
            package_info_url = f"https://pypi.org/pypi/{package_name}/json"
            package_info_response = requests.get(package_info_url)
            
            if package_info_response.status_code != 200:
                print(package_info_response.status_code)
                continue
            
            package_info = package_info_response.json()
            
            versions = package_info.get('releases', {})
            
            for version in versions:
                package_hash = get_package_hash(package_name, version)
                print(package_hash)
                
                print(f"Required: {required_bytes[y:y+x]}")
                if package_hash and package_hash.startswith(required_bytes[y:y + x]):
                    matches.append((package_name, version, package_hash))
                    return matches
    
    return matches

def convert_sentence_to_hex(sentence):
    return sentence.encode().hex()

sentence = "Hello!"
sentence_hex = convert_sentence_to_hex(sentence)
x = 1  # Number of bytes in the signature to match
y = 0  # Initial number of bytes to match

while y < len(sentence_hex):
    matches = search_pypi_for_matching_packages(sentence_hex, x, y)
    print(f"Matches for first {y + x} bytes of the sentence hex:")
    for match in matches:
        print(f"Package: {match[0]}, Version: {match[1]}, Hash: {match[2]}")
    with open("requirements_covert.txt", "a") as f:
        f.write(f"{match[0]}=={match[1]} # {match[2]}")
    
    y += x
