import argparse
import tldextract
import json
from multiprocessing import Pool, cpu_count

# prints the version message
version = "v0.0.3"

# Initialize single TLDExtract instance at module level for reuse
_extractor = tldextract.TLDExtract(cache_dir=None)

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

def extract_url(url, components, extractor=None):
    if extractor is None:
        extractor = _extractor
    extracted = extractor(url)
    output = {}
    
    if 'subdomain' in components:
        output['subdomain'] = extracted.subdomain
    if 'domain' in components:
        output['domain'] = extracted.domain
    if 'suffix' in components:
        output['suffix'] = extracted.suffix
    
    return output

def get_registered_domain(url, extractor=None):
    if extractor is None:
        extractor = _extractor
    extracted = extractor(url)
    return extracted.registered_domain

def get_fqdn(url, extractor=None):
    if extractor is None:
        extractor = _extractor
    extracted = extractor(url)
    return extracted.fqdn

# Process-local extractor for multiprocessing (initialized once per process)
_process_extractor = None

def _get_process_extractor():
    """Get or initialize process-local extractor for multiprocessing"""
    global _process_extractor
    if _process_extractor is None:
        _process_extractor = tldextract.TLDExtract(cache_dir=None)
    return _process_extractor

def process_url_worker(args_tuple):
    """Worker function for parallel processing"""
    url, mode, components, json_output = args_tuple
    extractor = _get_process_extractor()
    
    if mode == 'registered_domain':
        result = get_registered_domain(url, extractor)
    elif mode == 'fqdn':
        result = get_fqdn(url, extractor)
    elif mode == 'extract':
        result = extract_url(url, components, extractor)
    else:
        return None
    
    return (url, result, json_output, mode, components)

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
    
    # Determine processing mode
    if args.registered_domain:
        mode = 'registered_domain'
        components = None
    elif args.fqdn:
        mode = 'fqdn'
        components = None
    elif args.extract:
        mode = 'extract'
        components = args.extract.split(',')
    
    # Prepare URLs and arguments for parallel processing
    urls = [line.strip() for line in input_lines if line.strip()]
    
    if not urls:
        return
    
    # Prepare arguments for worker function
    worker_args = [(url, mode, components, args.json) for url in urls]
    
    # Process URLs in parallel
    num_processes = cpu_count()
    results = []
    
    if len(urls) == 1:
        # Single URL: use sequential processing (no multiprocessing overhead)
        url, result, json_output, mode, components = process_url_worker(worker_args[0])
        results.append((url, result, json_output, mode, components))
    else:
        # Multiple URLs: use parallel processing
        with Pool(processes=num_processes) as pool:
            results = pool.map(process_url_worker, worker_args)
    
    # Batch output all results
    for url, result, json_output, mode, components in results:
        if json_output:
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
