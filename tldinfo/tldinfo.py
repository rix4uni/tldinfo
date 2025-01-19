import argparse
import tldextract
import json

# prints the version message
version = "v0.0.1"

def PrintVersion():
    print(f"Current tldinfo version {version}")

def PrintBanner():
    banner = rf"""
   __   __     __ _         ____     
  / /_ / /____/ /(_)____   / __/____ 
 / __// // __  // // __ \ / /_ / __ \
/ /_ / // /_/ // // / / // __// /_/ /
\__//_/ \__,_//_//_/ /_//_/   \____/ 
"""
    print(f"{banner}\n\t\tCurrent tldinfo version {version}\n")

def extract_url(url, components):
    extracted = tldextract.extract(url)
    output = {}
    
    if 'subdomain' in components:
        output['subdomain'] = extracted.subdomain
    if 'domain' in components:
        output['domain'] = extracted.domain
    if 'suffix' in components:
        output['suffix'] = extracted.suffix
    
    return output

def get_registered_domain(url):
    extracted = tldextract.extract(url)
    return extracted.registered_domain

def get_fqdn(url):
    extracted = tldextract.extract(url)
    return extracted.fqdn

def main():
    parser = argparse.ArgumentParser(description="Accurately separates a URL’s subdomain, domain, and public suffix, using the Public Suffix List (PSL).")
    parser.add_argument('-e', '--extract', help="Comma-separated list of parts to extract (subdomain, domain, suffix)")
    parser.add_argument('-r', '--registered_domain', action='store_true', help="Get the registered domain")
    parser.add_argument('-f', '--fqdn', action='store_true', help="Get the fqdn")
    parser.add_argument('-j', '--json', action='store_true', help="Output result in JSON format")
    parser.add_argument('-s', '--silent', action='store_true', help='Run without printing the banner')
    parser.add_argument('-v', '--version', action='store_true', help='Show current version of tldinfo')
    args = parser.parse_args()

    if args.version:
        PrintBanner()
        PrintVersion()
        exit(1)

    if not args.silent:
        PrintBanner()

    # Ensure that --extract, --registered_domain and --fqdn are not used together
    if (args.extract and args.registered_domain) or (args.extract and args.fqdn) or (args.registered_domain and args.fqdn):
        print("Error: You cannot use --extract, --registered_domain, and --fqdn together.")
        return

    # Check if the necessary flag is provided
    if not args.extract and not args.registered_domain and not args.fqdn:
        print("Error: You must provide either --extract or --registered_domain or --fqdn flag.")
        return

    import sys
    input_lines = sys.stdin.readlines()
    
    for line in input_lines:
        url = line.strip()

        if args.registered_domain:
            result = get_registered_domain(url)
        elif args.fqdn:
            result = get_fqdn(url)
        elif args.extract:
            components = args.extract.split(',')
            result = extract_url(url, components)

        if args.json:
            if isinstance(result, dict):  # If the result is a dictionary
                print(json.dumps({"input": url, **result}))
            else:  # For string results from --registered_domain or --fqdn
                print(json.dumps({"input": url, "result": result}))
        else:
            if isinstance(result, dict):  # If it's a dictionary (from --extract)
                print(".".join([result.get(component) for component in ['subdomain', 'domain', 'suffix'] if result.get(component)]))
            else:  # For string results
                print(result)

if __name__ == "__main__":
    main()
