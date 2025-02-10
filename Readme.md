# Knowledge Graph Explorer

## What's This All About?

Imagine a smart tool that helps researchers connect the dots between genes and heart diseases. It maps out relationships between medical data, making it easier to uncover new insights and potential treatments.

## How It Works

### The Knowledge Graph Explained

Think of this tool as a big web of connections:

- **Nodes** are key players like genes, diseases, and medications.
- **Edges** are the links between them, showing how they're related.

By following these connections, researchers can discover new insights into heart disease.

### Our Data Sources

We pull information from top medical databases:

1. **GWAS Catalog**
   - **What it is:** A collection of genome-wide association studies (GWAS) that identify genetic variants linked to diseases.
   - **Why we use it:** It helps us understand which genes are associated with heart diseases.

2. **WikiPathways**
   - **What it is:** A database of biological pathways curated by the scientific community.
   - **Why we use it:** It provides insight into how genes interact within biological processes relevant to heart health.

3. **Open Targets Platform**
   - **What it is:** A research platform that connects genetic data with disease associations and drug targets.
   - **Why we use it:** It helps identify potential treatments and therapeutic targets for cardiovascular diseases.

4. **Bgee Database**
   - **What it is:** A curated database of gene expression in various tissues and conditions.
   - **Why we use it:** It helps researchers understand which genes are active in heart tissues and how they contribute to disease progression.

## Fetching Cardiovascular-Related Data

To extract relevant cardiovascular data from these sources, we:
- **Filter GWAS Catalog** for heart disease-related genetic associations.
- **Use WikiPathways** to identify pathways linked to heart function and disease.
- **Query Open Targets** to find genes with known drug interactions for heart disease treatment.
- **Leverage Bgee** to analyze gene expression patterns specific to cardiovascular tissues.

## Technical Approach: Fetching Data with Python

### Fetching Data from GWAS Catalog
```python
import requests
import pandas as pd

def fetch_gwas_cardio_data():
    url = "https://www.ebi.ac.uk/gwas/rest/api/studies"
    params = {"diseaseTrait": "cardiovascular"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data["_embedded"]["studies"])
    return None
```
*Explanation:* This function sends a request to the GWAS API, filtering results for cardiovascular traits. The data is extracted and formatted into a DataFrame.

### Extracting Pathways from WikiPathways
```python
import requests

def fetch_wikipathways_cardio():
    url = "https://webservice.wikipathways.org/findPathwaysByText"
    params = {"query": "cardiovascular", "format": "json"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["pathways"]
    return None
```
*Explanation:* This function queries WikiPathways for cardiovascular-related pathways and extracts the relevant pathway details.

### Querying Open Targets for Cardiovascular Disease Data
```python
import requests

def fetch_open_targets_cardio():
    url = "https://api.platform.opentargets.org/api/v4/graphql"
    query = """
    {
      disease(efoId: "EFO_0000319") {
        associatedTargets {
          rows {
            target {
              id
              approvedSymbol
            }
            score
          }
        }
      }
    }
    """
    response = requests.post(url, json={"query": query})
    if response.status_code == 200:
        return response.json()["data"]["disease"]["associatedTargets"]["rows"]
    return None
```
*Explanation:* This function uses GraphQL to fetch genes associated with cardiovascular disease from Open Targets. **EFO_0000319** corresponds to "cardiovascular disease" in the Experimental Factor Ontology (EFO), ensuring that we retrieve relevant gene-disease associations. If a more specific condition is needed (e.g., coronary artery disease or arrhythmia), a different EFO term can be used.

### Retrieving Gene Expression Data from Bgee
```python
import requests

def fetch_bgee_cardio():
    url = "https://bgee.org/api/geneExpression"
    params = {"organ": "heart"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["expressions"]
    return None
```
*Explanation:* This function queries Bgee for genes expressed in heart tissues, helping researchers understand gene activity in cardiovascular conditions.

## Key Features

1. **Interactive Map**
   - See the full network of connections.
   - Zoom in for more detail.
   - Filter information to focus on what matters most.

2. **Smart Analysis**
   - Identify key genes linked to heart disease.
   - Find new treatment options.
   - Detect patterns that might be missed otherwise.

3. **Easy Search**
   - Look up genes or heart conditions instantly.
   - Follow the paths between them.
   - Save and share your findings.

4. **Graph Analysis**
   - Finds important connections using smart algorithms.
   - Predicts new links that could reveal hidden relationships.
   - Suggests existing drugs that might work for new conditions.

## License

This project is open source and available under the MIT License.
