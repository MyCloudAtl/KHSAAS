import rdflib
import pandas as pd


def fetch_dependency_counts(sparql_client, software_name):
    query_dependencies = f"""
    PREFIX sc: <https://w3id.org/secure-chain/>
    PREFIX schema: <http://schema.org/>

    SELECT ?versionName (COUNT(DISTINCT ?dependency) AS ?dependencyCount)
    WHERE {{
        ?software a sc:Software .
        ?software schema:name "{software_name}" .
        ?software sc:hasSoftwareVersion ?version .
        ?version sc:versionName ?versionName .
        OPTIONAL {{ ?version sc:dependsOn ?dependency . }}
    }}
    GROUP BY ?versionName
    ORDER BY ?versionName
    """
    results = run_query(graph, query_dependencies)
    data = []
    if results and 'results' in results and 'bindings' in results['results']:
        for binding in results['results']['bindings']:
            version_name = binding['versionName']['value']
            dependency_count = int(binding['dependencyCount']['value'])
            data.append({'VersionName': version_name, 'DependencyCount': dependency_count})
    df_dependencies = pd.DataFrame(data)
    return df_dependencies

def fetch_vulnerability_counts(sparql_client, software_name):
    query_vulnerabilities = f"""
    PREFIX sc: <https://w3id.org/secure-chain/>
    PREFIX schema: <http://schema.org/>

    SELECT ?versionName (COUNT(DISTINCT ?vulnerability) AS ?vulnerabilityCount)
    WHERE {{
        ?software a sc:Software .
        ?software schema:name "{software_name}" .
        ?software sc:hasSoftwareVersion ?version .
        ?version sc:versionName ?versionName .
        OPTIONAL {{ ?version sc:vulnerableTo ?vulnerability . }}
    }}
    GROUP BY ?versionName
    ORDER BY ?versionName
    """
    results = run_query(graph, query_vulnerabilities)
    data = []
    if results and 'results' in results and 'bindings' in results['results']:
        for binding in results['results']['bindings']:
            version_name = binding['versionName']['value']
            vulnerability_count = int(binding['vulnerabilityCount']['value'])
            data.append({'VersionName': version_name, 'VulnerabilityCount': vulnerability_count})
    df_vulnerabilities = pd.DataFrame(data)
    return df_vulnerabilities

def build_dataframe(dependency_counts, vulnerability_counts, software_name):
    df_dependencies = fetch_dependency_counts(software_name)
    df_vulnerabilities = fetch_vulnerability_counts(software_name)

    # Merge DataFrames on VersionName
    df = pd.merge(df_dependencies, df_vulnerabilities, on='VersionName', how='outer')

    # Add ProductName column
    df['ProductName'] = software_name

    # Reorder columns
    df = df[['ProductName', 'VersionName', 'DependencyCount', 'VulnerabilityCount']]

    # Replace NaN counts with 0
    df[['DependencyCount', 'VulnerabilityCount']] = df[['DependencyCount', 'VulnerabilityCount']].fillna(0).astype(int)
    return df
    